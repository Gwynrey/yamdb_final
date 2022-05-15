import re

from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from users.models import CustomUser
from reviews.models import (
    Comment,
    Review,
    Category,
    Genre,
    Title
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        read_only_fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating')


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username',
                              read_only=True,)
    score = serializers.IntegerField(required=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate_score(self, score):
        if not isinstance(score, int) and score not in range(1, 11,):
            raise serializers.ValidationError(
                'Тип данных не целое число или превышает допустимое значние'
            )
        return score

    def validate(self, data):
        context = self.context['request']
        title = context.parser_context['kwargs']['title_id']
        author = context.user
        review = Review.objects.filter(title_id=title, author=author)
        if not context.method == 'POST':
            return data
        if review.exists():
            raise serializers.ValidationError(
                detail='Вы уже оставили свой отзыв к данному произведению',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username',
                              read_only=True,
                              allow_null=False)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class UsernameValidation(object):

    def __call__(self, value):
        regex_user = r'^[\w.@+\-]+$'
        if value == 'me' and re.match(regex_user, value):
            raise serializers.ValidationError('Недопустимое имя')
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UsernameValidation()]
    )
    confirmation_code = serializers.CharField(max_length=254)


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UsernameValidation()]
    )
    email = serializers.EmailField(max_length=254)


class AccountSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)
