# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Python modules
import datetime
import cachetools
import operator
from threading import Lock

# Django modules
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Project modules
from brand.models import BrandModel

id_lock = Lock()


class Car(models.Model):
    class Meta:
        unique_together = (
            ("model", "fuel", "capacity", "start_year", "end_year", "etype", "now"),
        )
        ordering = ["model__name"]
        indexes = [
            models.Index(fields=["id", "model"]),
        ]

    model = models.ForeignKey(BrandModel, on_delete=models.PROTECT)
    fuel = models.CharField(
        max_length=16,
        choices=[("Petrol", "Petrol"), ("Diesel", "Diesel")],
        default="Diesel",
    )
    etype = models.CharField(max_length=15, blank=True)
    capacity = models.FloatField(default=0.0)
    start_year = models.IntegerField(
        default=2000,
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(datetime.datetime.today().year),
        ],
    )
    end_year = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(datetime.datetime.today().year),
        ],
        blank=True,
    )
    now = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        if self.end_year == 0 and self.now:
            end_year = "Now"
        else:
            end_year = self.end_year
        return "%s %s %s %s-%s" % (
            self.model.name,
            self.capacity,
            self.fuel,
            self.start_year,
            end_year,
        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Car.objects.filter(id=id).first()
