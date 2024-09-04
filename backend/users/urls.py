from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CustomUserViewSet, CustomTokenPairView


user_router = DefaultRouter()
user_router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    # path('auth/', include('djoser.urls')),
    # path(
    #     'auth/token/login/',
    #     CustomTokenPairView.as_view(),
    #     name='token_obtain_pair'
    # ),
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('auth/', include('djoser.urls.jwt')),
    path('', include(user_router.urls)),
]