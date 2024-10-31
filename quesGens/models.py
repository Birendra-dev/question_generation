from django.db import models


class Question(models.Model):
    text = models.TextField()
    answer = models.CharField(max_length=255)
    distractors = models.JSONField()  # Storing distractors as a list of strings
