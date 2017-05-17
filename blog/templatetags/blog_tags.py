#!/usr/bin/env python
# coding=utf-8
from blog.models import *
from django import template
from django.db.models.aggregates import Count

register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all()[:num]

@register.simple_tag
def archives():
    return Post.objects.dates('created_time', 'month', order='DESC')


@register.simple_tag
def get_categories():
    return Category.objects.all()

@register.simple_tag
def get_num_posts():
    category_list = Category.objects.annotate(num_posts=Count('post'))
    return category_list

