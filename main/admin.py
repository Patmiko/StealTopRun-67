from django.contrib import admin
from django.contrib import messages
from django.http import HttpRequest
from django.db.models import QuerySet
from django.contrib.admin import ModelAdmin
from .actions import accept_and_configure_game
from .models import User, Status, VerificationStatus, Game, Report, Category, Speedrun, SpeedrunType, GameCategoryAllocation, SpeedrunReport, UserReport, GameRequest, SpeedrunTypeRequest



@admin.register(GameCategoryAllocation)
class GameCategoryAllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'category')
    search_fields = ('game__name', 'category__name')
    list_filter = ('game', 'category')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'avatar_url', 'status', 'username', 'email', 'password')
    search_fields = ('id', 'username', 'email')
    list_filter = ('status',)

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


@admin.action(description="Dismiss reports")
def dismiss_reports(
    modeladmin: ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[Report]
):
    updated = queryset.update(status=Status.REJECTED)
    modeladmin.message_user(
        request, 
        f'Successfully dismissed {updated} reports.', 
        messages.SUCCESS
    )


@admin.action(description='Resolve and Ban User')
def resolve_user_report(
    modeladmin: ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[UserReport]
):
    updated_reports = queryset.update(status=Status.ACCEPTED)

    banned_count = 0
    for report in queryset:
        if report.target.status != VerificationStatus.BANNED:
            report.target.status = VerificationStatus.BANNED
            report.target.save()
            banned_count += 1
            
    modeladmin.message_user(
        request, 
        f'Resolved {updated_reports} reports. Banned {banned_count} user(s).', 
        messages.SUCCESS
    )


@admin.action(description='Resolve and Ban User')
def resolve_speedrun_report(
    modeladmin: ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[SpeedrunReport]
):
    updated_reports = queryset.update(status=Status.ACCEPTED)

    banned_count = 0
    for report in queryset:
        speedrun_owner = report.target.user
        if speedrun_owner.status != VerificationStatus.BANNED:
            speedrun_owner.status = VerificationStatus.BANNED
            speedrun_owner.save()
            banned_count += 1

    modeladmin.message_user(
        request, 
        f'Resolved {updated_reports} reports. Banned {banned_count} user(s).', 
        messages.SUCCESS
    )


@admin.register(SpeedrunReport)
class SpeedrunReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'target', 'reporter', 'date', 'status', 'title')
    search_fields = ('target__url', 'reporter__username', 'title')
    list_filter = ('status', 'date')

    actions = [dismiss_reports, resolve_speedrun_report]


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'target', 'reporter', 'date', 'status', 'title')
    search_fields = ('target__user__username', 'reporter__username', 'title')
    list_filter = ('status', 'date')

    actions = [dismiss_reports, resolve_user_report]


@admin.register(GameRequest)
class GameRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'date', 'title', 'description')
    search_fields = ('user__username', 'title')
    list_filter = ('status', 'date')
    actions = [accept_and_configure_game]


@admin.register(SpeedrunTypeRequest)
class SpeedrunTypeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'date', 'name', 'description', 'game')
    search_fields = ('user__username', 'name')
    list_filter = ('status', 'date')
