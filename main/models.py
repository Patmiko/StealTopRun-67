from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from urllib.parse import urlparse, parse_qs



class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    REJECTED = 'REJECTED', 'Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'


class VerificationStatus(models.TextChoices):
    VERIFIED = "VERIFIED", "Verified"
    UNVERIFIED = "UNVERIFIED", "Unverified"
    BANNED = "BANNED", "Banned"


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='images/profiles/', blank=True, null=True)

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
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='images/game_images/', blank=True, null=True)
    categories = models.ManyToManyField(Category, through=GameCategoryAllocation)

    def __str__(self):
        return self.name


class SpeedrunType(models.Model):
    name = models.CharField(max_length=255)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='speedrun_types')
    description = models.CharField(max_length=255)


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
    speedrun_type = models.ForeignKey(SpeedrunType, on_delete=models.CASCADE, related_name='speedruns')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speedruns')

    @property
    def embed_url(self):
        # Parses the URL to get the video ID
        parsed_url = urlparse(self.url)
        if 'youtube.com' in parsed_url.netloc:
            query = parse_qs(parsed_url.query)
            video_id = query.get('v', [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be' in parsed_url.netloc:
            # Handle shortened links
            video_id = parsed_url.path.lstrip('/')
            return f"https://www.youtube.com/embed/{video_id}"
        return self.url # Return original if not recognized
    
    @property
    def formatted_time(self):
        """Converts total seconds into format like 1h 20min 30s 500ms (skipping zeroes)."""
        total_milliseconds = int(self.time * 1000)
        
        # Calculate individual units
        milliseconds = total_milliseconds % 1000
        total_seconds = total_milliseconds // 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        if seconds > 0:
            parts.append(f"{seconds}s")
        if milliseconds > 0:
            parts.append(f"{milliseconds}ms")
            
        # Fallback if time is effectively zero
        return " ".join(parts) if parts else "0s"


class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    date = models.DateField(default=date.today)

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
    date = models.DateField(default=date.today)


class GameRequest(Request):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    release_date = models.DateField()


class SpeedrunTypeRequest(Request):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='speedrun_type_requests')