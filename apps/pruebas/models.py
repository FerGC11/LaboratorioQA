from decimal import Decimal

from django.conf import settings
from django.db import models


class ModeloCatalogo(models.Model):
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Proveedores(ModeloCatalogo):
    idProveedor = models.BigAutoField(primary_key=True)
    nombreProveedor = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombreProveedor


class TipoJuego(ModeloCatalogo):
    idTipoJuego = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Protocolo(ModeloCatalogo):
    idProtocolo = models.BigAutoField(primary_key=True)
    nombreProtocolo = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Protocolo"
        verbose_name_plural = "Protocolos"
        ordering = ["nombreProtocolo"]

    def __str__(self):
        return self.nombreProtocolo


class FamiliasJuegos(ModeloCatalogo):
    idFamilia = models.BigAutoField(primary_key=True)
    nombreFamilia = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombreFamilia


class Juegos(ModeloCatalogo):
    idJuego = models.BigAutoField(primary_key=True)
    idFamilia = models.ForeignKey(FamiliasJuegos, on_delete=models.PROTECT, related_name="juegos")
    nombreJuego = models.CharField(max_length=120)
    version = models.CharField(max_length=80)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("idFamilia", "nombreJuego", "version"), name="juego_unico_por_familia_version")
        ]

    def __str__(self):
        return f"{self.nombreJuego} {self.version}"


class TiposPruebas(ModeloCatalogo):
    idTipoPrueba = models.BigAutoField(primary_key=True)
    nombreTipoPrueba = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombreTipoPrueba


class Estados(ModeloCatalogo):
    idEstado = models.BigAutoField(primary_key=True)
    nombreEstado = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nombreEstado


class Resultados(ModeloCatalogo):
    idResultado = models.BigAutoField(primary_key=True)
    nombreResultado = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nombreResultado


class TiposAplicativos(ModeloCatalogo):
    idTipoAplicativo = models.BigAutoField(primary_key=True)
    nombreTipoAplicativo = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombreTipoAplicativo


class Proyectos(ModeloCatalogo):
    idProyecto = models.BigAutoField(primary_key=True)
    nombreProyecto = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombreProyecto


class Pruebas(models.Model):
    idPrueba = models.BigAutoField(primary_key=True)
    idEncargado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pruebas_encargadas")
    idTipoPrueba = models.ForeignKey(TiposPruebas, on_delete=models.PROTECT, related_name="pruebas")
    idResultado = models.ForeignKey(Resultados, on_delete=models.PROTECT, related_name="pruebas", null=True)
    idEstado = models.ForeignKey(Estados, on_delete=models.PROTECT, related_name="pruebas")
    observaciones = models.TextField(blank=True, null=True)
    fechaPuestaPunto = models.DateField(null=True, blank=True)
    fechaInicio = models.DateField(null=True, blank=True)
    fechaFin = models.DateField(null=True, blank=True)
    documentoPruebas = models.URLField(max_length=500, null=True, blank=True)
    numAprobado = models.PositiveIntegerField(default=0)
    numNoAprobado = models.PositiveIntegerField(default=0)
    numAprobadoMenos = models.PositiveIntegerField(default=0)
    numCasosPrueba = models.PositiveIntegerField(default=0)
    porcentajeAvance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    porcentajeAprobado = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if update_fields is None or {"numAprobado", "numCasosPrueba", "porcentajeAprobado"}.intersection(update_fields):
            self.porcentajeAprobado = (
                Decimal(self.numAprobado or 0) * Decimal("100") / Decimal(self.numCasosPrueba)
                if self.numCasosPrueba else Decimal("0")
            ).quantize(Decimal("0.01"))
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"porcentajeAprobado"}
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Prueba {self.idPrueba}"

class PruebasMaquinas(models.Model):
    idPruebaMaquina = models.BigAutoField(primary_key=True)
    idPrueba = models.ForeignKey(Pruebas, on_delete=models.CASCADE, related_name="pruebas_maquinas")
    idFamilia = models.ForeignKey(FamiliasJuegos, on_delete=models.PROTECT, related_name="pruebas_maquinas")
    idMaquina = models.ForeignKey("maquinas.Maquinas", on_delete=models.PROTECT, related_name="pruebas_maquinas")
    idProveedor = models.ForeignKey(Proveedores, on_delete=models.PROTECT, related_name="pruebas_maquinas", null=True, blank=True)
    codigoPrueba = models.CharField(max_length=100, unique=True)
    idTipoJuego = models.ForeignKey(TipoJuego, on_delete=models.PROTECT, related_name="pruebas_maquinas")
    idProtocolo = models.ForeignKey(Protocolo, on_delete=models.PROTECT, related_name="pruebas_maquinas", null=True, blank=True)
    versionSistemaCaja = models.CharField(max_length=100)
    versionNexus = models.CharField(max_length=100)
    nombreJuego = models.CharField(max_length=150, null=True, blank=True)

    @property
    def proveedor(self):
        return self.idProveedor or self.idMaquina.idProveedor

    def __str__(self):
        return self.codigoPrueba


class PruebasAplicativos(models.Model):
    idPruebaAplicativo = models.BigAutoField(primary_key=True)
    idPrueba = models.ForeignKey(Pruebas, on_delete=models.CASCADE, related_name="pruebas_aplicativos")
    idTipoAplicativo = models.ForeignKey(TiposAplicativos, on_delete=models.PROTECT, related_name="pruebas_aplicativos")
    idProyecto = models.ForeignKey(Proyectos, on_delete=models.PROTECT, related_name="pruebas_aplicativos")
    codigoPrueba = models.CharField(max_length=100, unique=True)
    nombrePrueba = models.CharField(max_length=150, null=True, blank=True)
    versionAplicacion = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.codigoPrueba
