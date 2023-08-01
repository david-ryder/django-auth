from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('users/', UserListView.as_view()),
    path('delete/', UserDeleteView.as_view()),
]
