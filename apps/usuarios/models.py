from django.contrib.auth.models import AbstractUser
from django.db import models


class Cargos(models.Model):
    idCargo = models.BigAutoField(primary_key=True)
    nombreCargo = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreCargo


class Areas(models.Model):
    idArea = models.BigAutoField(primary_key=True)
    nombreArea = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombreArea


class Usuario(AbstractUser):
    apellidoMaterno = models.CharField(max_length=150, blank=True)
    idCargo = models.ForeignKey(
        Cargos,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    idArea = models.ForeignKey(
        Areas,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    activo = models.BooleanField(default=True)