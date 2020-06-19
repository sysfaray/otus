from django.conf import settings
from django.db.models import Q
from rest_framework.decorators import api_view, schema, renderer_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework import response, schemas
from django.shortcuts import render

from question.models import Question, Answer
from api.serializers import IndexSerializer, TrendingSerializer, SearchSerializer, QuestionSerializer, AnswerSerializer


class IndexAPIView(generics.ListAPIView):
    '''List of questions with pagination'''
    queryset = Question.objects.all().order_by('-pub_date')
    serializer_class = IndexSerializer

class TrendingAPIView(generics.ListAPIView):
    '''Ten most popular questions'''
    queryset = Question.objects.order_by('-votes')[:10]
    serializer_class = TrendingSerializer

class SearchAPIView(generics.ListAPIView):
    '''Search question.
       Uses GET parameter "q" for searching
    '''
    serializer_class = SearchSerializer

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Question.objects.filter(Q(heading__icontains=query) | Q(content__icontains=query)).order_by('votes','-pub_date')[:20]
        return queryset

class QuestionAPIView(generics.RetrieveAPIView):
    '''Question details'''
    serializer_class = QuestionSerializer
    lookup_field = 'pk'
    queryset = Question.objects.all()

class QuestionAnswersAPIView(generics.ListAPIView):
    '''Question answers list with pagination'''
    serializer_class = AnswerSerializer
    lookup_field = 'pk'

    def get_queryset(self, *args, **kwargs):
        question_id = self.kwargs.get("pk")
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise NotFound()
        answers = Answer.objects.filter(question_ref=question).order_by('votes').all()
        return answers

def schema_view(request):
    return render(request, "api/index.html", {})

@api_view()
@schema(None)
def wrong_url(request):
    return Response({"message": "Wrong URL: check API documentation at http://{}/api/docs/".format(settings.SITE_URL)})
