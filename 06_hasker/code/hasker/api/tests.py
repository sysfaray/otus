import datetime
import re
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user.models import User
from question.models import Question, Answer

# Create your tests here.

class ApiIndexTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test', password='test')
        self.question = Question.objects.create(id=0, heading='Question about Python', pub_date=datetime.datetime.now(), votes=2, author=self.user)
        Question.objects.create(heading='Question about Go', pub_date=datetime.datetime.now(), votes=4, author=self.user)
        Question.objects.create(heading='Question about Nginx', pub_date=datetime.datetime.now(), votes=1, author=self.user)
        Question.objects.create(heading='Question about Centos', pub_date=datetime.datetime.now(), votes=5, author=self.user)
        Question.objects.create(heading='Question about SQL', pub_date=datetime.datetime.now(), votes=3, author=self.user)
        Answer.objects.create(content='Answer 1', pub_date=datetime.datetime.now(), question_ref=self.question, author=self.user)
        Answer.objects.create(content='Answer 2', pub_date=datetime.datetime.now(), question_ref=self.question, author=self.user)
        Answer.objects.create(content='Answer 3', pub_date=datetime.datetime.now(), question_ref=self.question, author=self.user)
        self.client = APIClient(enforce_csrf_checks=True)

    def test_index(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/v1/index/')
        print(resp.json())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json()['count'],
            Question.objects.count())

    def test_trending(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/v1/trending/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            resp.json()['count'],
            Question.objects.count())
        votes = [result['votes'] for result in resp.json()['results']]
        self.assertEqual([5, 4, 3, 2, 1], votes)

    def test_search(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/v1/search/?q=python')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()['count'], len(resp.json()["results"]))
        regex = re.compile("python", re.IGNORECASE)
        self.assertRegex(resp.json()["results"][0]['heading'], regex)

    def test_question(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/v1/questions/0/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()['id'], 0)

    def test_answers(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/v1/questions/0/answers/')
        print ("RESP=",resp.json())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()['count'], 3)
        self.assertRegex(resp.json()["results"][0]['content'], 'Answer 1')

