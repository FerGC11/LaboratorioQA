from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pruebas", "0007_remove_pruebasaplicativos_numaprobado_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="pruebas",
            old_name="procentajeAvense",
            new_name="porcentajeAvance",
        ),
    ]
