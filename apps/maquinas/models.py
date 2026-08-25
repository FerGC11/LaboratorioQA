from django.db import models


# Create your models here.

class PosicionesLaboratorio(models.Model):
    idPosicion = models.IntegerField(primary_key=True)
    nombrePosicion = models.CharField(max_length=25)
    fila = models.IntegerField()
    columna = models.IntegerField()
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Posicion {self.idPosicion}"

class Maquinas(models.Model):
    idMaquina = models.IntegerField(primary_key=True)
    nombreMaquina = models.CharField(max_length=25)
    juego = models.CharField(max_length=30)
    activa = models.BooleanField(default=True)
    idPosicion = models.ForeignKey('PosicionesLaboratorio', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombreMaquina
