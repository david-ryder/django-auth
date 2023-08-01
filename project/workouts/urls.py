from django.urls import path
from .views import *

urlpatterns = [
    path('create-workout/', CreateWorkoutView.as_view()),
    path('my-workouts/', MyWorkoutsView.as_view()),
    path('list/<str:object_type>/', ObjectListAPIView.as_view()),
]

