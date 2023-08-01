from rest_framework import status
from django.urls import reverse
from .serializers import WorkoutSerializer, ExerciseSerializer, SetSerializer
from .models import Workout, Exercise, Set
from authentication.tests import AuthAPIBaseTestCase

# Test workout creation


class CreateWorkoutViewTest(AuthAPIBaseTestCase):
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
    def test_success(self):
        workout1 = Workout.objects.create(name='Workout 1', user=self.user)
        workout2 = Workout.objects.create(name='Workout 2', user=self.user)

        url = reverse('get-my-workouts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = WorkoutSerializer([workout1, workout2], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_empty(self):
        url = reverse('get-my-workouts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class SetsAPIViewTest(AuthAPIBaseTestCase):
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

        url = reverse('create-sets', kwargs={'exercise_id': exercise.id})

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(len(response.data), len(data))

        for i, set_data in enumerate(data):
            set_obj = Set.objects.filter(exercise=exercise, weight=set_data['weight'], reps=set_data['reps']).first()
            self.assertIsNotNone(set_obj, f"Set {i+1} not found in the database.")