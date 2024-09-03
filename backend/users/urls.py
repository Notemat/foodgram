from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet, CustomTokenViewSet


user_router = DefaultRouter()
user_router.register('users', CustomUserViewSet, basename='users')
user_router.register('tokens', CustomTokenViewSet, basename='tokens')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(user_router.urls)),
]