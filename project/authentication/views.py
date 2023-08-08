from rest_framework.status import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer

# Register a user for an account
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please provide username and password'}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=username, password=password)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)

# Log into user's account
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please provide username and password'}, status=HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid username or password'}, status=HTTP_401_UNAUTHORIZED)

# Delete user's account
class UserDeleteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            user.delete()
            return Response({'message': 'Account deleted successfully'}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer