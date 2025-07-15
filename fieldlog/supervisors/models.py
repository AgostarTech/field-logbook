from django.db import models

# Create your models here.
from users.models import CustomUser

class Task(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_by', limit_choices_to={'role__in': ['onstation', 'oncampus']})
    date = models.DateField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.student.username} - {self.description[:30]}"

