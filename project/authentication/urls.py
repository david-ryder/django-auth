from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register-user'),
    path('login/', UserLoginView.as_view(), name='login-user'),
    path('delete/', UserDeleteView.as_view(), name='delete-user'),
    path('users-list/', UserListView.as_view(), name='list-users'),
]
