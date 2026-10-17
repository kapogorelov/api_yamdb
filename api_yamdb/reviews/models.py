from django.db import models

from reviews.constants import NAME_MAX_LENGTH, SLUG_MAX_LENGTH, STR_LENGTH
from reviews.validators import validate_year


class NameSlugModel(models.Model):
    """Абстрактная модель с полями name и slug для категорий и жанров."""

    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(
        'Слаг',
        max_length=SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_LENGTH]


class Category(NameSlugModel):
    """Категория (тип) произведения: «Фильмы», «Книги», «Музыка»."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    """Жанр произведения: «Сказка», «Рок», «Артхаус»."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведение: одна категория, несколько жанров."""

    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    year = models.SmallIntegerField(
        'Год выпуска',
        validators=(validate_year,),
        db_index=True,
    )
    description = models.TextField('Описание', blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанры',
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name[:STR_LENGTH]


class GenreTitle(models.Model):
    """Связь произведения и жанра.

    При удалении жанра удаляется только связь, само произведение остаётся.
    """

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'жанр произведения'
        verbose_name_plural = 'Жанры произведений'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'genre'), name='unique_title_genre'
            ),
        )

    def __str__(self):
        return f'{self.title} — {self.genre}'
