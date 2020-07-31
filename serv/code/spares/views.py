# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Django modules
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http.response import JsonResponse

# Project modules
from car.models import Car
from work.models import Work, SparesAnalogCount, SparesOriginalCount
from .models import Spares, SparesAnalog


class SparesView(TemplateView):
    def get(self, request):
        result = []
        car = request.GET.get("car")
        car = Car.get_by_id(car)
        odata = Spares.objects.filter(model=car)
        nodata = SparesAnalog.objects.filter(model=car)
        for d in odata:
            result.append(
                {
                    "name": d.name.name,
                    "part_number": d.part_number,
                    "cost": d.cost,
                    "count": d.count,
                    "type": "Оригинал",
                }
            )
        for nd in nodata:
            result.append(
                {
                    "name": nd.name.name,
                    "part_number": nd.part_number,
                    "cost": nd.cost,
                    "count": nd.count,
                    "type": "Аналог",
                }
            )
        return render(request, "spares/index.html", {"result": result})


class IndexView(TemplateView):

    CHECK = {"true": True, "false": False}

    def get(self, request):
        result = {}
        result["spares"] = []
        result["original"] = True
        car = request.GET.get("car")
        id = request.GET.get("id")
        if id:
            cr = Car.get_by_id(car)
            original_cost = 0
            analog_cost = 0
            wrk = Work.get_by_id(id=id)
            for sc in SparesOriginalCount.objects.filter(work__id=id).order_by("name"):
                original_cost = original_cost + (sc.name.cost * sc.count)
                if not self.CHECK.get(request.GET.get("original")):
                    continue
                result["spares"].append(
                    {
                        "id": sc.name.id,
                        "name": sc.name.name.name,
                        "part_number": sc.name.part_number,
                        "cost": sc.name.cost,
                        "count": sc.count,
                        "type": "Оригинал",
                    }
                )
            for notsc in SparesAnalogCount.objects.filter(work__id=id).order_by("name"):
                analog_cost = analog_cost + (notsc.name.cost * notsc.count)
                if self.CHECK.get(request.GET.get("original")):
                    continue
                result["spares"].append(
                    {
                        "id": notsc.name.id,
                        "name": notsc.name.name.name,
                        "part_number": notsc.name.part_number,
                        "cost": notsc.name.cost,
                        "count": notsc.count,
                        "type": "Аналог",
                    }
                )
            cost = original_cost
            if not self.CHECK.get(request.GET.get("original")):
                cost = analog_cost
                result["original"] = False
            result["spares_cost"] = cost
            result["work_cost"] = cr.model.brand.clock_rate * wrk.work_ratio
            result["difference"] = original_cost - analog_cost
            result["summary"] = cr.model.brand.clock_rate * wrk.work_ratio + cost
            return render(request, "work/index.html", {"result": result})
        return JsonResponse({"success": False, "result": result})
