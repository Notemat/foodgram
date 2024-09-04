from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated, )
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.permissions import PostOrReadOnly
from users.serializers import (
    AvatarSerializer, CustomTokenObtainPairSerializer,
    CustomUserSerializer, RegisterDataSerializer
)
from users.models import User


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вью-класс для пользователей."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (PostOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    lookup_field = 'id'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
        url_path='me'
    )
    def me(self, request):
        """Получение или обновление пользователя."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='me/avatar'
    )
    def manage_avatar(self, request):
        """Обновление и удаление аватара."""
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(
                {'message': 'Аватар удалён.'},
                status=status.HTTP_204_NO_CONTENT
            )

    def create(self, request, *args, **kwargs):
        """
        Переопределение метода создания пользователя
        для использования сериализатора регистрации.
        """

        serializer = RegisterDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'user': CustomUserSerializer(user).data,
                'message': 'Пользователь успешно создан.'
            },
            status=status.HTTP_201_CREATED
        )


class CustomTokenPairView(TokenObtainPairView):
    """Вьюсет для токена."""

    serializer_class = CustomTokenObtainPairSerializer
