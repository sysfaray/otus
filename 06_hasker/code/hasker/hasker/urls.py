"""hasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from user.views import SignupView, SignupDoneView, UserSettingsView
from question.models import Trend
from question.views import IndexView, AskView, QuestionView, QuestionListView, VoteView, BestAnswerView, SearchView, TagView


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        extra_context={"trends": Trend.get_trends()}
    )),
    path('logout/', auth_views.LogoutView.as_view()),
    path('signup/', SignupView.as_view()),
    path('signup/done/', SignupDoneView.as_view()),
    path('settings/', UserSettingsView.as_view()),
    path('ask/', AskView.as_view()),
    path('question/<int:id>/', QuestionView.as_view(), name="question"),
    path('question/vote/', VoteView.as_view(), name="question_vote"),
    path('question/best/', BestAnswerView.as_view(), name="question_best"),
    path('question/list/', QuestionListView.as_view(), name="question_vote"),
    path('search/', SearchView.as_view(), name="question_search"),
    path('tag/<str:tag>/', TagView.as_view(), name="question_tag"),
    path('admin/', admin.site.urls),
    url(r'^api/', include(('api.urls', 'api'), namespace='api')),
    path('', IndexView.as_view()),
]
