import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.full_name


class FilmWork(UUIDMixin, TimeStampedMixin):

    class FilmType(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv_show', _('tv_show')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'), blank=True, null=True)
    rating = models.FloatField(
        _('rating'), blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    type = models.CharField(_('type'), max_length=255, choices=FilmType.choices)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    persons = models.ManyToManyField(Person, through='PersonFilmWork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('filmwork')
        verbose_name_plural = _('filmworks')

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, verbose_name=_('filmwork'))
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_('genre'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('genre_filmwork')
        verbose_name_plural = _('genres_filmworks')
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'genre'],
                name='genre_film_work_film_work_id_genre_id_uniq'
            )
        ]


class PersonFilmWork(UUIDMixin):

    class RoleType(models.TextChoices):
        ACTOR = 'actor', _('actor')
        WRITER = 'writer', _('writer')
        DIRECTOR = 'director', _('director')

    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, verbose_name=_('filmwork'))
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_('person'))
    role = models.TextField(_('role'), choices=RoleType.choices, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('person_filmwork')
        verbose_name_plural = _('persons_filmworks')
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'person', 'role'],
                name='person_film_work_film_work_id_person_id_role_uniq'
            )
        ]