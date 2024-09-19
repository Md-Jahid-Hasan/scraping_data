from django.urls import path
from .views import LoginView, CreateUserView, CurrentUser

app_name = 'user'

urlpatterns = [
    path('', CurrentUser.as_view(), name='me'),
    path('login/', LoginView.as_view(), name='login'),
    path('create/', CreateUserView.as_view(), name='create')
]