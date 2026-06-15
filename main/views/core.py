from django.shortcuts import render
from django.views import View


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')
    
class ContactView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'contact.html')

# ERROR HANDLING PATHS
# ===================================================================================================================


class PageNotFoundView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'errors/404.html', status=404)
    
class ServerErrorView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'errors/500.html', status=500)
    
class PermissionDeniedView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'errors/403.html', status=403)
    
class BadRequestView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'errors/400.html', status=400)
