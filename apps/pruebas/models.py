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


class Juegos(ModeloCatalogo):
    idJuego = models.BigAutoField(primary_key=True)
    nombreJuego = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombreJuego


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


class Pruebas(models.Model):
    idPrueba = models.BigAutoField(primary_key=True)
    idEncargado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pruebas_encargadas",
    )
    idTipoPrueba = models.ForeignKey(
        TiposPruebas,
        on_delete=models.PROTECT,
        related_name="pruebas",
    )
    idResultado = models.ForeignKey(
        Resultados,
        on_delete=models.PROTECT,
        related_name="pruebas",
    )
    idEstado = models.ForeignKey(
        Estados,
        on_delete=models.PROTECT,
        related_name="pruebas",
    )
    observaciones = models.TextField(blank=True)
    fechaPuestaPunto = models.DateField(null=True, blank=True)
    fechaInicio = models.DateField(null=True, blank=True)
    fechaFin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Prueba {self.idPrueba}"


class PruebasMaquinas(models.Model):
    idPruebaMaquina = models.BigAutoField(primary_key=True)
    idPrueba = models.ForeignKey(
        Pruebas,
        on_delete=models.CASCADE,
        related_name="pruebas_maquinas",
    )
    idProveedor = models.ForeignKey(
        Proveedores,
        on_delete=models.PROTECT,
        related_name="pruebas_maquinas",
    )
    idJuego = models.ForeignKey(
        Juegos,
        on_delete=models.PROTECT,
        related_name="pruebas_maquinas",
    )
    idMaquina = models.ForeignKey(
        "maquinas.Maquinas",
        on_delete=models.PROTECT,
        related_name="pruebas_maquinas",
    )
    codigoPrueba = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.codigoPrueba


class PruebasAplicativos(models.Model):
    idPruebaAplicativo = models.BigAutoField(primary_key=True)
    idPrueba = models.ForeignKey(
        Pruebas,
        on_delete=models.CASCADE,
        related_name="pruebas_aplicativos",
    )
    idTipoAplicativo = models.ForeignKey(
        TiposAplicativos,
        on_delete=models.PROTECT,
        related_name="pruebas_aplicativos",
    )
    idDesarrollador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pruebas_desarrolladas",
    )
    codigoPrueba = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.codigoPrueba