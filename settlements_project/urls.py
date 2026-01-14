from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('settlements/', include('settlements.urls')),
    path('', RedirectView.as_view(url='/settlements/')),
]
