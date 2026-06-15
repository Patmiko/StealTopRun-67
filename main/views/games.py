from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Prefetch
from django.views import View
from ..models import Game, Speedrun, SpeedrunType, VerificationStatus
from ..forms import Category


class GamesView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', '').strip()

        if search_query:
            games = Game.objects.filter(name__icontains=search_query)
            grouped_games = None
        else:
            games = None
            categories = Category.objects.prefetch_related('game_set').all()

            grouped_games = {}
            for category in categories:
                category_games = category.game_set.all()

                if category_games.exists():
                    grouped_games[category.name] = category_games

        return render(request, 'games.html', {
            'games': games,
            'grouped_games': grouped_games,
            'search_term': search_query
        })


class GameDetailView(View):
    def get(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, pk=game_id)
        speedrun_types = game.speedrun_types.all()
        return render(request, 'game_detail.html', {'game': game, 'speedrun_types': speedrun_types})


class DiscoverView(View):
    def get(self, request, *args, **kwargs):
        one_week_ago = timezone.now().date() - timedelta(days=7)

        # Filter runs from the last 7 days
        recent_accepted_runs = Q(
            speedruns__status='ACCEPTED',
            speedruns__date__gte=one_week_ago,
            speedruns__user__status=VerificationStatus.VERIFIED)

        # Get the valid runs
        valid_runs = Prefetch(
            'speedruns',
            queryset=Speedrun.objects.filter(
                status='ACCEPTED',
                user__status=VerificationStatus.VERIFIED 
            ).select_related('user').order_by('time'),
            to_attr='top_runs'
        )

        # Get top 5 categories by runs
        top_categories = SpeedrunType.objects.select_related('game').annotate(
            recent_run_count=Count('speedruns', filter=recent_accepted_runs)
        ).filter(
            recent_run_count__gt=0 
        ).order_by('-recent_run_count').prefetch_related(valid_runs)[:5]

        return render(request, 'discover.html', {'top_categories': top_categories})
