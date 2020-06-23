import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.views.generic import View, UpdateView, FormView, CreateView

from user.models import User
from utils.mailsender import MailSender
from user.forms import SignupForm, UserForm
from question.models import Trend

class SignupView(CreateView):

    def get(self, request):
        form = SignupForm()

        return render(request, "index/signup.html", {
            "form": form,
            "trends": Trend.get_trends()
        })

    def post(self, request):
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Creating user and profile
            try:
                with transaction.atomic():
                    new_user = User.objects.create(
                                    username=form.cleaned_data['login'],
                                    password=make_password(form.cleaned_data['password']),
                                    email=form.cleaned_data['email'],
                                    avatar=form.cleaned_data['avatar'],
                                    reg_date=datetime.datetime.now()
                                    )
                    if new_user:
                        MailSender().send(new_user.email, 'sign_up', context={"login": new_user.username})
                return HttpResponseRedirect('/signup/done/')
            except Exception as error:
                message = 'Error while adding new user: ' + str(error) + str(form.cleaned_data)
        else:
            message = 'Error while adding new user, check fields '

        return render(request, "index/signup.html", {
            "form": form,
            "message": message,
            "trends": Trend.get_trends()
        })


class SignupDoneView(FormView):

    def get(self, request):
        return render(request, "index/signup_done.html", {
            "trends": Trend.get_trends()
        })


class UserSettingsView(UpdateView):

    def get(self, request):
        return render(request, "index/settings.html", {
            "trends": Trend.get_trends()
        })

    def post(self, request):
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            with transaction.atomic():
                user_form.save()
            message = 'User settings successfully updated'
        else:
            message = 'Error while updating user'
        return render(request, "index/settings.html", {
            "user_form": user_form,
            "message": message,
            "trends": Trend.get_trends()
        })