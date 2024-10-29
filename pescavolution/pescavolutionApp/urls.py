from django.urls import path
from pescavolutionApp import views
from dash_apps import dashboard

urlpatterns = [
    path('',views.home, name="Inicio"),
    path('cargaDatos',views.cargaDatos, name="CargaDatos"),
    path('misFiltros/',views.misFiltros, name="Mis Filtros"),
    path('import_filter/', views.import_filter, name='import_filter'),
    path('export_filter/<int:filter_id>/', views.export_filter, name='export_filter'),
]