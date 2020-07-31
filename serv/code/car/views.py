# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging

# Django modules
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http.response import JsonResponse

# Project modules
from car.models import Car
from brand.models import BrandModel

logger = logging.getLogger("django.request")


class IndexView(TemplateView):
    def get(self, request):
        result = sorted(
            BrandModel.objects.filter(active=True)
            .exclude(brand__active=False)
            .values_list("brand__name", flat=True)
            .distinct()
        )
        return render(request, "car/index.html", {"result": result})


class SearchModel(TemplateView):
    def get(self, request):
        brand = request.GET.get("brand")
        result = sorted(
            list(
                Car.objects.filter(active=True, model__brand__name=brand)
                .exclude(model__active=False)
                .values_list("model__name", flat=True)
                .distinct()
            )
        )
        return render(request, "car/list.html", {"result": result})


class SearchFuel(TemplateView):
    def get(self, request):
        model = request.GET.get("model")
        res = list(
            Car.objects.filter(model__name=model).values("fuel", "etype").distinct()
        )
        result = ";".join(
            "%s, %s" % (r["fuel"], r["etype"]) if r["etype"] else r["fuel"] for r in res
        )
        return render(request, "car/list.html", {"result": result.split(";")})


class SearchCap(TemplateView):
    def get(self, request):
        etype = ""
        model = request.GET.get("model")
        f = request.GET.get("fuel")
        if "," in f:
            fuel = f.split(",")[0].strip()
            etype = f.split(",")[1].strip()
        else:
            fuel = f
        result = list(
            Car.objects.filter(model__name=model, fuel=fuel, etype=etype)
            .values_list("capacity", flat=True)
            .distinct()
        )

        return render(request, "car/list.html", {"result": result})


class SearchYear(TemplateView):
    def get(self, request):
        result = {}
        etype = ""
        model = request.GET.get("model")
        f = request.GET.get("fuel")
        if "," in f:
            fuel = f.split(",")[0].strip()
            etype = f.split(",")[1].strip()
        else:
            fuel = f
        capacity = request.GET.get("capacity")
        try:
            cc = Car.objects.get(
                model__name=model, fuel=fuel, etype=etype, capacity=capacity
            )

            start = cc.start_year
            end = cc.end_year
            if cc.now:
                end = datetime.datetime.today().year
            result["car"] = cc.id
            result["date"] = sorted([r for r in range(start, end + 1)])
            return JsonResponse({"success": True, "result": result})
        except Exception as e:
            logger.error("Errot: %s", e)
            return JsonResponse({"success": False, "result": result})
