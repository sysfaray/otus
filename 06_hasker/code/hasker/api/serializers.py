from django.contrib.auth.models import User, Group
from rest_framework import serializers

from question.models import Question, Answer

class IndexSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'heading', 'votes', 'answers', 'published', 'author_name', 'tag_list')

class TrendingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'heading', 'votes')

class SearchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'heading', 'votes')

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'heading', 'content', 'author_name', 'pub_date', 'votes', 'tag_list')

class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'content', 'author_name', 'pub_date', 'votes')