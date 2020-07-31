# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True, unique=True)
    clock_rate = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BrandModel(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "%s %s" % (self.brand, self.name)
