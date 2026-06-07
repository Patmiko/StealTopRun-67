from django.contrib import admin
from .models import Game, Category, Speedrun, SpeedrunType


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'release_date')
    search_fields = ('name',)
    list_filter = ('release_date',)


@admin.register(SpeedrunType)
class SpeedrunTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game')
    search_fields = ('name', 'game__name')
    list_filter = ('game',)


@admin.register(Speedrun)
class SpeedrunAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'time', 'date', 'status', 'speedtrun_type', 'user')
    search_fields = ('url', 'speedtrun_type__name', 'user__username')
    list_filter = ('status', 'date')
