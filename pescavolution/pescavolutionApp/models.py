from django.db import models
from django.contrib.auth.models import User


# Modelo para trabajar con los diferentes dashboards que guarda el usuario
class FiltroUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) #Usuario del filtro
    nombreFiltro = models.CharField(max_length=100)  # Nombre del filtro
    datosFiltro = models.JSONField()  # Guardar los diferentes parametros del filtro

    def __str__(self):
        return self.nombreFiltro