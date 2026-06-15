from django.shortcuts import render
from django.views import View


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

# ERROR HANDLING PATHS
# ===================================================================================================================


class PageNotFoundView(View):
    def get(self, request, *args, **kwargs):
        return render(request, '404.html', status=404)
