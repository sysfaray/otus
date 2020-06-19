from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin
from django.db import transaction
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.mailsender import MailSender
from question.models import Question, Tag, Trend, Answer, AnswerVote, QuestionVote, VoteManager
from .forms import AskForm, AnswerForm



# Create your views here.

class IndexView(View):

    def get(self, request):
        quest_list = Question.objects.order_by('-pub_date')
        paginator = Paginator(quest_list, 20)
        page = request.GET.get('page')
        questions = paginator.get_page(page)

        return render(request, "question/index.html", {
            "questions": questions,
            "page": page,
            "trends": Trend.get_trends()
        })


class AskView(LoginRequiredMixin, View):

    def get(self, request):
        form = AskForm()
        return render(request, "question/ask.html", {
            "trends": Trend.get_trends(),
            "form": form
        })

    def post(self, request):
        form = AskForm(request.POST)
        if form.is_valid():
            new_question_id = Question.add_question(form.cleaned_data, request.user)
            return HttpResponseRedirect('/question/' + str(new_question_id) + '/')
        else:
            message = 'Error while adding'
            return render(request, "question/ask.html", {
                    "form": form,
                    "message": message,
                    "trends": Trend.get_trends()
            })


class QuestionView(MultipleObjectMixin, View):

    def get(self, request, id):
        form = AnswerForm()
        quest = Question.objects.get(id=id)
        quest.active_user_vote = quest.active_vote(request.user.id)
        answers_set = Answer.get_answers(quest, request.user.id)

        page = request.GET.get('page')
        paginator = self.get_paginator(answers_set, 30)
        answers = paginator.get_page(page)

        return render(request, "question/question.html", {
            "trends": Trend.get_trends(),
            "form": form,
            "question": quest,
            "answers": answers,
        })

    def post(self, request, id):
        if request.user.is_authenticated:
            form = AnswerForm(request.POST)
            if form.is_valid():
                quest_author_email = Answer.add(id, form.cleaned_data, request.user)
                url = request.headers["Origin"] + '/question/%s/' % id
                link = '<a href="{}">{}</a>'.format(url, url)
                MailSender.send(quest_author_email, 'new_answer', context={"link": link})
                return HttpResponseRedirect(url)
            else:
                message = 'Error while adding'
                return render(request, "question/question.html", {
                    "form": form,
                    "id": id,
                    "message": message,
                    "trends": Trend.get_trends()
                })


class VoteView(LoginRequiredMixin, View):

    def get(self, request):
        type =  request.GET.get('type')
        obj_id = int(request.GET.get('id'))
        value = request.GET.get('value')

        if type == 'answer':
            vote = AnswerVote
            ref_obj = Answer.objects.get(id=obj_id)
        elif type == 'question':
            vote = QuestionVote
            ref_obj = Question.objects.get(id=obj_id)
        else:
            return

        votes, result = VoteManager().check(vote, ref_obj, value, request.user)
        return render(request, "question/vote.html", {
            "result": result,
            "votes": votes
        })


class BestAnswerView(LoginRequiredMixin, View):

    def get(self, request):
        answer_id = int(request.GET.get('id'))
        answer = Answer.objects.get(id=answer_id)

        result = 'error'
        if answer.question_ref.author == request.user:
            result = answer.set_best_answer()

        return render(request, "question/best.html", {
            "result": result
        })


class SearchView(View):

    def get(self, request):
        query = request.GET.get('q')
        quest_list = Question.objects.filter(Q(heading__icontains=query) | Q(content__icontains=query)).order_by('votes','-pub_date')[:20]
        paginator = Paginator(quest_list, 20)
        page = request.GET.get('page')
        questions = paginator.get_page(page)

        return render(request, "question/search.html", {
            "questions": questions,
            "query": query,
            "trends": Trend.get_trends()
        })


class TagView(View):

    def get(self, request, tag):
        tag = str(tag).strip()
        if Tag.objects.filter(name=tag).exists():
            tag_elem = Tag.objects.get(name=tag)
            quest_list = Question.objects.filter(tags=tag_elem).order_by('votes','-pub_date')[:20]
            paginator = Paginator(quest_list, 20)
            page = request.GET.get('page')

            try:
                questions = paginator.get_page(page)
            except PageNotAnInteger:
                questions = paginator.get_page(1)
            except EmptyPage:
                questions = paginator.get_page(page)

        return render(request, "question/search.html", {
            "questions": questions,
            "query": "tag:{}".format(tag),
            "trends": Trend.get_trends()
        })


class QuestionListView(View):

    def get(self, request):
        page = request.GET.get('page')
        sort = request.GET.get('sort')
        if sort == 'date':
            sort_1 = '-pub_date'
            sort_2 = '-votes'
        else:
            sort_1 = '-votes'
            sort_2 = '-pub_date'
        quest_list = Question.objects.order_by(sort_1, sort_2)
        paginator = Paginator(quest_list, 20)

        try:
            questions = paginator.get_page(page)
        except PageNotAnInteger:
            questions = paginator.get_page(1)
        except EmptyPage:
            questions = paginator.get_page(page)

        return render(request, "question/list.html", {
            "questions": questions,
            "trends": Trend.get_trends()
        })