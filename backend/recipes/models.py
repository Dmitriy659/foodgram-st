from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint


class Ingredient(models.Model):
    """
    Модель ингредиента
    """
    name = models.CharField(max_length=128,
                            verbose_name="Название")
    measurement_unit = models.CharField(max_length=64,
                                        verbose_name="Мера")

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_name"
            )
        ]
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class FoodgramUser(AbstractUser):
    """
    Модель пользователя
    """
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name="Email")
    first_name = models.CharField(max_length=150,
                                  verbose_name="Имя")
    last_name = models.CharField(max_length=150,
                                 verbose_name="Фамилия")
    username = models.CharField(max_length=150, unique=True,
                                validators=[RegexValidator(
                                    regex=r"^[\w.@+-]+$")],
                                verbose_name="Ник")
    avatar = models.ImageField(null=True,
                               blank=True,
                               upload_to="avatars/",
                               verbose_name="Аватарка")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("email",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Recipe(models.Model):
    """
    Модель рецепта
    """

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=256,
        verbose_name="Название рецепта"
    )
    text = models.TextField(
        verbose_name="Описание рецепта"
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления (мин)"
    )
    ingredients = models.ManyToManyField(
        to="Ingredient",
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты блюда"
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Изображение"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "name"],
                name="unique_recipe_per_author"
            )
        ]
        ordering = ("-id",)  # сначала новые рецепты


class RecipeIngredient(models.Model):
    """
    Связь рецепт - ингредиенты
    """
    recipe = models.ForeignKey(Recipe,
                               verbose_name="Где используются",
                               on_delete=models.CASCADE,
                               related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name="Используемые инргедиенты",
                                   on_delete=models.CASCADE,
                                   related_name="ingredient_recipes")
    amount = models.IntegerField(verbose_name="Количество",
                                 validators=[MinValueValidator(1)],
                                 )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_per_ingredient"
            )
        ]


class BaseUserRecipeRelation(models.Model):
    """
    Абстрактная модель для связи пользователя и рецепта
    """

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="%(class)ss"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="%(class)ss"
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["author", "recipe"],
                name="unique_%(class)s"
            )
        ]

    def __str__(self):
        return f"{self.author} - {self.recipe}"


class Favourite(BaseUserRecipeRelation):
    """
    Рецепты в избранном
    """

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(BaseUserRecipeRelation):
    """
    Рецепты в списке покупок
    """

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"


class Subscriber(models.Model):
    """
    Модель для обозначения подписки между пользователями
    """
    subscriber = models.ForeignKey(FoodgramUser,
                                   on_delete=models.CASCADE,
                                   related_name="subscribers")
    publisher = models.ForeignKey(FoodgramUser,
                                  on_delete=models.CASCADE,
                                  related_name="publishers")

    def __str__(self):
        return f"{self.subscriber} подписан на {self.publisher}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "publisher"],
                name="unique_subscription"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
