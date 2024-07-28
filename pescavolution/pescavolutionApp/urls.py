from django.urls import path
from pescavolutionApp import views

urlpatterns = [
    path('',views.home, name="Inicio"),
    path('cargaDatos',views.cargaDatos, name="CargaDatos"),
]