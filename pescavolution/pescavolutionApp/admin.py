from django.contrib import admin
from .models import FiltroUsuario

# Registrar el modelo FiltroUsuario para que pueda ser gestionado por el admin
admin.site.register(FiltroUsuario)
