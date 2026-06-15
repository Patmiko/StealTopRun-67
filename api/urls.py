from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicGameViewSet, PublicSpeedrunViewSet, PublicCategoryViewSet

router = DefaultRouter()
router.register(r'games', PublicGameViewSet, basename='public-games')
router.register(r'speedruns', PublicSpeedrunViewSet, basename='public-speedruns')
router.register(r'categories', PublicCategoryViewSet, basename='public-categories')

urlpatterns = [
    path('', include(router.urls)),
]