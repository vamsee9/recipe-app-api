from django.urls import path
from .views import CreateUserView, AuthTokenView

urlpatterns = [
    path('register/', CreateUserView.as_view(), name='register'),
    path('login/', AuthTokenView.as_view(), name='login'),
]