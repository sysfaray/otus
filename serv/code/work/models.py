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

# Python modules
from car.models import Car
from spares.models import Spares, SparesAnalog

id_lock = Lock()


class TypeWork(models.Model):
    class Meta:
        verbose_name = "Типы работ"
        verbose_name_plural = "Типы работ"
        ordering = ("name",)
        indexes = [
            models.Index(fields=["id", "name"]),
        ]

    name = models.CharField(max_length=200, blank=True, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Work(models.Model):
    class Meta:
        verbose_name = "Виды работ"
        verbose_name_plural = "Виды работ"
        ordering = ("name",)
        indexes = [
            models.Index(fields=["id", "name"]),
        ]

    name = models.CharField(max_length=200, null=True, blank=True)
    work_ratio = models.FloatField(default=1)
    original = models.ManyToManyField(Spares, through="SparesOriginalCount")
    analog = models.ManyToManyField(SparesAnalog, through="SparesAnalogCount")
    type_work = models.ForeignKey(TypeWork, on_delete=models.PROTECT)
    cars = models.ManyToManyField(Car, blank=True)
    active = models.BooleanField(default=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Work.objects.filter(id=id).first()


class SparesOriginalCount(models.Model):
    class Meta:
        verbose_name = "Запчасти Оригинал"
        verbose_name_plural = "Запчасти Оригинал"
        indexes = [
            models.Index(fields=["id", "name", "work"]),
        ]

    name = models.ForeignKey(Spares, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def __str__(self):
        return "%s/ %s/ %s" % (self.work, self.name, self.count)


class SparesAnalogCount(models.Model):
    class Meta:
        verbose_name = "Запчасти Аналог"
        verbose_name_plural = "Запчасти Аналог"
        indexes = [
            models.Index(fields=["id", "name", "work"]),
        ]

    name = models.ForeignKey(SparesAnalog, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def __str__(self):
        return "%s/ %s/ %s" % (self.work, self.name, self.count)
