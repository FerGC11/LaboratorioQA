from django.db import models


class Posiciones(models.Model):
    idPosicion = models.BigAutoField(primary_key=True)
    numeroPosicion = models.CharField(max_length=25, unique=True)
    fila = models.PositiveIntegerField()
    columna = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ("fila", "columna")
        constraints = [
            models.UniqueConstraint(fields=("fila", "columna"), name="posicion_unica_fila_columna")
        ]

    def __str__(self):
        return self.numeroPosicion


class Maquinas(models.Model):
    idMaquina = models.BigAutoField(primary_key=True)
    nombreGabinete = models.CharField(max_length=100)
    idProveedor = models.ForeignKey("pruebas.Proveedores", on_delete=models.PROTECT, related_name="maquinas")
    numeroSerie = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    idPosicion = models.ForeignKey(Posiciones, on_delete=models.PROTECT, related_name="maquinas")

    def __str__(self):
        return f"{self.nombreGabinete} ({self.numeroSerie})"


class JuegosMaquinas(models.Model):
    idJuegoMaquina = models.BigAutoField(primary_key=True)
    idJuego = models.ForeignKey("pruebas.Juegos", on_delete=models.CASCADE, related_name="juegos_maquinas")
    idMaquina = models.ForeignKey(Maquinas, on_delete=models.CASCADE, related_name="juegos_maquinas")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("idJuego", "idMaquina"), name="juego_unico_por_maquina")
        ]

    def __str__(self):
        return f"{self.idJuego} - {self.idMaquina}"