from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year',
                    'description', 'category')
    search_fields = ('name',)
    list_filter = ('year',)
    list_editable = ('category',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'pub_date', 'score', 'text',)
    list_editable = ('text', 'score',)
    list_filter = ('title', 'author',)
    search_fields = ('title', 'author',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'pub_date', 'author', 'review',)
    list_editable = ('text',)
    list_filter = ('pub_date', 'author', 'text', 'review',)
    search_fields = ('author', 'text', 'review',)
    empty_value_display = '-пусто-'
