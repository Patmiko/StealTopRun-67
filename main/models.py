from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=255, unique=True)
    release_date = models.DateField()
    img_url = models.URLField(max_length=500, blank=True)

    categories = models.ManyToManyField(Category, related_name='games')

    def __str__(self):
        return self.name


class SpeedrunType(models.Model):
    name = models.CharField(max_length=255)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='speedrun_types')

    def __str__(self):
        return f"{self.game.name} - {self.name}"
