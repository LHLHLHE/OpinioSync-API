from django.conf import settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
    UserSerializer,
    PasswordRetypeSerializer,
    UsernameSerializer
)
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from djoser.conf import settings as djoser_settings
from users.models import CustomUser
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment,
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


class CustomSetUsernameSerializer(UsernameSerializer):
    class Meta:
        model = CustomUser
        fields = (djoser_settings.LOGIN_FIELD,)


class SetEmailSerializer(serializers.ModelSerializer):
    new_email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('new_email',)

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
    photo = serializers.SerializerMethodField()

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

    def get_photo(self, obj):
        photo = obj.photo
        if not photo:
            return None
        return f'{settings.HOST_URL}{photo.url}'


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
        ]
    )
    pub_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M', read_only=True)

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


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализует/десериализует данные модели Comment.
    """
    review = serializers.SlugRelatedField(
        slug_field='pk',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    pub_date = serializers.DateTimeField(format='%d.%m.%Y %H:%M', read_only=True)

    class Meta:
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        model = Comment
