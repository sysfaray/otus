# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Python modules
import cachetools
import operator
from threading import Lock

# Django modules
from django.db import models

# Project modules
from car.models import Car

id_lock = Lock()


class SparesName(models.Model):
    class Meta:
        verbose_name = "Наименование"
        verbose_name_plural = "Наименование"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "name"]),
        ]

    name = models.CharField(max_length=200, blank=True, unique=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Spares(models.Model):
    class Meta:
        verbose_name = "Запчасти Оригинал"
        verbose_name_plural = "Запчасти Оригинал"
        ordering = ["name__name"]
        indexes = [
            models.Index(fields=["id", "name", "part_number"]),
        ]

    name = models.ForeignKey(SparesName, on_delete=models.PROTECT)
    part_number = models.CharField(max_length=200, unique=True)
    model = models.ManyToManyField(Car, blank=True)
    cost = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s" % (self.name, self.part_number)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name_and_car(cls, name, car):
        return list(Spares.objects.filter(name__name=name, model=car))


class SparesAnalog(models.Model):
    class Meta:
        verbose_name = "Запчасти Аналог"
        verbose_name_plural = "Запчасти Аналог"
        ordering = ["name__name"]
        indexes = [
            models.Index(fields=["id", "name", "part_number"]),
        ]

    name = models.ForeignKey(SparesName, on_delete=models.PROTECT)
    part_number = models.CharField(max_length=200, unique=True)
    model = models.ManyToManyField(Car, blank=True)
    cost = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s" % (self.name, self.part_number)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name_and_car(cls, name, car):
        return list(Spares.objects.filter(name__name=name, model=car))
