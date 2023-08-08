from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .serializers import *
from datetime import timedelta
from django.utils import timezone


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
                    exercise_serializer = ExerciseSerializer(
                        data=exercise_data)
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

    def get(self, request):
        user_id = request.user.id
        workouts = Workout.objects.filter(user_id=user_id)
        serializer = WorkoutSerializer(workouts, many=True)
        return Response(serializer.data)


class WorkoutExercisesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, workout_id):
        try:
            exercises = Exercise.objects.filter(
                user_id=request.user.id, workout_id=workout_id)
            exercise_serializer = ExerciseSerializer(exercises, many=True)
            if exercise_serializer.data == []:
                return Response({'error': 'No exercises found for this workout'}, status=status.HTTP_404_NOT_FOUND)
            return Response(exercise_serializer.data, status=status.HTTP_200_OK)
        except Workout.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)


class WorkoutUpdateDeleteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = WorkoutSerializer

    def get(self, request, workout_id):
        user_id = request.user.id
        return Workout.objects.filter(id=workout_id, user=user_id)

    def put(self, request, workout_id):
        user_id = request.user.id

        try:
            workout = Workout.objects.get(id=workout_id, user_id=user_id)
        except Workout.DoesNotExist:
            return Response({'error': 'Workout not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update workout name
        name = request.data.get('name', None)
        if name:
            workout.name = name
            workout.save()

        # Delete existing exercises for the workout
        Exercise.objects.filter(workout_id=workout_id,
                                user_id=user_id).delete()

        # Insert the updated exercises
        exercises = request.data.get('exercises', [])
        if exercises:
            for exercise_data in exercises:
                exercise_data['user'] = user_id
                exercise_data['workout'] = workout_id
                exercise_serializer = ExerciseSerializer(data=exercise_data)
                if exercise_serializer.is_valid():
                    exercise_serializer.save()
                else:
                    return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Workout modified successfully'})

    def delete(self, request, workout_id):
        user_id = request.user.id

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

    def get(self, request, exercise_id):
        # Check if exercise_id is present
        if exercise_id is None:
            return Response({'error': 'exercise_id must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exercise = Exercise.objects.get(id=exercise_id, user=request.user)
            sets = Set.objects.filter(exercise=exercise)
            set_serializer = SetSerializer(sets, many=True)
            return Response(set_serializer.data, status=status.HTTP_200_OK)
        except Exercise.DoesNotExist:
            return Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, exercise_id):

        # Check if exercise_id is present
        if exercise_id is None:
            return Response({'error': 'exercise_id must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        sets_data = request.data

        # Create sets for the exercise
        sets_created = []
        try:
            # Retrieve the exercise by ID and the current user
            exercise = Exercise.objects.get(id=exercise_id, user=request.user)
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


class SetDeleteAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, set_id):
        try:
            # Find the set with the specified setid and belonging to the current user
            set_to_delete = Set.objects.get(
                id=set_id, user=request.user)
            set_to_delete.delete()
            return Response({'message': 'Set deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Set.DoesNotExist:
            return Response({'error': 'Set not found'}, status=status.HTTP_404_NOT_FOUND)


class WorkoutSummaryAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Retrieve all sets performed by the user in the last 4 hours
        sets = Set.objects.filter(
            user=request.user, created_at__gte=four_hours_ago)

        # Organize the sets by exercise
        exercise_sets = {}
        for set_data in sets:
            exercise_name = set_data.exercise.name
            if exercise_name not in exercise_sets:
                exercise_sets[exercise_name] = []
            serialized_set = SetSerializer(set_data).data
            exercise_sets[exercise_name].append(serialized_set)

        return Response(exercise_sets, status=status.HTTP_200_OK)


class ExerciseProgressionAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Get all exercises performed in the last 4 hours that are eligible for progression
    def get(self, request):
        # Get the datetime 4 hours ago
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Retrieve the sets performed in the last 4 hours
        sets = Set.objects.filter(
            user=request.user, created_at__gte=four_hours_ago)

        # Initialize list to store results
        eligible_exercises = []

        # Loop through each exercise to determine if each goal has been met
        for set in sets:
            exercise = set.exercise

            # Check if the exercise is already added to eligible exercises list
            if exercise.id in eligible_exercises:
                continue

            # Get all sets for this exercise performed in the last 4 hours
            exercise_sets = sets.filter(exercise=exercise)

            # Check if all sets meet the criteria
            all_sets_meet_criteria = all(
                s.weight >= exercise.current_weight and s.reps >= exercise.target_reps
                for s in exercise_sets
            )

            # Check if the exercise meets the progression criteria
            if (
                all_sets_meet_criteria
                and exercise.target_sets <= exercise_sets.count()
            ):
                eligible_exercises.append(exercise.id)

        # Retrieve the eligible exercises
        exercises = Exercise.objects.filter(id__in=eligible_exercises)

        # Serialize the exercises
        exercise_serializer = ExerciseSerializer(exercises, many=True)

        return Response(exercise_serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        # Get the exercise_ids from the request
        exercises_to_progress = request.data.get('exercises', [])

        updated_exercises = []

        # For each exercise in the array, increment
        for exercise_id in exercises_to_progress:
            try:
                exercise = Exercise.objects.get(id=exercise_id, user=request.user)
                exercise.current_weight += exercise.weight_modifier
                exercise.save()
                updated_exercises.append(exercise)
            except Exercise.DoesNotExist:
                pass

        # Serialize the updated exercises and return them
        exercise_serializer = ExerciseSerializer(updated_exercises, many=True)

        return Response(exercise_serializer.data, status=status.HTTP_200_OK)

class WorkoutListAPIView(ListAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer


class ExerciseListAPIView(ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


class SetListAPIView(ListAPIView):
    queryset = Set.objects.all()
    serializer_class = SetSerializer
