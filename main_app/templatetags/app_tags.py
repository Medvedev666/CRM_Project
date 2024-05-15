from django import template
from django.db.models import Count

from main_app.models import Category

register = template.Library()



@register.inclusion_tag('list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        cats = Category.objects.all()
    else:
        cats = Category.objects.order_by(sort)

    return {"cats": cats, "cat_selected": cat_selected}

@register.filter()
def class_name(value):
    return value.__class__.__name__
