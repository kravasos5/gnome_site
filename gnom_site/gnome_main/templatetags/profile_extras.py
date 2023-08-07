from django import template

register = template.Library()

@register.filter(name="sub_pluralize")
def sub_pluralize(value):
    new_value = str(value)
    if value == 0 or value >= 5:
        new_value += ' подписчиков'
    elif value == 1:
        new_value += ' подписчик'
    else:
        new_value += ' подписчика'
    return new_value

@register.filter(name="post_pluralize")
def post_pluralize(value):
    new_value = str(value)
    if value == 0 or value >= 5:
        new_value += ' записей'
    elif value == 1:
        new_value += ' запись'
    else:
        new_value += ' записи'
    return new_value