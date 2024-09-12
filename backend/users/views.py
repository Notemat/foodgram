from django.shortcuts import get_object_or_404

from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated, )
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.permissions import PostOrReadOnly
from users.serializers import (
    AvatarSerializer, ChangePasswordSerializer,
    CustomTokenObtainPairSerializer, CustomUserSerializer,
    RegisterDataSerializer, SubscribeSerializer
)
from users.models import Subscribe, User


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
        permission_classes=(IsAuthenticated, ),
        url_path='me/avatar'
    )
    def manage_avatar(self, request):
        """Обновление и удаление аватара."""
        user = request.user
        if request.method == 'PUT':

            print(request.data)
            serializer = AvatarSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(
                {'message': 'Аватар удалён.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
        url_path='set_password'
    )
    def change_password(self, request, *args, **kwargs):
        """
        Переопределение метода создания пользователя
        для использования сериализатора регистрации.
        """

        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class CustomLogoutView(views.APIView):
    """Представление для удаления токенов."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {'detail': 'Токен удален.'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для спика подписок."""

    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)


class SubscribeViewSet(
    CreateModelMixin, DestroyModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для создания и удаления подписок."""

    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        """Сохраняем автора и объект подписки."""
        subscription = get_object_or_404(User, id=self.kwargs['user_id'])
        serializer.save(
            user=self.request.user, subscription=subscription
        )

    def delete(self, request, *args, **kwargs):
        """Удаляем объект из избранного."""
        subscription = get_object_or_404(User, id=self.kwargs['user_id'])
        subscribe = get_object_or_404(
            Subscribe,
            user=self.request.user,
            subscription=subscription
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
