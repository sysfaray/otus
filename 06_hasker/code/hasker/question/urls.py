from django.urls import path, re_path
from django.conf.urls import url
from question.views import IndexView, AskView, QuestionView, QuestionListView, VoteView, BestAnswerView, SearchView, TagView

app_name = 'question'

urlpatterns = [
    path('ask/', AskView.as_view()),
    path('question/<int:id>/', QuestionView.as_view(), name="question"),
    path('question/vote/', VoteView.as_view(), name="question_vote"),
    path('question/best/', BestAnswerView.as_view(), name="question_best"),
    path('question/list/', QuestionListView.as_view(), name="question_vote"),
    url(r'^search/?$', SearchView.as_view(), name='search'),
    path('tag/<str:tag>/', TagView.as_view(), name="question_tag"),
    path('', IndexView.as_view()),
]
