# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.conf.urls import url
from django.contrib.auth import views as auth_views

# Project modules
from .views import SignupView, SignupDoneView, UserSettingsView

app_name = "user"

urlpatterns = [
    url(r"^login/", auth_views.LoginView.as_view()),
    url(r"^settings/", UserSettingsView.as_view()),
    url(r"^signup/$", SignupView.as_view(), name="signup"),
    url(r"^signup/done/$", SignupDoneView.as_view(), name="login"),
    url(r"^logout/$", auth_views.LogoutView.as_view(), name="logout"),
    url(r"^settings/$", UserSettingsView.as_view(), name="settings"),
]
