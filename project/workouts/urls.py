from django.urls import path
from .views import *

urlpatterns = [
    path('create-workout/', CreateWorkoutView.as_view()),
    path('my-workouts/', MyWorkoutsView.as_view()),
    path('workouts-list/', WorkoutListAPIView.as_view()),
    path('exercises-list/', ExerciseListAPIView.as_view()),
    path('sets-list/', SetListAPIView.as_view()),
    path('<int:workout_id>/exercises/', WorkoutExercisesView.as_view()),
    path('<int:workout_id>/modify/', WorkoutModifyView.as_view()),
]

