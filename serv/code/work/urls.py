# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.conf.urls import url

# Project modules
from .views import IndexView

app_name = "type_work"

urlpatterns = [
    url(r"^type_work_search?", IndexView.as_view(), name="type_work_search"),
]
