from rest_framework import viewsets
from main.models import Game, Speedrun, Status
from .serializers import PublicGameSerializer, PublicSpeedrunSerializer

class PublicGameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public endpoint to view all registered games and their categories.
    """
    queryset = Game.objects.prefetch_related('categories').all()
    serializer_class = PublicGameSerializer

class PublicSpeedrunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public endpoint to view ACCEPTED speedruns.
    """
    serializer_class = PublicSpeedrunSerializer

    def get_queryset(self):
        return Speedrun.objects.filter(
            status=Status.ACCEPTED
        ).select_related('user', 'speedrun_type__game')