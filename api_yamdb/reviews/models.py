import datetime as dt

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

EVALUATIONS = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
]


class Category(models.Model):
    name = models.CharField(
        'Название',
        max_length=256
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True,
        db_index=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(
        'Название',
        max_length=256
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True,
        db_index=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField('Название', db_index=True)
    year = models.IntegerField(
        blank=True,
        validators=[
            MaxValueValidator(
                int(dt.datetime.now().year),
                message='Год выпуска не может быть позже текущего года'
            ),
            MinValueValidator(
                1888,
                message='Самый первый фильм снят в 1888 году'
            )
        ]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
        verbose_name='Жанр'
    )
    description = models.TextField(
        'Описание',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('-year',)
        verbose_name = 'Название произведения'
        verbose_name_plural = 'Названия произведений'


class Review(models.Model):
    text = models.TextField(
        blank=False
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    score = models.IntegerField(
        verbose_name='score',
        default=1,
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='user',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    comment = models.ForeignKey(
        'Comment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        ordering = ('id',)
        db_table = 'review'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title',),
                name='unique_review'),
            models.CheckConstraint(
                name='author_not_title_again',
                check=~models.Q(author=models.F('title')),
            )
        ]

    def __str__(self):
        return f' Автор: {self.author}. Текст:{self.text[:10]}'


class Comment(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Название',
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return f'{self.author}: {self.text}'
