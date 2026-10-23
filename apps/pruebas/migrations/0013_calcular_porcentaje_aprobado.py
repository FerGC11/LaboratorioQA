from decimal import Decimal

from django.db import migrations


def calcular_porcentajes(apps, schema_editor):
    Pruebas = apps.get_model("pruebas", "Pruebas")
    registros = Pruebas.objects.using(schema_editor.connection.alias)
    for prueba in registros.all().iterator():
        porcentaje = (
            Decimal(prueba.numAprobado or 0) * Decimal("100") / Decimal(prueba.numCasosPrueba)
            if prueba.numCasosPrueba else Decimal("0")
        ).quantize(Decimal("0.01"))
        registros.filter(pk=prueba.pk).update(porcentajeAprobado=porcentaje)


class Migration(migrations.Migration):
    dependencies = [("pruebas", "0012_pruebas_porcentajeaprobado")]
    operations = [migrations.RunPython(calcular_porcentajes, migrations.RunPython.noop)]
