from unittest.mock import Mock
from django.test import TestCase
from django.utils import timezone
from django.contrib import messages

from .admin import dismiss_reports, resolve_speedrun_report, resolve_user_report
from .models import User, UserReport, SpeedrunReport, Status, VerificationStatus, Speedrun, Game, SpeedrunType

class BaseReportTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        self.target_user = User.objects.create(
            username="bad_user",
            email="bad@example.com",
            password="password",
            status=VerificationStatus.VERIFIED,
        )

        self.reporter_user = User.objects.create(
            username="reporter",
            email="reporter@example.com",
            password="password",
            status=VerificationStatus.VERIFIED,
        )

        self.game = Game.objects.create(
            name="Minecraft",
            release_date="2011-11-18"
        )

        self.speedrun_type = SpeedrunType.objects.create(
            name="Any%",
            game=self.game
        )

class DismissReportsTest(BaseReportTestCase):
    def test_should_reject_reports(self):
        report = UserReport.objects.create(
            target=self.target_user,
            reporter=self.reporter_user,
            title="test",
            description="test",
            date=timezone.now(),
            status=Status.PENDING,
        )

        queryset = UserReport.objects.filter(id=report.id)

        modeladmin = Mock()
        request = Mock()

        dismiss_reports(modeladmin, request, queryset)

        report.refresh_from_db()

        self.assertEqual(report.status, Status.REJECTED)
        self.assertEqual(report.target.status, VerificationStatus.VERIFIED)

class ResolveUserReportTest(BaseReportTestCase):
    def test_should_ban_user(self):
        report = UserReport.objects.create(
            target=self.target_user,
            reporter=self.reporter_user,
            title="test",
            description="test",
            date=timezone.now(),
            status=Status.PENDING,
        )

        queryset = UserReport.objects.filter(id=report.id)

        modeladmin = Mock()
        request = Mock()

        resolve_user_report(modeladmin, request, queryset)

        report.refresh_from_db()
        self.target_user.refresh_from_db()

        self.assertEqual(report.status, Status.ACCEPTED)
        self.assertEqual(self.target_user.status, VerificationStatus.BANNED)


class ResolveSpeedrunReportTest(BaseReportTestCase):
    def test_should_ban_user(self):
        speedrun = Speedrun.objects.create(
            url="https://example.com",
            time=123.45,
            date=timezone.now().date(),
            status=Status.PENDING,
            speedtrun_type=self.speedrun_type,
            user=self.target_user
        )

        report = SpeedrunReport.objects.create(
            target=speedrun,
            reporter=self.reporter_user,
            title="test",
            description="test",
            date=timezone.now(),
            status=Status.PENDING,
        )

        queryset = SpeedrunReport.objects.filter(id=report.id)

        modeladmin = Mock()
        request = Mock()

        resolve_speedrun_report(modeladmin, request, queryset)

        report.refresh_from_db()
        self.target_user.refresh_from_db()

        self.assertEqual(report.status, Status.ACCEPTED)
        self.assertEqual(self.target_user.status, VerificationStatus.BANNED)