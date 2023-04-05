from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
    UserSerializer,
    PasswordRetypeSerializer,
    CurrentPasswordSerializer
)
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import CustomUser
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
)


class CustomUserCreateSerializer(UserCreatePasswordRetypeSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'password',
            'photo'
        )
        required_fields = (
            'username',
            'email',
            'password'
        )


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'photo'
        )


class CustomPasswordSerializer(PasswordRetypeSerializer):
    current_password = serializers.CharField(required=True)


class SetEmailSerializer(
    serializers.ModelSerializer,
    CurrentPasswordSerializer
):
    new_email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('new_email', 'current_password')

    def validate(self, attrs):
        user = self.context['request'].user or self.user
        assert user is not None

        if attrs['new_email'] == user.email:
            raise serializers.ValidationError({
                'new_email': 'Введена та же почта, что и в аккаунте'
            })
        return super().validate(attrs)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализует/десериализует данные модели Category.
    """
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализует/десериализует данные модели Genre.
    """
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализует данные модели Title.
    """
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = (
            'id',
            'name',
            'year',
            'description',
            'photo',
            'genre',
            'category',
            'rating'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализует/десериализует данные модели Review.
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    title = serializers.SlugRelatedField(
        slug_field='pk',
        read_only=True,
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ])

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        """Можно оставить только один отзыв."""
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if (self.context['request'].method != 'PATCH'
                and Review.objects.filter(
                    author=author, title=title_id).exists()):
            raise serializers.ValidationError('Вы уже оставили отзыв')
        return data
