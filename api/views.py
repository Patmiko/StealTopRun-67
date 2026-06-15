from rest_framework import viewsets
from main.models import Game, Speedrun, Status, Category
from .serializers import PublicGameSerializer, PublicSpeedrunSerializer, PublicCategorySerializer


class PublicGameViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicGameSerializer

    def get_queryset(self):
        queryset = Game.objects.prefetch_related('categories').all()

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id).distinct()

        return queryset


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


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public endpoint to view all speedrun categories.
    """
    queryset = Category.objects.all()
    serializer_class = PublicCategorySerializer
