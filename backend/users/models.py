from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager, PermissionsMixin)
from django.core.validators import RegexValidator
from django.db import models


class FoodgramUserManager(BaseUserManager):
    """
    Управление созданием пользвоателя
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class FoodgramUser(AbstractBaseUser, PermissionsMixin):
    """
    Модель пользователя
    """
    email = models.EmailField(max_length=254, unique=True, null=False)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    username = models.CharField(max_length=150, unique=True, null=False,
                                validators=[RegexValidator(
                                    regex=r"^[\w.@+-]+$",
                                    message="Only letters/digits")])
    avatar = models.ImageField(null=True, blank=True, upload_to="avatars/")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = FoodgramUserManager()

    @property
    def is_admin(self):
        return self.is_staff and self.is_superuser

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Subscriber(models.Model):
    """
    Модель для обозначения подписки между пользователями
    """
    subscriber = models.ForeignKey(FoodgramUser,
                                   on_delete=models.CASCADE,
                                   related_name="subscriber")
    publisher = models.ForeignKey(FoodgramUser,
                                  on_delete=models.CASCADE,
                                  related_name="publisher")

    def __str__(self):
        return f"{self.subscriber} подписан на {self.publisher}"

    class Meta:
        unique_together = ("subscriber", "publisher")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
