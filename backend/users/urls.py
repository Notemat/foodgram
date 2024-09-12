from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    CustomLogoutView, CustomUserViewSet, CustomTokenPairView,
    SubscribeViewSet, SubscriptionViewSet
)


user_router = DefaultRouter()
user_router.register('users', CustomUserViewSet, basename='users')
user_router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)
user_router.register(
    r'users/subscriptions',
    SubscriptionViewSet,
    basename='subscriptions'
)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path(
        'auth/token/login/',
        CustomTokenPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'auth/token/logout/',
        CustomLogoutView.as_view(),
        name='token_logout'
    ),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(user_router.urls)),
]