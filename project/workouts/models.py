from django.db import models
from django.contrib.auth.models import User

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    current_weight = models.IntegerField()
    target_sets = models.IntegerField()
    target_reps = models.IntegerField()
    weight_modifier = models.IntegerField()

class Set(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.IntegerField()
    reps = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
