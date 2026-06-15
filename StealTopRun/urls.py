from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main.views.core import BadRequestView, PageNotFoundView, PermissionDeniedView, ServerErrorView

urlpatterns = [
    # Admin Site
    path('admin/', admin.site.urls),
    # Main App
    path('', include('main.urls')),
    # API Endpoints (Read ONLY)
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = PageNotFoundView.as_view()
handler500 = ServerErrorView.as_view()
handler403 = PermissionDeniedView.as_view()
handler400 = BadRequestView.as_view()