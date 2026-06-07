from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='categories', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


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

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        REJECTED = 'REJECTED', 'Rejected'
        ACCEPTED = 'ACCEPTED', 'Accepted'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    speedtrun_type = models.ForeignKey(SpeedrunType, on_delete=models.CASCADE, related_name='speedruns')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='speedruns')
