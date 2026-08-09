"""Small reusable template filters/tags used across the app."""

from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """Return the current querystring with ``kwargs`` applied/overridden.

    Keeps existing GET params (filters) intact when building pagination or
    filter links, e.g. ``?status=pending&page=2``.
    """
    request = context.get("request")
    params = request.GET.copy() if request else {}
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    return urlencode(params, doseq=True)


@register.filter
def get_item(dictionary, key):
    """Look up a dict value by key inside a template."""
    if hasattr(dictionary, "get"):
        return dictionary.get(key)
    return None
