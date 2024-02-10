from django.db import models

# Create your models here.

class Question(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'