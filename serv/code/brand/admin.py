# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.contrib import admin

# Project modules
from .models import Brand, BrandModel


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass


@admin.register(BrandModel)
class BrandModelAdmin(admin.ModelAdmin):
    list_display = ("active", "brand", "name")
    list_display_links = ("brand", "name")
    list_filter = ["brand__name"]
    search_fields = ["name"]
