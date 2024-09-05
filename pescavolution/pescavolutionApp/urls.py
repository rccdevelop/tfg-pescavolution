from django.urls import path
from pescavolutionApp import views
from dash_apps import dashboard

urlpatterns = [
    path('',views.home, name="Inicio"),
    path('cargaDatos',views.cargaDatos, name="CargaDatos"),
    path('filtros',views.filtros, name="Filtros"),
]