from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import validate_comma_separated_integer_list
from .helpers import checkboxParse
# pylint: disable=maybe-no-member
# Field lengths #

LIST_OF_INTEGERS_LENGTH = 1024    # A maximum of ~500 questionnaires per course, seems good

class Course(models.Model):

    name = models.CharField(max_length=64, default='New course')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    img = models.FileField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def rating(self):
        return len(self.liked_by.all())

    def new_questionnaire(self):
        tmp = Questionnaire.objects.create(course=self, number=len(self)+1)
        Question.objects.create(questionnaire=tmp, number=1)

    def delete_questionnaire(self, number):
        self.questionnaires.get(number=number).delete()
        self.update_positions()

    def update_positions(self, L=''):
        L = L or self
        for i, object in enumerate(L):
            if object.number != i+1:
                object.number = i+1
                object.save(update_fields=['number'])

    def __len__(self):
        return len(self.questionnaires.all())
    
    def __getitem__(self, i):
        return self.questionnaires.all()[i]

    def get_subfeature_questionnaires(self):
        return self.questionnaires.all()

class Questionnaire(models.Model):  # 'child' of Course

    course = models.ForeignKey(Course,
        related_name='questionnaires', on_delete=models.CASCADE)

    name = models.CharField(max_length=64, default='New questionnaire')

    # So they can be ordered, e.g. Course 1 can have Beginner, Intermediate, Advanced in order
    number = models.SmallIntegerField(blank=True, default=0)

    questions_per_test = models.SmallIntegerField(blank=True, default=0)
    ordered = models.BooleanField(blank=True, default=False)
    auto_randomize_ints = models.BooleanField(blank=True, default=True)
    # Imports the answers from ALL the previous questionnaires in this course
    include_answers_from_previous = models.BooleanField(blank=True, default=True)
    # For multiple choice questions
    choices_per_question = models.SmallIntegerField(blank=True, default=3)

    # Probability that the question will be of that type (in %)
    type_choice = models.SmallIntegerField(blank=True, default=85)
    type_write = models.SmallIntegerField(blank=True, default=15)

    def edit_values(self, data):
        ''' 'data' is a POST request with all the variables you can change in Questionnaire '''
        self.name = data.get('name') or self.name
        self.ordered = checkboxParse(data.get('ordered'))
        self.auto_randomize_ints = checkboxParse(data.get('auto_randomize_ints'))
        self.include_answers_from_previous = checkboxParse(data.get('include_answers_from_previous'))
        self.choices_per_question = int(data.get('choices_per_question'))
        self.questions_per_test = int(data.get('questions_per_test'))
        
        if data.get('typing_questions'):
            self.type_write = int(data.get(('probability')))
            self.type_choice = 100-int(data.get(('probability')))
        else:
            self.type_write = 0
            self.type_choice = 100

    def new_question(self):
        Question.objects.create(questionnaire=self, number=len(self)+1)

    def delete_question(self, number):
        self.questions.get(number=number).delete()
        self.update_positions()

    def update_positions(self, L=''):
        # Updates a list or itself
        L = L or self
        for i, object in enumerate(L):
            if object.number != i+1:
                object.number = i+1
                object.save(update_fields=['number'])

    def move_up(self):
        L = list(self.course.questionnaires.order_by('number'))
        if self.number == 1:
            L.append(L.pop(self.number-1))
        else:
            L[self.number-1], L[self.number-2] = L[self.number-2], L[self.number-1]
        self.course.update_positions(L)

    def move_down(self):
        L = list(self.course.questionnaires.order_by('number'))
        if self.number == len(L):
            L.insert(0, L.pop(self.number-1))
        else:
            L[self.number-1], L[self.number] = L[self.number], L[self.number-1]
        self.course.update_positions(L)

    def __len__(self):
        return len(self.questions.all())
    
    def __getitem__(self, i):
        return self.questions.all()[i]

    class Meta:
        ordering = ['number']


class Question(models.Model):

    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', on_delete=models.CASCADE)

    # So they can be ordered? Lets not use this for now
    number = models.SmallIntegerField(blank=True, default=0)
    # If you want to change the default, you also have to go to editquestion.html and change it there (autofocuses if text = New question)
    question = models.CharField(max_length=256, blank=True, default='New question')
    # Can contain several answers, separated by commas!!!
    answer = models.CharField(max_length=64, blank=True, default='Answer')
    # CSV strings
    # If you introduce choices manually, they have to be at least choices_per_question-1.
    # It will choose the manual ones and skip the automation
    choices = models.CharField(max_length=1024, blank=True, default='')

    class Meta:
        ordering = ['number']

    def move_up(self):
        L = list(self.questionnaire.questions.all())
        if self.number == 1:
            L.append(L.pop(self.number-1))
        else:
            L[self.number-1], L[self.number-2] = L[self.number-2], L[self.number-1]
        self.questionnaire.update_positions(L)

    def move_down(self):
        L = list(self.questionnaire.questions.all())
        if self.number == len(L):
            L.insert(0, L.pop(self.number-1))
        else:
            L[self.number-1], L[self.number] = L[self.number], L[self.number-1]
        self.questionnaire.update_positions(L)