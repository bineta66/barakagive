from django.conf import settings
from django.conf.urls.static import static
from config.urls import urlpatterns as project_urlpatterns

# Model the DEBUG media fallback even when this test suite starts with DEBUG=False.
urlpatterns = project_urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
