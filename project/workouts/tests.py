from rest_framework import status
from django.urls import reverse
from .serializers import WorkoutSerializer, ExerciseSerializer, SetSerializer
from .models import Workout, Exercise, Set
from authentication.tests import AuthAPIBaseTestCase

# Test workout creation


class CreateWorkoutViewTest(AuthAPIBaseTestCase):
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


class MyWorkoutsViewTest(AuthAPIBaseTestCase):
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


class SetsAPIViewTest(AuthAPIBaseTestCase):
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
            set_obj = Set.objects.filter(exercise=exercise, weight=set_data['weight'], reps=set_data['reps']).first()
            self.assertIsNotNone(set_obj, f"Set {i+1} not found in the database.")
    
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
            Set.objects.create(user=self.user, exercise=exercise, weight=set_data['weight'], reps=set_data['reps'])

        url = reverse('create-get-sets', kwargs={'exercise_id': exercise.id})
        response = self.client.get(url, format='json')

        # Check if the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data matches the created sets
        self.assertEqual(len(response.data), len(data))
        for i, set_data in enumerate(data):
            self.assertEqual(response.data[i]['weight'], set_data['weight'])
            self.assertEqual(response.data[i]['reps'], set_data['reps'])

class SetDeleteAPIViewTest(AuthAPIBaseTestCase):
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
            Set.objects.create(user=self.user, exercise=exercise, weight=set_data['weight'], reps=set_data['reps'])

        # Get the ID of one of the sets to delete
        set_to_delete = Set.objects.filter(exercise=exercise).first()
        set_id = set_to_delete.id

        # Perform the deletion request
        url = reverse('delete-set', kwargs={'exercise_id': exercise.id, 'set_id': set_id})
        response = self.client.delete(url)

        # Check if the deletion was successful (HTTP 204 No Content)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the set has been deleted from the database
        set_exists = Set.objects.filter(id=set_id).exists()
        self.assertFalse(set_exists, "Set still exists in the database after deletion.")

        # Check the number of remaining sets for the exercise
        remaining_sets_count = Set.objects.filter(exercise=exercise).count()
        self.assertEqual(remaining_sets_count, len(sets_data) - 1, "Incorrect number of sets remaining after deletion.")