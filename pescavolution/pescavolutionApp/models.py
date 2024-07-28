from django.db import models

# Create your models here.

class VentasPesqueras(models.Model):
    fechaVenta = models.DateField()
    provincia = models.CharField(max_length=50)
    lonja = models.CharField(max_length=100)
    tipoEspecie = models.CharField(max_length=20)
    faoEspecie = models.CharField(max_length=3)
    nombreEspecie = models.CharField(max_length=100)
    totalKilos = models.DecimalField(max_digits=15, decimal_places=2)
    totalEuros = models.DecimalField(max_digits=15, decimal_places=2)
    idVenta = models.AutoField(primary_key=True)
    
    def __str__(self):
        cadena = self.fechaVenta + ', ' + self.lonja + ', ' + self.nombreEspecie + ', ' + self.totalKilos + ' kg, ' + self.totalEuros + ' €'
        return cadena
