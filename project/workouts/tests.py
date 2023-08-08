from rest_framework import status
from django.urls import reverse
from .serializers import WorkoutSerializer, ExerciseSerializer, SetSerializer
from .models import Workout, Exercise, Set
from authentication.tests import AuthAPIBaseTestCase
from django.utils import timezone
from datetime import timedelta


class WorkoutBaseTestCase(AuthAPIBaseTestCase):
    def create_exercise_and_set(self, exercise_name, set_data, created_at):
        # Create an exercise and a set associated with that exercise
        workout = Workout.objects.create(user=self.user, name='test workout')
        exercise = Exercise.objects.create(user=self.user, workout=workout, name=exercise_name,
                                           current_weight=100, target_sets=3, target_reps=10, weight_modifier=5)

        Set.objects.create(user=self.user, exercise=exercise,
                           weight=set_data['weight'], reps=set_data['reps'], created_at=created_at)

# Test workout creation


class CreateWorkoutViewTest(WorkoutBaseTestCase):
    # Test successful query
    def test_success(self):
        url = reverse('create-workout')
        data = {
            "name": "new workout",
            "exercises": [
                {
                    "name": "Exercise 1",
                    "current_weight": 100,
                    "target_sets": 3,
                    "target_reps": 10,
                    "weight_modifier": 10
                },
                {
                    "name": "Exercise 2",
                    "current_weight": 100,
                    "target_sets": 3,
                    "target_reps": 10,
                    "weight_modifier": 10
                }
            ]
        }

        response = self.client.post(url, data=data, format='json')

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the workout and exercises are created in the database
        workout_id = response.data['id']
        self.assertTrue(Workout.objects.filter(id=workout_id).exists())

        # Assert that each exercise has been created in the database
        exercises = data['exercises']
        for exercise_data in exercises:
            exercise_name = exercise_data['name']
            self.assertTrue(
                Exercise.objects.filter(
                    workout_id=workout_id, name=exercise_name).exists()
            )

    # Test missing name
    def test_missing_name(self):
        url = reverse('create-workout')
        data = {
            "exercises": [
                {
                    "name": "Exercise 1",
                    "current_weight": 100,
                    "target_sets": 3,
                    "target_reps": 10,
                    "weight_modifier": 10
                }
            ]
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test empty exercises list
    def test_missing_exercises(self):
        url = reverse('create-workout')
        data = {
            "name": "new workout",
            "exercises": []
        }
        response = self.client.post(url, data=data, format='json')

        # Assert that the request is unsuccessful
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MyWorkoutsViewTest(WorkoutBaseTestCase):
    # Test successful query
    def test_success(self):
        workout1 = Workout.objects.create(name='Workout 1', user=self.user)
        workout2 = Workout.objects.create(name='Workout 2', user=self.user)

        url = reverse('get-my-workouts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = WorkoutSerializer([workout1, workout2], many=True).data
        self.assertEqual(response.data, expected_data)

    # Test empty query
    def test_empty(self):
        url = reverse('get-my-workouts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class SetsAPIViewTest(WorkoutBaseTestCase):
    # Test successful query
    def test_create_success(self):
        # Create an exercise to associate with the set
        workout = Workout.objects.create(user=self.user, name='test workout')
        exercise = Exercise.objects.create(user=self.user, workout=workout, name='test exercise',
                                           current_weight=100, target_sets=3, target_reps=10, weight_modifier=5)
        data = [
            {
                "weight": 50,
                "reps": 10
            },
            {
                "weight": 60,
                "reps": 8
            }
        ]

        url = reverse('create-get-sets', kwargs={'exercise_id': exercise.id})

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(response.data), len(data))

        for i, set_data in enumerate(data):
            set_obj = Set.objects.filter(
                exercise=exercise, weight=set_data['weight'], reps=set_data['reps']).first()
            self.assertIsNotNone(
                set_obj, f"Set {i+1} not found in the database.")

    # Test successful fetch
    def test_get_success(self):
        # Create an exercise to associate with the set
        workout = Workout.objects.create(user=self.user, name='test workout')
        exercise = Exercise.objects.create(user=self.user, workout=workout, name='test exercise',
                                           current_weight=100, target_sets=3, target_reps=10, weight_modifier=5)
        data = [
            {
                "weight": 50,
                "reps": 10
            },
            {
                "weight": 60,
                "reps": 8
            }
        ]

        for set_data in data:
            Set.objects.create(user=self.user, exercise=exercise,
                               weight=set_data['weight'], reps=set_data['reps'])

        url = reverse('create-get-sets', kwargs={'exercise_id': exercise.id})
        response = self.client.get(url, format='json')

        # Check if the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data matches the created sets
        self.assertEqual(len(response.data), len(data))
        for i, set_data in enumerate(data):
            self.assertEqual(response.data[i]['weight'], set_data['weight'])
            self.assertEqual(response.data[i]['reps'], set_data['reps'])


class SetDeleteAPIViewTest(WorkoutBaseTestCase):
    # Test successful deletion
    def test_delete_success(self):
        # Create an exercise to associate with the sets
        workout = Workout.objects.create(user=self.user, name='test workout')
        exercise = Exercise.objects.create(user=self.user, workout=workout, name='test exercise',
                                           current_weight=100, target_sets=3, target_reps=10, weight_modifier=5)

        # Create some sets for the exercise
        sets_data = [
            {
                "weight": 50,
                "reps": 10
            },
            {
                "weight": 60,
                "reps": 8
            }
        ]
        for set_data in sets_data:
            Set.objects.create(user=self.user, exercise=exercise,
                               weight=set_data['weight'], reps=set_data['reps'])

        # Get the ID of one of the sets to delete
        set_to_delete = Set.objects.filter(exercise=exercise).first()
        set_id = set_to_delete.id

        # Perform the deletion request
        url = reverse(
            'delete-set', kwargs={'set_id': set_id})
        response = self.client.delete(url)

        # Check if the deletion was successful (HTTP 204 No Content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the set has been deleted from the database
        set_exists = Set.objects.filter(id=set_id).exists()
        self.assertFalse(
            set_exists, "Set still exists in the database after deletion.")

        # Check the number of remaining sets for the exercise
        remaining_sets_count = Set.objects.filter(exercise=exercise).count()
        self.assertEqual(remaining_sets_count, len(sets_data) - 1,
                         "Incorrect number of sets remaining after deletion.")


class WorkoutSummaryAPIViewTest(WorkoutBaseTestCase):
    def test_get_exercises_and_sets_in_last_4_hours(self):
        # Calculate the datetime 3 hours ago from the current time
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Create exercises and sets, all within the last 4 hours
        self.create_exercise_and_set(
            'exercise 1', {'weight': 50, 'reps': 10}, four_hours_ago)
        self.create_exercise_and_set(
            'exercise 2', {'weight': 60, 'reps': 8}, four_hours_ago)

        # Make the GET request to fetch the exercises and sets in the last 4 hours
        url = reverse('workout-summary')
        response = self.client.get(url, format='json')

        # Check if the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the correct exercises and sets in the desired JSON format
        # Number of exercises performed within the last 4 hours
        self.assertEqual(len(response.data), 2)
        self.assertIn('exercise 1', response.data)
        self.assertIn('exercise 2', response.data)
        self.assertNotIn('exercise 3', response.data)

        # Check the sets data for each exercise
        # Only one set for 'exercise 1' was performed in the last 4 hours
        self.assertEqual(len(response.data['exercise 1']), 1)
        self.assertEqual(response.data['exercise 1'][0]['weight'], 50)
        self.assertEqual(response.data['exercise 1'][0]['reps'], 10)

        # Only one set for 'exercise 2' was performed in the last 4 hours
        self.assertEqual(len(response.data['exercise 2']), 1)
        self.assertEqual(response.data['exercise 2'][0]['weight'], 60)
        self.assertEqual(response.data['exercise 2'][0]['reps'], 8)


class ExerciseProgressionAPIViewTest(WorkoutBaseTestCase):
    def test_exercise_progression_results(self):
        now = timezone.now()
        url = reverse('progress-exercises')

        # Create an exercise and set that meets the criteria
        set_data = {'weight': 100, 'reps': 10}  # Exercise meets criteria
        self.create_exercise_and_set(exercise_name="Exercise 1", set_data=set_data, created_at=now - timedelta(hours=2))
        response = self.client.get(url)  # Replace with your actual URL
        self.assertEqual(response.status_code, 200)

        # Create an exercise and set that doesn't meet the criteria
        set_data = {'weight': 40, 'reps': 8}  # Exercise doesn't meet criteria
        self.create_exercise_and_set(exercise_name="Exercise 2", set_data=set_data, created_at=now - timedelta(hours=1))
        response = self.client.get(url)  # Replace with your actual URL
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        # Create an exercise with sets that meet the criteria
        exercise_name = "Exercise 3"
        set_data_1 = {'weight': 70, 'reps': 12}
        set_data_2 = {'weight': 70, 'reps': 12}
        set_data_3 = {'weight': 70, 'reps': 12}
        self.create_exercise_and_set(exercise_name=exercise_name, set_data=set_data_1, created_at=now - timedelta(hours=2))
        self.create_exercise_and_set(exercise_name=exercise_name, set_data=set_data_2, created_at=now - timedelta(hours=1))
        self.create_exercise_and_set(exercise_name=exercise_name, set_data=set_data_3, created_at=now - timedelta(minutes=30))
        response = self.client.get(url)  # Replace with your actual URL
        self.assertEqual(response.status_code, 200)