import datetime
import json
import os
import subprocess
import sys
from shlex import quote

from invoke import run as local
from invoke.context import Context
from invoke.tasks import task

PROJECT_DIR = "/app"
LOCAL_DUMP_DIR = "database_dumps"

PRODUCTION_APP_INSTANCE = "ukgwa-production"
STAGING_APP_INSTANCE = "ukgwa-staging"

LOCAL_MEDIA_DIR = "media"
LOCAL_IMAGES_DIR = LOCAL_MEDIA_DIR + "/original_images"
LOCAL_DATABASE_NAME = "ukgwa"


############
# Production
############


def dexec(cmd, service="web"):
    return local(
        "docker compose exec -T {} bash -c {}".format(quote(service), quote(cmd))
    )


@task
def build(c: Context):
    """
    Build the development environment (call this first)
    """
    # Check if the web container is running, ask user if they want to stop it
    web_status_json = subprocess.check_output(
        ["docker", "compose", "ps", "--all", "--format=json", "web"],
        encoding="utf-8",
    )
    if json.loads(web_status_json or "{}").get("State") == "running":
        response = input(
            "The web container is currently running. Do you want to stop it and continue? (y/N): "
        )
        if response.lower() in ["y", "yes"]:
            print("Stopping containers...")
            local("docker compose stop")
        else:
            print("Build cancelled. Stop the containers with `fab stop` and try again.")
            sys.exit(1)

    # Remove the web container, if it exists. If we don't do this, we won't be
    # able to drop the node_modules volume below, so just exit with an error.
    subprocess.check_call(["docker", "compose", "rm", "--force", "web"])

    # If the node_modules named volume exists, try to remove it so that it
    # gets reinitialised with the node_modules/ from the image. This guarantees
    # that the Node dependencies are up to date after running this task.
    web_service_config_json = subprocess.check_output(
        ["docker", "compose", "config", "--format=json", "web"],
        encoding="utf-8",
    )
    web_service_config = json.loads(web_service_config_json)
    node_modules_volume_name = web_service_config["volumes"]["node_modules"]["name"]
    subprocess.run(["docker", "volume", "rm", "--force", node_modules_volume_name])

    # Pull up-to-date images and build the development environment
    local("docker compose pull")
    local(
        f"docker compose build --build-arg UID={os.getuid()} --build-arg GID={os.getgid()}"
    )


@task
def start(c):
    """
    Start the development environment
    """
    local("docker compose up --detach")


@task
def stop(c):
    """
    Stop the development environment
    """
    local("docker compose stop")


@task
def restart(c):
    """
    Restart the development environment
    """
    stop(c)
    start(c)


@task
def destroy(c):
    """
    Destroy development environment containers and volumes (database will be lost!)
    """
    local("docker compose down --volumes")


@task
def sh(c, service="web"):
    """
    Run bash in a local container
    """
    subprocess.run(["docker", "compose", "exec", service, "bash"])


@task
def delete_docker_database(c):
    dexec("psql -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'")


@task(
    help={
        "new_default_site_hostname": "Pass an empty string to skip the default site's hostname replacement"
        " - default is 'localhost:8000'"
    }
)
def import_data(
    c, database_filename: str, new_default_site_hostname: str = "localhost:8000"
):
    """
    Import local data file to the db container.
    """
    delete_docker_database(c)
    dexec(
        f"pg_restore --clean --if-exists --no-owner --no-acl --dbname={LOCAL_DATABASE_NAME} {database_filename}",
    )

    # When pulling data from a heroku environment, the hostname in wagtail > sites is not updated.
    # This means when browsing the site locally with this pulled data you can end up with links to staging, or even
    # the live site.
    # --> let's update the default site hostname values
    if new_default_site_hostname:
        if ":" in new_default_site_hostname:
            hostname, port = new_default_site_hostname.split(":")
        else:
            hostname, port = new_default_site_hostname, "8000"
        assert hostname and port and port.isdigit()
        dexec(
            f"psql -c \"UPDATE wagtailcore_site SET hostname = '{hostname}', port = {port} WHERE is_default_site IS TRUE;\""  # noqa: E501
        )
        print(f"Default site's hostname was updated to '{hostname}:{port}'.")

    print(
        "Any superuser accounts you previously created locally will have been wiped and will need to be recreated."
    )


#########
# Production
#########


@task
def pull_production_media(c):
    """Pull media from production AWS S3"""
    pull_media_from_s3_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_images(c):
    """Pull images from production AWS S3"""
    pull_images_from_s3_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_data(c):
    """Pull database from production Heroku Postgres"""
    pull_database_from_heroku(c, PRODUCTION_APP_INSTANCE, anonymise=True)


@task
def production_shell(c):
    """Spin up a one-time Heroku production dyno and connect to shell"""
    open_heroku_shell(c, PRODUCTION_APP_INSTANCE)


#########
# Staging
#########


@task
def pull_staging_media(c):
    """Pull media from staging AWS S3"""
    pull_media_from_s3_heroku(c, STAGING_APP_INSTANCE)


@task
def pull_staging_images(c):
    """Pull images from staging AWS S3"""
    pull_images_from_s3_heroku(c, STAGING_APP_INSTANCE)


@task
def pull_staging_data(c):
    """Pull database from staging Heroku Postgres"""
    pull_database_from_heroku(c, STAGING_APP_INSTANCE)


@task
def staging_shell(c):
    """Spin up a one-time Heroku staging dyno and connect to shell"""
    open_heroku_shell(c, STAGING_APP_INSTANCE)


####
# S3
####


def aws(c, command, aws_access_key_id, aws_secret_access_key):
    return local(
        "aws {command}".format(
            command=command,
        ),
        env={
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
        },
    )


def pull_media_from_s3(
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
    local_media_dir=LOCAL_MEDIA_DIR,
):
    aws_cmd = "s3 sync --delete s3://{bucket_name} {local_media}".format(
        bucket_name=aws_storage_bucket_name,
        local_media=local_media_dir,
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def pull_images_from_s3_heroku(c, app_instance):
    aws_access_key_id = get_heroku_variable(c, app_instance, "AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_heroku_variable(
        c, app_instance, "AWS_SECRET_ACCESS_KEY"
    )
    aws_storage_bucket_name = get_heroku_variable(
        c, app_instance, "AWS_STORAGE_BUCKET_NAME"
    )
    pull_images_from_s3(
        c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name
    )


def pull_images_from_s3(
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
    local_images_dir=LOCAL_IMAGES_DIR,
):
    aws_cmd = (
        "s3 sync --delete s3://{bucket_name}/original_images {local_media}".format(
            bucket_name=aws_storage_bucket_name, local_media=local_images_dir
        )
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)

    # The above command just syncs the original images, so we need to drop the wagtailimages_renditions
    # table so that the renditions will be re-created when requested on the local build.
    dexec("psql -c 'DELETE FROM images_rendition;'")


########
# Heroku
########


def pull_media_from_s3_heroku(c, app_instance):
    aws_access_key_id = get_heroku_variable(c, app_instance, "AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_heroku_variable(
        c, app_instance, "AWS_SECRET_ACCESS_KEY"
    )
    aws_storage_bucket_name = get_heroku_variable(
        c, app_instance, "AWS_STORAGE_BUCKET_NAME"
    )
    pull_media_from_s3(
        c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name
    )


def pull_database_from_heroku(c, app_instance, anonymise=False):
    datestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    local(
        "heroku pg:backups:download --output={dump_folder}/{datestamp}.dump --app {app}".format(
            app=app_instance, dump_folder=LOCAL_DUMP_DIR, datestamp=datestamp
        ),
    )

    import_data(c, f"/app/{LOCAL_DUMP_DIR}/{datestamp}.dump")

    local(
        "rm {dump_folder}/{datestamp}.dump".format(
            dump_folder=LOCAL_DUMP_DIR,
            datestamp=datestamp,
        ),
    )

    if anonymise:
        dexec("./manage.py run_birdbath --skip-checks")


def open_heroku_shell(c, app_instance, shell_command="bash"):
    subprocess.call(
        [
            "heroku",
            "run",
            shell_command,
            "-a",
            app_instance,
        ]
    )


#######
# Utils
#######


def make_bold(msg):
    return "\033[1m{}\033[0m".format(msg)


@task
def docker_coverage(c):
    return dexec(
        "coverage erase && coverage run manage.py test \
            --settings=ukgwa.settings.test && coverage report",
    )


def get_heroku_variable(c, app_instance, variable):
    return local(
        "heroku config:get {var} --app {app}".format(app=app_instance, var=variable),
        hide=True,
    ).stdout.strip()


@task
def run_test(c):
    """
    Run python tests in the web container
    """
    subprocess.call(
        [
            "docker",
            "compose",
            "exec",
            "web",
            "python",
            "manage.py",
            "test",
            "--settings=ukgwa.settings.test",
            "--parallel",
        ]
    )
