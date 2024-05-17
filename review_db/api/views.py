from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser import permissions
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
)
from users.models import CustomUser
from .permissions import (
    ReadOnlyPermission,
    CreateAndUpdatePermission,
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CustomUserSerializer,
    CustomUserCreateSerializer,
    CustomPasswordSerializer,
    SetEmailSerializer,
    CommentSerializer,
    CustomSetUsernameSerializer
)
from .filters import TitlesFilter


class CustomUserViewSet(UserViewSet):

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'set_password':
            return CustomPasswordSerializer
        elif self.action == 'set_username':
            return CustomSetUsernameSerializer
        elif self.action == 'set_email':
            return SetEmailSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action == 'set_email':
            self.permission_classes = [permissions.CurrentUserOrAdmin]
        return super().get_permissions()

    def get_queryset(self):
        return CustomUser.objects.all()

    @action(['post'], detail=False, url_path='set_email')
    def set_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        new_email = serializer.data['new_email']

        setattr(user, 'email', new_email)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoriesGenresBaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый класс для категорий и жанров.
    """
    permission_classes = (ReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class CategoriesViewSet(CategoriesGenresBaseViewSet):
    """
    Реализует основные операции с моделью категорий:
    - получения списка категорий
    - создание категории
    - удаление категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(CategoriesGenresBaseViewSet):
    """
    Реализует основные операции с моделью жанров:
    - получения списка жанров
    - создание жанра
    - удаление жанра.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    """
    Реализует основные операции с моделью произведений:
    - возвращает список всех произведений
    - добавление нового произведения
    - возвращает информацию о произведении
    - обновляет информацию о произведении
    - удаляет произведение
    """
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).order_by('-rating')
    serializer_class = TitleSerializer
    permission_classes = (ReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReadOnlyPermission | CreateAndUpdatePermission,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReadOnlyPermission | CreateAndUpdatePermission,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
