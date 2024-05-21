from django.db import models
from django.contrib.auth.models import User
import json

class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    quiz_data = models.TextField() 
    score = models.IntegerField(default=0)

    def get_quiz_data(self):
        return json.loads(self.quiz_data)


