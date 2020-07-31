# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Project modules
from .models import User

admin.site.register(User, UserAdmin)
