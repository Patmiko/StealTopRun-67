from django.contrib.auth.models import AbstractUser
from django.db import models


class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    REJECTED = 'REJECTED', 'Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'


class VerificationStatus(models.TextChoices):
    VERIFIED = "VERIFIED", "Verified"
    UNVERIFIED = "UNVERIFIED", "Unverified"
    BANNED = "BANNED", "Banned"


class User(AbstractUser):
    avatar_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED
    )


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class GameCategoryAllocation(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'category')

    def __str__(self):
        return f"{self.game.name} - {self.category.name}"


class Game(models.Model):
    name = models.CharField(max_length=255, unique=True)
    release_date = models.DateField()
    img_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class SpeedrunType(models.Model):
    name = models.CharField(max_length=255)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='speedrun_types')

    def __str__(self):
        return f"{self.game.name} - {self.name}"


class Speedrun(models.Model):
    url = models.CharField(max_length=255)
    time = models.FloatField()
    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    speedtrun_type = models.ForeignKey(SpeedrunType, on_delete=models.CASCADE, related_name='speedruns')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speedruns')


class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports"
    )


class UserReport(Report):
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_about_me"
    )


class SpeedrunReport(Report):
    target = models.ForeignKey(
        Speedrun,
        on_delete=models.CASCADE,
        related_name="reports_about_speedrun"
    )


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    date = models.DateField()

