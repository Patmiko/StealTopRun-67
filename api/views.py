from rest_framework import viewsets
from main.models import Game, Speedrun, Status
from .serializers import PublicGameSerializer, PublicSpeedrunSerializer


class PublicGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.prefetch_related('categories').all()
    serializer_class = PublicGameSerializer


class PublicSpeedrunViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicSpeedrunSerializer

    def get_queryset(self):
        queryset = Speedrun.objects.filter(
            status=Status.ACCEPTED
        ).select_related('user', 'speedrun_type__game')

        game_id = self.request.query_params.get('game')
        if game_id:
            queryset = queryset.filter(speedrun_type__game_id=game_id)

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(speedrun_type_id=category_id)

        return queryset