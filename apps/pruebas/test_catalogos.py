from django.test import Client, TestCase
from django.urls import reverse

from .catalogos import CATALOGOS
from .models import FamiliasJuegos, Juegos, Proveedores


class CatalogosTests(TestCase):
    def url(self, slug="proveedores"):
        return reverse("pruebas:Catalogo", args=[slug])

    def test_navegacion_y_todos_los_catalogos(self):
        self.assertContains(self.client.get(reverse("inicio")), reverse("pruebas:DetallesGenerales"))
        self.assertEqual(self.client.get(reverse("pruebas:DetallesGenerales")).status_code, 200)
        for slug, (titulo, _, _) in CATALOGOS.items():
            with self.subTest(catalogo=slug):
                response = self.client.get(self.url(slug))
                self.assertContains(response, titulo)
                self.assertEqual(len(response.context["catalogos"]), 15)

    def test_agregar_editar_y_desactivar_sin_duplicar(self):
        response = self.client.post(self.url(), {"nombreProveedor": "Nuevo", "activo": "on"})
        self.assertRedirects(response, self.url() + "?guardado=1")
        registro = Proveedores.objects.get(nombreProveedor="Nuevo")
        response = self.client.get(self.url(), {"editar": registro.pk})
        self.assertEqual(response.context["formulario"].instance, registro)
        response = self.client.post(self.url(), {"registro_id": registro.pk, "nombreProveedor": "Editado"})
        self.assertEqual(response.status_code, 302)
        registro.refresh_from_db()
        self.assertEqual(registro.nombreProveedor, "Editado")
        self.assertFalse(registro.activo)
        self.assertEqual(Proveedores.objects.count(), 1)

    def test_duplicados_requeridos_y_relaciones_invalidas(self):
        Proveedores.objects.create(nombreProveedor="Existente")
        response = self.client.post(self.url(), {"nombreProveedor": "Existente", "activo": "on"})
        self.assertIn("nombreProveedor", response.context["formulario"].errors)
        response = self.client.post(self.url(), {"activo": "on"})
        self.assertIn("nombreProveedor", response.context["formulario"].errors)
        response = self.client.post(self.url("juegos"), {"nombreJuego": "Juego", "version": "1", "idFamilia": 9999})
        self.assertIn("idFamilia", response.context["formulario"].errors)
        self.assertEqual(Juegos.objects.count(), 0)

    def test_juegos_relacion_y_unicidad_compuesta(self):
        familia = FamiliasJuegos.objects.create(nombreFamilia="Familia buscable")
        datos = {"nombreJuego": "Juego A", "idFamilia": familia.pk, "version": "1", "activo": "on"}
        self.assertEqual(self.client.post(self.url("juegos"), datos).status_code, 302)
        juego = Juegos.objects.get()
        self.assertEqual(juego.idFamilia, familia)
        response = self.client.post(self.url("juegos"), datos)
        self.assertTrue(response.context["formulario"].non_field_errors())
        self.assertEqual(Juegos.objects.count(), 1)
        response = self.client.get(self.url("juegos"), {"q": "buscable"})
        self.assertEqual(response.context["pagina"].paginator.count, 1)

    def test_busqueda_estado_y_paginacion(self):
        Proveedores.objects.bulk_create([Proveedores(nombreProveedor=f"Proveedor {i}") for i in range(30)])
        Proveedores.objects.create(nombreProveedor="Desactivado", activo=False)
        response = self.client.get(self.url(), {"pagina": 2})
        self.assertEqual(response.context["pagina"].number, 2)
        self.assertEqual(len(response.context["filas"]), 6)
        response = self.client.get(self.url(), {"q": "desactivado", "activo": "0"})
        self.assertEqual(response.context["pagina"].paginator.count, 1)
        response = self.client.get(self.url(), {"q": "desactivado", "activo": "1"})
        self.assertEqual(response.context["pagina"].paginator.count, 0)

    def test_limites_rutas_csrf_y_escape(self):
        self.assertEqual(self.client.get(self.url("usuarios")).status_code, 404)
        self.assertEqual(self.client.get(self.url(), {"editar": "invalido"}).status_code, 404)
        self.assertEqual(self.client.post(self.url(), {"registro_id": 9999}).status_code, 404)
        self.assertEqual(self.client.delete(self.url()).status_code, 405)
        self.assertEqual(Client(enforce_csrf_checks=True).post(self.url(), {"nombreProveedor": "Sin csrf"}).status_code, 403)
        Proveedores.objects.create(nombreProveedor="<script>alert(1)</script>")
        response = self.client.get(self.url())
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
