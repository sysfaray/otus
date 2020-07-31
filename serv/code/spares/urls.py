# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.conf.urls import url

# Project modules
from .views import IndexView, SparesView

app_name = "spares"

urlpatterns = [
    url(r"^spares_view?", SparesView.as_view(), name="spares_view"),
    url(r"^spares_search?", IndexView.as_view(), name="spares_search"),
]
