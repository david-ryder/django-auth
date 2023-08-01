from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import *

class CreateWorkoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        data['user'] = request.user.id

        # Check if 'name' exists in the request data
        if 'name' not in data:
            return Response({'error': 'Workout name is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if 'exercises' list is empty
        exercises = data.get('exercises', [])
        if not exercises:
            return Response({'error': 'Exercises are missing'}, status=status.HTTP_400_BAD_REQUEST)

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
    
class WorkoutExercisesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseSerializer

    def get(self, *args, **kwargs):
        workout_id = self.kwargs.get('workout_id', None)
        user_id = self.request.user.id

        try:
            exercises = Exercise.objects.filter(user_id=user_id, workout_id=workout_id)
            exercise_serializer = self.serializer_class(exercises, many=True)
            return Response(exercise_serializer.data, status=status.HTTP_200_OK)
        except Workout.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        
class WorkoutUpdateDeleteView(APIView):
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
    
    def delete(self, request, *args, **kwargs):
        workout_id = self.kwargs.get('workout_id', None)
        user_id = self.request.user.id

        try:
            workout = Workout.objects.get(user_id=user_id, id=workout_id)
        except Workout.DoesNotExist:
            return Response({'error': 'Workout not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the workout
        workout.delete()

        return Response({'message': 'Workout and exercises deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class SetsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        exercise_id = self.kwargs.get('exercise_id', None)

        # Check if exercise_id is present
        if exercise_id is None:
            return Response({'error': 'exercise_id must be provided'}, status=status.HTTP_400_BAD_REQUEST)
    
        sets_data = request.data
        
        # Create sets for the exercise
        sets_created = []
        try:
            exercise = Exercise.objects.get(id=exercise_id, user=request.user)  # Retrieve the exercise by ID and the current user
        except Exercise.DoesNotExist:
            return Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

        for set_data in sets_data:
            # Include the exercise ID and user ID in the set data
            set_data['exercise'] = exercise.id
            set_data['user'] = request.user.id

            set_serializer = SetSerializer(data=set_data)
            if set_serializer.is_valid():
                set_serializer.save()
                sets_created.append(set_serializer.data)
            else:
                return Response(set_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(sets_created, status=status.HTTP_201_CREATED)



class WorkoutListAPIView(ListAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

class ExerciseListAPIView(ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

class SetListAPIView(ListAPIView):
    queryset = Set.objects.all()
    serializer_class = SetSerializer