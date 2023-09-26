from django import template
from django.utils.text import Truncator

register = template.Library()

@register.filter(name="my_truncatewords")
def my_truncatewords(value, num):
    # button class="more-text-trunc">Ещё</button>
    return Truncator(value).words(int(num))

@register.filter(name="btn_add")
def btn_add(value):
    return str(value) + '<button class="more-text-trunc">Ещё</button>'