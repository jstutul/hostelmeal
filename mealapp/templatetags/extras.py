from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_nested(dictionary, keys):
    """Get nested dict value: keys is a comma-separated string"""
    keys_list = keys.split(',')
    d = dictionary
    for k in keys_list:
        d = d.get(k)
        if d is None:
            return None
    return d


@register.filter
def sum_attribute(list_of_dicts, attr):
    return sum(d.get(attr, 0) for d in list_of_dicts)