# myproject/core/pattern_contexts.py

from pattern_library import register_context_modifier


@register_context_modifier(template="components/streamfield/document_block.html")
def get_file_size(context, request):
    if (
        "document" in context["value"]
        and "get_file_size" not in context["value"]["document"]
    ):
        context["value"]["document"]["get_file_size"] = "10485760"  # 10 MB in bytes
