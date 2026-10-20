from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.validators import UniqueValidator

from api.v1.validators import UsernameValidatorMixin
from api_yamdb.constants import (
    EMAIL_MAX_LENGTH, SCORE_MAX, SCORE_MIN, USERNAME_MAX_LENGTH
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        if value > date.today().year:
            raise ValidationError('Год не может быть больше текущего.')
        return value

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value):
        if not (SCORE_MIN <= value <= SCORE_MAX):
            raise ValidationError(
                f'Оценка должна быть от {SCORE_MIN} до {SCORE_MAX}.'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(
                author=request.user, title_id=title_id
            ).exists():
                raise ValidationError(
                    'Вы уже оставляли отзыв на это произведение!'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(UsernameValidatorMixin, serializers.Serializer):
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_MAX_LENGTH,
        required=True
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()
        if user_by_username and user_by_email:
            if user_by_username != user_by_email:
                raise serializers.ValidationError(
                    'Username и email принадлежат разным пользователям.'
                )
        elif user_by_username and not user_by_email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )
        elif user_by_email and not user_by_username:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        user, _ = User.objects.get_or_create(
            username=username, defaults={'email': email}
        )
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound({'username': 'Пользователь не найден.'})
        if not default_token_generator.check_token(user, confirmation_code):
            raise ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
        data['user'] = user
        return data


class UserSerializer(UsernameValidatorMixin, serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
