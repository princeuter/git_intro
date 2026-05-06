from django.contrib import admin
from .models import Genre, Person, FilmWork, GenreFilmWork, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    extra = 0


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    extra = 0


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)
    list_display = ('title', 'type', 'creation_date', 'rating', 'created', 'modified')
    list_filter = ('type', 'genres')
    search_fields = ('title', 'description', 'id')
    def created(self, obj):
        return obj.created
    created.short_description = 'Дата создания'

    def modified(self, obj):
        return obj.modified
    modified.short_description = 'Дата изменения'