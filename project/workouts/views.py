from rest_framework import status, permissions, authentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import *

class CreateWorkoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        data['user'] = request.user.id

        try:
            # Create new workout
            workout_serializer = WorkoutSerializer(data=data)
            if workout_serializer.is_valid():
                workout = workout_serializer.save()

                # Create exercises for the workout
                exercises = data.get('exercises', [])
                for exercise in exercises:
                    exercise['workout'] = workout.id
                    exercise['user'] = request.user.id
                    exercise_serializer = ExerciseSerializer(data=exercise)
                    if exercise_serializer.is_valid():
                        exercise_serializer.save()
                    else:
                        return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(workout_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MyWorkoutsView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkoutSerializer

    def get(self, request):
        user_id = request.user.id
        workouts = Workout.objects.filter(user_id=user_id)
        serializer = self.serializer_class(workouts, many=True)
        return Response(serializer.data)
    
class WorkoutListAPIView(ListAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

class ExerciseListAPIView(ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = WorkoutSerializer

class SetListAPIView(ListAPIView):
    queryset = Set.objects.all()
    serializer_class = WorkoutSerializer