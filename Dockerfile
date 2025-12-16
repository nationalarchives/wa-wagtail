# syntax=docker/dockerfile:1.10
# check=error=true

# NB: The above comments are special directives to Docker that enable us to use
# more up-to-date Dockerfile syntax and will cause the build to fail if any
# Docker build checks fail:
#  https://docs.docker.com/reference/build-checks/
#
# We've set it so that failing checks will cause `docker build .` to fail, but
# when that happens the error message isn't very helpful. To get more
# information, run `docker build --check .` instead.

# Build stage hierarchy:
#
#         ┌────────┐   ┌──────────────┐
#         │  base  │   │  frontend-*  │
#         └────────┘   └──────────────┘
#          /      \     /
#   ┌───────┐    ┌───────┐
#   │  dev  │    │  web  │
#   └───────┘    └───────┘
#                 /     \
#       ┌───────────┐  ┌──────┐
#       │  release  │  │  ci  │
#       └───────────┘  └──────┘

##############
# base stage #
##############

# This stage is the base for the web and dev stages. It contains the version of
# Python we want to use and any OS-level dependencies that we need in all
# environments. It also sets up the always-activated virtual environment and
# installs Poetry.

FROM python:3.13-slim-bookworm AS base

WORKDIR /app

# Install common OS-level dependencies
RUN --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    <<EOF
    apt-get --quiet --yes update
    apt-get --quiet --yes install --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        git
    apt-get --quiet --yes autoremove
EOF

# Create an unprivileged user and virtual environment for the app
ARG UID=1000
ARG GID=1000
ARG USERNAME=ukgwa
ARG VIRTUAL_ENV=/venv
RUN <<EOF
    # Create the unprivileged user and group. If you have issues with file
    # ownership, you may need to adjust the UID and GID build args to match your
    # local user.
    groupadd --gid $GID $USERNAME
    useradd --gid $GID --uid $UID --create-home $USERNAME
    python -m venv --upgrade-deps $VIRTUAL_ENV
    chown -R $UID:$GID /app $VIRTUAL_ENV
EOF

# Install Poetry in its own virtual environment
ARG POETRY_VERSION=1.8.5
ARG POETRY_HOME=/opt/poetry
RUN --mount=type=cache,target=/root/.cache/pip <<EOF
    python -m venv --upgrade-deps $POETRY_HOME
    $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION
EOF

# Set common environment variables
ENV \
    # Don't buffer Python output so that we don't lose logs in the event of a crash
    PYTHONUNBUFFERED=1 \
    # Let things know that a virtual environment is being used
    VIRTUAL_ENV=$VIRTUAL_ENV \
    # Make sure the virtual environment's bin directory and Poetry are on the PATH
    PATH=$VIRTUAL_ENV/bin:$POETRY_HOME/bin:$PATH

# Install .bashrc for dj shortcuts
COPY --chown=$UID:$GID ./docker/bashrc.sh ./docker/bashrc.sh
RUN ln -sTf /app/docker/bashrc.sh /home/$USERNAME/.bashrc

# Switch to the unprivileged user
USER $USERNAME

# Install the app's production dependencies and the root package so that `import
# ukgwa` works regardles of the current directory. We only use
# the absolute bare minimum files to allow this to work here. That prevents us
# needing to reinstall all the dependencies every time the app code changes.
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/home/$USERNAME/.cache/,uid=$UID,gid=$GID \
    <<EOF
    # Create a dummy package so that we can install the root package before we
    # copy in the application code
    mkdir ukgwa
    touch ukgwa/__init__.py
    # Install the root package and the production dependencies
    poetry install --without dev
EOF


###################
# frontend stages #
###################

FROM node:22-slim AS frontend-deps

# This stage is used to install the front-end build dependencies. It's separate
# from the frontend-build stage so that we can initialise the node_modules
# volume in the dev container from here without needing to run the production
# build.

WORKDIR /build/

# Make any build & post-install scripts that respect this variable behave as if
# we were in a CI environment (e.g. for logging verbosity purposes)
ENV CI=true

# Install front-end dependencies
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=optional --no-audit --progress=false \
    && npm install @parcel/css --no-save # Install parcel as a dependency to fix this issue https://github.com/tailwindlabs/tailwindcss/issues/15806

FROM frontend-deps AS frontend-build

# This stage is used to compile the front-end assets. The web stage copies the
# compiled assets bundles from here, so it doesn't need to have the front-end
# build dependencies installed.

# Compile static files - only copy tailwind.config.js if it exists
COPY .eslintignore .eslintrc.js .stylelintrc.js tsconfig.json webpack.config.js ./
COPY ./ukgwa/ ./ukgwa/
# Create placeholder tailwind.config.js if it doesn't exist
RUN [ -f tailwind.config.js ] || echo "module.exports = {};" > tailwind.config.js
RUN npm run build:prod


#############
# web stage #
#############

# This is the stage that actually gets run in staging and production on Heroku.
# It extends the base stage by installing production Python dependencies and
# copying in the compiled front-end assets. It runs the WSGI server, gunicorn,
# in its CMD.

FROM base AS web

# Set production environment variables
ENV \
    # Django settings module
    DJANGO_SETTINGS_MODULE=ukgwa.settings.production \
    # Default port and number of workers for gunicorn to spawn
    PORT=8000 \
    WEB_CONCURRENCY=2

# Copy in built static files and the application code. Run collectstatic so
# whitenoise can serve static files for us.
COPY . .
ARG UID
ARG GID
COPY --chown=$UID:$GID --from=frontend-build --link /build/ukgwa/static_compiled ./ukgwa/static_compiled
RUN <<EOF
    django-admin collectstatic --noinput --clear
EOF

# Run Gunicorn using the config in gunicorn.conf.py (the default location for
# the config file). To change gunicorn settings without needing to make code
# changes and rebuild this image, set the GUNICORN_CMD_ARGS environment variable.
CMD ["gunicorn"]


#################
# release stage #
#################

# This stage is run in the relase phase by Heroku. It's the same as the web
# stage, it just overrides CMD to run deployment checks and migrations.

FROM web AS release

SHELL ["/bin/bash", "-c"]
CMD django-admin check --deploy && django-admin createcachetable && django-admin migrate --noinput


#############
# dev stage #
#############

# This stage is used in the development environment, either via `fab sh` etc. or
# as the dev container in VS Code or PyCharm. It extends the base stage by
# adding additional OS-level dependencies to allow things like using git and
# psql. It also adds sudo and gives the unprivileged user passwordless sudo
# access to make things like experimenting with different OS dependencies easier
# without needing to rebuild the image or connect to the container as root.
#
# This stage does not include the application code at build time! Including the
# code would result in this image needing to be rebuilt every time the code
# changes at all which is unnecessary because we always bind mount the code at
# /app/ anyway.

FROM base AS dev

# Switch to the root user and Install extra OS-level dependencies for
# development, including Node.js and the correct version of the Postgres client
# library (Debian's bundled version is normally too old)
USER root
ARG POSTGRES_VERSION=17
RUN --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    <<EOF
    apt-get --quiet --yes update
    apt-get --quiet --yes install \
        git \
        gnupg \
        less \
        openssh-client \
        postgresql-common \
        sudo
    # Install the Postgres repo
    /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y
    # Intall the Postgres client (make sure the version matches the one in production)
    apt-get --quiet --yes install \
        postgresql-client-${POSTGRES_VERSION}
    # Download and import the Nodesource GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    # Create NodeSource repository
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list
    # Update lists again and install Node.js
    apt-get --quiet --yes update
    apt-get --quiet --yes install nodejs
    # Tidy up
    apt-get --quiet --yes autoremove
EOF

# Give the unprivileged user passwordless sudo access
ARG USERNAME
RUN echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Make less the default pager for things like psql results and git logs
ENV PAGER=less

# Flag that this is the dev container
ENV DEVCONTAINER=1

# Switch back to the unprivileged user
USER $USERNAME

# Copy in the node_modules directory from the frontend-deps stage to initialise
# the volume that gets mounted here
ARG UID
ARG GID
COPY --chown=$UID:$GID --from=frontend-deps --link /build/node_modules ./node_modules

# Install the dev dependencies (they're omitted in the base stage)
RUN --mount=type=cache,target=/home/$USERNAME/.cache/,uid=$UID,gid=$GID \
    poetry install

# Just do nothing forever - exec commands elsewhere
CMD ["tail", "-f", "/dev/null"]


############
# ci stage #
############

FROM dev AS ci

# This stage is used in the CI pipeline to run tests, linters, etc.
# It extends the dev stage by adding in the collected static files from the web
# stage so that we can use Whitenoise's manifest storage backend in tests
# without needing to run collectstatic.

ARG UID
ARG GID
COPY --chown=$UID:$GID --from=web --link /app/static/ /app/static/
