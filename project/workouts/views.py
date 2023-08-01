from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import *

class CreateWorkoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

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
                for exercise_data in exercises:
                    exercise_data['workout'] = workout.id
                    exercise_data['user'] = request.user.id
                    exercise_serializer = ExerciseSerializer(data=exercise_data)
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = WorkoutSerializer

    def get(self, request):
        user_id = request.user.id
        workouts = Workout.objects.filter(user_id=user_id)
        serializer = self.serializer_class(workouts, many=True)
        return Response(serializer.data)
    
class WorkoutExercisesView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        workout_id = self.kwargs.get('workout_id', None)
        user_id = self.request.user.id

        try:
            exercises = Exercise.objects.filter(user_id=user_id, workout_id=workout_id)
            return exercises
        except Workout.DoesNotExist:
            return Exercise.objects.none()
        
class WorkoutModifyView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = WorkoutSerializer

    def get_queryset(self):
        workout_id = self.kwargs.get('workout_id', None)
        user_id = self.request.user.id
        return Workout.objects.filter(id=workout_id, user=user_id)
    
    def put(self, request, *args, **kwargs):
        workout_id = self.kwargs.get('workout_id', None)
        user_id = self.request.user.id

        try:
            workout = Workout.objects.get(id=workout_id, user_id=user_id)
        except Workout.DoesNotExist:
            return Response({'error': 'Workoutnot found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update workout name
        name = request.data.get('name', None)
        if name:
            workout.name = name
            workout.save()
        
        # Delete existing exercises for the workout
        Exercise.objects.filter(workout_id=workout_id, user_id=user_id).delete()

        # Insert the updated exercises
        exercises = request.data.get('exercises', [])
        if exercises:
            for exercise_data in exercises:
                exercise_data['workout'] = workout_id
                exercise_data['user'] = user_id
                exercise_serializer = ExerciseSerializer(data=exercise_data)
                if exercise_serializer.is_valid():
                    exercise_serializer.save()
                else:
                    return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Workout modified successfully'})
    
    def destroy(self, request, *args, **kwargs):
        workout_id = self.kwargs.get('workout_id', None)
        user_id = self.request.user.id

        try:
            workout = Workout.objects.get(user_id=user_id, id=workout_id)
        except Workout.DoesNotExist:
            return Response({'error': 'Workout not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the workout
        workout.delete()

        return Response({'message': 'Workout and exercises deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class WorkoutListAPIView(ListAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

class ExerciseListAPIView(ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

class SetListAPIView(ListAPIView):
    queryset = Set.objects.all()
    serializer_class = SetSerializer