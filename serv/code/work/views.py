# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (C) 2020 Maksim Mikhnenko
# ----------------------------------------------------------------------

# Python modules
from collections import OrderedDict

# Django modules
from django.views.generic import TemplateView
from django.http.response import JsonResponse

# Project modules
from car.models import Car
from .models import Work


class IndexView(TemplateView):
    def get(self, request):
        def sortdict(dct):
            res = OrderedDict()
            for x in sorted(dct):
                for k, v in dct.items():
                    if k == x:
                        res[k] = v
            return res

        result = {}
        car = request.GET.get("car")
        car = Car.get_by_id(car)
        for wrk in Work.objects.filter(active=True, cars=car):
            if result.get(wrk.type_work.name):
                result[wrk.type_work.name].append({"id": wrk.id, "name": wrk.name})
            else:
                result[wrk.type_work.name] = [{"id": wrk.id, "name": wrk.name}]
        return JsonResponse({"success": True, "result": sortdict(result)})
