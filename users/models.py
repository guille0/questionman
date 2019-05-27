from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Questionnaire
from django.db.models.signals import post_save
from django.dispatch import receiver
# pylint: disable=maybe-no-member

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses_liked = models.ManyToManyField(Course, related_name='liked_by', blank=True)
    courses_done = models.ManyToManyField(Course, related_name='done_by', blank=True)
    questionnaires_done = models.ManyToManyField(Questionnaire, related_name='done_by', blank=True)

    def has_liked(self, course):
        if course in self.courses_liked.all():
            return True

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
