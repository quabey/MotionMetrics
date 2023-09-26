from django.urls import path
from .views import FileUploadView


urlpatterns = [
    path('plot-csv/', FileUploadView.as_view(), name='plot-csv'),
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
