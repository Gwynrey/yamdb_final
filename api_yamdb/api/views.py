from django.db.models import Avg
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import tokens
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters, viewsets, status, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .permissions import (
    IsAdminOrReadOnly,
    IsAdminOrReadOnlyForGenresTitlesCat,
    IsAdmin,
    IsAuthorOrAdminOrModerReadOnly)
from .filters import TitleGenreFilter
from .serializers import (
    GenreSerializer,
    TitleSerializer,
    UserSerializer,
    TokenSerializer,
    SignUpSerializer,
    AccountSerializer,
    ReviewSerializer,
    CommentSerializer,
    CategorySerializer,
    TitleCreateSerializer
)
from users.models import CustomUser
from reviews.models import (
    Review,
    Title,
    Genre,
    Category
)


class ListCreateDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleGenreFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return TitleCreateSerializer
        return TitleSerializer


class CategoriesViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnlyForGenresTitlesCat,)
    throttle_classes = (AnonRateThrottle,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorOrAdminOrModerReadOnly,
        IsAuthenticatedOrReadOnly
    )
    pagination_class = PageNumberPagination
    throttle_classes = (AnonRateThrottle,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('pub_date',)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthorOrAdminOrModerReadOnly,
        IsAuthenticatedOrReadOnly
    )
    pagination_class = PageNumberPagination
    throttle_classes = (AnonRateThrottle,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('pub_date',)

    def get_queryset(self):
        review = get_object_or_404(Review,
                                   id=self.kwargs['review_id'],
                                   title=self.kwargs['title_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review,
                                   id=self.kwargs['review_id'],
                                   title=self.kwargs['title_id'])
        serializer.save(author=self.request.user,
                        review=review)
        return review.comments.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('username')
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)

    @action(
        methods=('GET', 'PATCH',),
        detail=False,
        url_path='me',
        serializer_class=AccountSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            request.user,
            data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    user = get_object_or_404(CustomUser, username=username)
    confirmation_code = serializer.validated_data['confirmation_code']
    if not tokens.default_token_generator.check_token(
        user.confirmation_code,
        confirmation_code
    ):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({'token': str(refresh.access_token)},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    confirmation_code = tokens.default_token_generator
    try:
        CustomUser.objects.get_or_create(
            username=username,
            email=email,
            confirmation_code=confirmation_code
        )
    except IntegrityError:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    send_mail(
        subject='Код подтверждения доступа Yamdb',
        message=f'Код подтверждения доступа: {confirmation_code}',
        from_email=settings.EMAIL,
        recipient_list=(email,))
    return Response(
        serializer.data,
        status=status.HTTP_200_OK)
