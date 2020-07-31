# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.urls import path
from django.conf.urls import url

# Project modules
from car.views import IndexView, SearchModel, SearchFuel, SearchCap, SearchYear

app_name = "car"

urlpatterns = [
    path("", IndexView.as_view()),
    url(r"model?", SearchModel.as_view(), name="model"),
    url(r"fuel?", SearchFuel.as_view(), name="fuel"),
    url(r"capacity?", SearchCap.as_view(), name="capacity"),
    url(r"year?", SearchYear.as_view(), name="year"),
]
