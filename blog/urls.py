#!/usr/bin/env python
# coding=utf-8
from django.conf.urls import url
from blog.views import *

app_name = 'blog'
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', detail, name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', archives, name='archives'),
    url(r'^category/(?P<pk>[0-9]+)/$', category, name='category'),
]
