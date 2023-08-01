from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token

# Reusable code to initialize user and token


class AuthAPIBaseTestCase(APITestCase):
    def setUp(self):  # Create test user and get its token
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        url = reverse('delete-user')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_token(self):
        self.client.credentials()
        url = reverse('delete-user')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Test User registration


class UserRegistrationViewTest(APITestCase):
    def test_success(self):
        url = reverse('register-user')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

        # Verify user data is in the database
        user = User.objects.filter(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, data['username'])  # Verify username
        self.assertTrue(user.check_password(data['password']))  # Verify password

    def test_missing_data(self):
        url = reverse('register-user')
        data = {'username': 'testuser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that the user is not created in the database
        user = User.objects.filter(username='testuser').first()
        self.assertIsNone(user)  # Check that the user does not exist

# Test User login


class UserLoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_success(self):
        url = reverse('login-user')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_invalid_credentials(self):
        url = reverse('login-user')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Test User deletion


class UserDeleteViewTest(APITestCase):
    def setUp(self):  # Create user and copy its token
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_success(self):
        url = reverse('delete-user')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(
            username='testuser').exists())

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtoken')
        url = reverse('delete-user')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_token(self):
        self.client.credentials()
        url = reverse('delete-user')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
