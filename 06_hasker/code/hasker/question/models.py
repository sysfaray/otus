import datetime

from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

# Create your models here.

class Question(models.Model):
    heading = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField('Tag')
    pub_date = models.DateTimeField('date published')
    votes = models.IntegerField(default=0)
    answers = models.IntegerField(default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=0)
    best_answer = models.ForeignKey('Answer', default=None, null=True, on_delete=models.SET_NULL)

    def published(self):
        delta = timezone.now() - self.pub_date
        if delta.days > 0:
            name = "day" if delta.days == 1 else "days"
            return str(delta.days) + " " + name
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            name = "hour" if hours == 1 else "hours"
            return str(hours) + " " + name
        elif delta.seconds > 60:
            mins = delta.seconds // 60
            name = "minute" if mins == 1 else "minutes"
            return str(mins) + " " + name
        elif delta.seconds > 0:
            name = "sec" if delta.seconds == 1 else "seconds"
            return str(delta.seconds) + " " + name

    def author_name(self):
        return self.author.username

    def author_avatar(self):
        return self.author.avatar

    def tag_list(self):
        return ','.join([tag.name for tag in self.tags.all()])

    def recount_votes(self):
        votes = QuestionVote.objects.filter(reference=self).aggregate(models.Sum('value'))
        self.votes = votes['value__sum']
        if self.votes == None:
            self.votes = 0
        self.save()

    def recount_answers(self):
        self.answers = Answer.objects.filter(question_ref=self).count()
        if self.answers == None:
            self.answers = 0
        self.save()

    def active_vote(self, user_id):
        if QuestionVote.objects.filter(reference=self, author=user_id).exists():
            existing_vote = QuestionVote.objects.get(reference=self, author=user_id)
            return existing_vote.value

    @staticmethod
    def add_question(cleaned_data, user):
        with transaction.atomic():
            new_question = Question(heading=cleaned_data['heading'],
                                    content=cleaned_data['content'],
                                    pub_date=datetime.datetime.now(),
                                    author=user)
            new_question.save()
            for tag in cleaned_data['tags_list']:
                tag = tag.strip()
                if Tag.objects.filter(name=tag).exists():
                    new_tag = Tag.objects.get(name=tag)
                else:
                    new_tag = Tag(name=tag)
                    new_tag.save()
                new_question.tags.add(new_tag)
        return new_question.id


class Trend(object):
    @staticmethod
    def get_trends():
        return Question.objects.order_by('-votes')[:10]


class Tag(models.Model):
    name = models.CharField(max_length=60)


class Answer(models.Model):
    content = models.TextField()
    question_ref = models.ForeignKey(Question, on_delete=models.CASCADE, null=False, blank=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=0)
    pub_date = models.DateTimeField('date published')
    votes = models.IntegerField(default=0)
    active_user_vote = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_question()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._update_question()

    def recount_votes(self):
        votes = AnswerVote.objects.filter(reference=self).aggregate(models.Sum('value'))
        self.votes = votes['value__sum']
        if self.votes == None:
            self.votes = 0
        self.save()

    def author_name(self):
        return self.author.username

    def author_avatar(self):
        return self.author.avatar

    @staticmethod
    def get_answers(question, user_id):
        answers = list(Answer.objects.filter(question_ref=question).order_by('-votes','-pub_date'))
        for answer in answers:
            existing_vote = 0
            if AnswerVote.objects.filter(reference=answer, author=user_id).exists():
                existing_vote = AnswerVote.objects.get(reference=answer, author=user_id).value
            answer.active_user_vote = existing_vote
        return answers

    def _update_question(self):
        self.question_ref.recount_answers()

    @staticmethod
    def add(quest_id, cleaned_data, user):
        quest = Question.objects.get(id=quest_id)
        new_answer = Answer(content=cleaned_data['answer'],
                            question_ref=quest,
                            pub_date=datetime.datetime.now(),
                            author=user)
        new_answer.save()
        return quest.author.email

    def set_best_answer(self):
        with transaction.atomic():
            if self.question_ref.best_answer == self:
                self.question_ref.best_answer = None
                self.question_ref.save()
                result = 'delete'
            else:
                self.question_ref.best_answer = self
                self.question_ref.save()
                result = 'update'
        return result


class VoteManager(object):

    def check(self, vote, ref_obj, value, user):
        if not vote == None and not ref_obj == None and value in ('up', 'down'):
            if value == 'up':
                val = 1
            else:
                val = -1

            if vote.objects.filter(reference=ref_obj, author=user).exists():
                return self.set_existing_vote(vote, ref_obj, val, user)
            else:
                return self.add_new_vote(vote, ref_obj, val, user)

    def add_new_vote(self, vote, ref_obj, val, user):
        with transaction.atomic():
            new_vote = vote(reference=ref_obj,
                            author=user,
                            value=val)
            new_vote.save()
        result = 'add'
        return new_vote.reference.votes, result

    def set_existing_vote(self, vote, ref_obj, val, user):
        existing_vote = vote.objects.get(reference=ref_obj, author=user)
        with transaction.atomic():
            if existing_vote.value == val:
                existing_vote.delete()
                result = 'delete'
            else:
                existing_vote.value = val
                existing_vote.save()
                result = 'update'
        return existing_vote.reference.votes, result


class AnswerVote(models.Model):
    reference = models.ForeignKey(Answer, on_delete=models.CASCADE, default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=0)
    value = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_ans_votes()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._update_ans_votes()

    def _update_ans_votes(self):
        self.reference.recount_votes()


class QuestionVote(models.Model):
    reference = models.ForeignKey(Question, on_delete=models.CASCADE, default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=0)
    value = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_quest_votes()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._update_quest_votes()

    def _update_quest_votes(self):
        self.reference.recount_votes()
