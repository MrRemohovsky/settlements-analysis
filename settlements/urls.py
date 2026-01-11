from django.urls import path
from . import views

app_name = 'settlements'

urlpatterns = [
    path('', views.StatsView.as_view(), name='stats'),
    path('regions/<str:region_name>/', views.RegionDetailView.as_view(), name='region'),
    path('regions/<str:region_name>/<str:municipality_name>/', views.MunicipalityDetailView.as_view(), name='municipality'),
]
