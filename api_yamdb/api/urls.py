from django.urls import path, include
from rest_framework import routers

from .views import (
    CategoriesViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    UserViewSet,
    sign_up,
    token)

router_v1 = routers.DefaultRouter()
router_v1.register('categories', CategoriesViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')
router_v1.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path(
        'v1/auth/signup/',
        sign_up,
    ),
    path(
        'v1/auth/token/',
        token,
    ),
]
