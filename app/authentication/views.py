from .serializers import UserSerializer, AuthTokenSerializer, EmailSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

class AuthTokenView(generics.CreateAPIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        if token.expiry_date < timezone.now():
            token.delete()
            token = Token.objects.create(user=user)

        return Response({'token': token.key})

class PasswordResetView(generics.CreateAPIView):
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', args=(uid, token))
            )

            # Send password reset email
            send_mail(
                'Password Reset',
                f'Please follow the link to reset your password: {reset_url}',
                'noreply@example.com',
                [email],
            )

        return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)