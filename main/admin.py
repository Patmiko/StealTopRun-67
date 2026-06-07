from django.contrib import admin
from .models import Game, Category, SpeedrunType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'release_date')
    search_fields = ('name',)
    list_filter = ('release_date', 'categories')
    filter_horizontal = ('categories',)

@admin.register(SpeedrunType)
class SpeedrunTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game')
    search_fields = ('name', 'game__name')
    list_filter = ('game',)
