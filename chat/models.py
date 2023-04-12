from django.db import models

class Message(models.Model):
    question = models.CharField(max_length=1000)
    response = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.question
