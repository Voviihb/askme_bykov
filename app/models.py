from django.contrib.auth.models import User
from django.db import models
from random import randint


def prepare_tags():
    t = Tag.objects.most_popular()
    colors = ["bg-primary", "bg-secondary", "bg-success", "bg-danger", "bg-warning text-dark", "bg-info text-dark",
              "bg-light text-dark", "bg-dark"]
    res = [{
        'tag': tag["tag"],
        'color': colors[randint(0, 7)]
    } for tag in t]
    return res


# Create your models here.
class QuestionManager(models.Manager):
    def sort_new(self):
        return self.order_by('-created')

    def sort_hot(self):
        return self.order_by('-like', '-created')

    def toggle_like(self, user, question):
        # Get the specific question instance
        question_instance = self.get(pk=question.pk)

        # Check if the user has already liked the question
        if question_instance.liked_by.filter(pk=user.pk).exists():
            question_instance.liked_by.remove(user)
            question_instance.like -= 1
        else:
            question_instance.liked_by.add(user)
            question_instance.like += 1

        # Save the changes to the question instance
        question_instance.save()


class Question(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    like = models.IntegerField(default=0, editable=False)
    tags = models.ManyToManyField('Tag', related_name='questions')
    answers = models.ManyToManyField('Answer', related_name='questions', blank=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    liked_by = models.ManyToManyField(User, related_name='questions', blank=True)

    objects = QuestionManager()

    def __str__(self):
        return f"{self.title}"


class TagManager(models.Manager):
    def most_popular(self):
        return self.values('tag').annotate(total=models.Sum('questions__like')).order_by('-total')[:9]

    def get_questions(self, t):
        t_id = self.get(tag=t)
        return Question.objects.filter(tags=t_id)


class Tag(models.Model):
    tag = models.CharField(max_length=50)

    objects = TagManager()

    def __str__(self):
        return f"{self.tag}"


class AnswerManager(models.Manager):
    def sort_by_date(self):
        return self.order_by('created')

    def get_answers(self, q_id):
        return self.filter(questions__id=q_id).order_by('created')

    def toggle_like(self, user, answer):
        # Get the specific question instance
        answer_instance = self.get(pk=answer.pk)

        # Check if the user has already liked the question
        if answer_instance.rated_by.filter(pk=user.pk).exists():
            answer_instance.rated_by.remove(user)
            answer_instance.like -= 1
        else:
            answer_instance.rated_by.add(user)
            answer_instance.like += 1

        # Save the changes to the question instance
        answer_instance.save()

    def toggle_correct(self, user, answer, question):
        # Get the specific question instance
        answer_instance = self.get(pk=answer.pk)
        question_instance = Question.objects.get(pk=question.pk)

        # Check if the user has already liked the question
        if user == question_instance.author:
            if answer_instance.correct:
                answer_instance.correct = False
            else:
                answer_instance.correct = True

            # Save the changes to the question instance
            answer_instance.save()


class Answer(models.Model):
    correct = models.BooleanField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    like = models.IntegerField(default=0, editable=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    rated_by = models.ManyToManyField(User, related_name='answers', blank=True)

    objects = AnswerManager()

    def __str__(self):
        return f"{self.content}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar/%Y/%m/%d', default='avatar.png', blank=True, null=True)

    def __str__(self):
        return f"{self.user}"
