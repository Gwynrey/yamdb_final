from django.db.models import CharField, TextField, EmailField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class UsernameCharacterValidator(UnicodeUsernameValidator):
    regex = r'^[\w.@+\-]+$'


class CustomUser(AbstractUser):
    username_validator = UsernameCharacterValidator()
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )
    username = CharField(
        max_length=150,
        unique=True,
        validators=[username_validator]
    )
    first_name = CharField(max_length=150, blank=True)
    last_name = CharField(max_length=150, blank=True)
    email = EmailField(max_length=254, unique=True)
    bio = TextField(
        blank=True,
        verbose_name='Информация о пользователе'
    )
    role = CharField(
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    confirmation_code = CharField(max_length=254, default='')

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff
