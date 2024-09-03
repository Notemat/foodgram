from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet, CustomTokenPairView


user_router = DefaultRouter()
user_router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/token/login/', CustomTokenPairView.as_view(), name='token_obtain_pair'),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(user_router.urls)),
]