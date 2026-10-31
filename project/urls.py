from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("superuser/", admin.site.urls),
    path("", include("core.urls")),
    # path("webhook/", stripe_webhook, name="stripe_webhook"),
    path("payment/", include("payment.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
]
if settings.DEBUG:
    # urlpatterns += debug_toolbar_urls()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
