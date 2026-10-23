from urllib.parse import parse_qs, urlsplit

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.maquinas.models import Maquinas, Posiciones
from apps.usuarios.models import Usuario
from .models import (Estados, FamiliasJuegos, Protocolo, Proveedores, Proyectos,
                     Pruebas, PruebasAplicativos, PruebasMaquinas, TipoJuego,
                     TiposAplicativos, TiposPruebas)


class EstadisticasCategoriasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create(username="qa")
        estado = Estados.objects.create(nombreEstado="En curso")
        tipo = TiposPruebas.objects.create(nombreTipoPrueba="Prueba")
        cls.proyecto = Proyectos.objects.create(nombreProyecto="Proyecto A")
        tipo_app = TiposAplicativos.objects.create(nombreTipoAplicativo="Web")
        cls.prueba_app = Pruebas.objects.create(
            idEncargado=cls.usuario, idEstado=estado, idTipoPrueba=tipo,
            fechaPuestaPunto=timezone.localdate(), numAprobado=3, numCasosPrueba=5)
        PruebasAplicativos.objects.create(
            idPrueba=cls.prueba_app, idProyecto=cls.proyecto, idTipoAplicativo=tipo_app,
            codigoPrueba="APP-1", nombrePrueba="Prueba aplicativo")
        cls.protocolo = Protocolo.objects.create(nombreProtocolo="Protocolo A")
        familia = FamiliasJuegos.objects.create(nombreFamilia="Familia A")
        tipo_juego = TipoJuego.objects.create(nombre="Juego A")
        posicion = Posiciones.objects.create(numeroPosicion="1", fila=1, columna=1)
        proveedor = Proveedores.objects.create(nombreProveedor="Proveedor A")
        maquina = Maquinas.objects.create(nombreGabinete="Gabinete A", numeroSerie="SERIE-1",
                                          idProveedor=proveedor, idPosicion=posicion)
        cls.prueba_maquina = Pruebas.objects.create(
            idEncargado=cls.usuario, idEstado=estado, idTipoPrueba=tipo,
            fechaPuestaPunto=timezone.localdate(), numAprobado=7, numCasosPrueba=10)
        PruebasMaquinas.objects.create(
            idPrueba=cls.prueba_maquina, idFamilia=familia, idTipoJuego=tipo_juego,
            idMaquina=maquina, idProtocolo=cls.protocolo, codigoPrueba="MAQ-1",
            versionSistemaCaja="1", versionNexus="1")

    def consultar(self, **params):
        return self.client.get(reverse("pruebas:EstadisticasPruebas"), params)

    def test_generales_conserva_datos_y_filtros_actuales(self):
        response = self.consultar()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], 2)
        self.assertEqual(response.context["casos_resultado"][0]["total"], 10)
        self.assertIn("tipo", response.context["formulario_filtro"].fields)
        self.assertContains(response, "statistics-dashboard")

    def test_cada_categoria_separa_tarjetas_graficas_y_detalle(self):
        for categoria, codigo, aprobados in (("aplicativos", "APP-1", 3), ("maquinas", "MAQ-1", 7)):
            with self.subTest(categoria=categoria):
                response = self.consultar(categoria=categoria)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["total"], 1)
                self.assertEqual(response.context["meses"][0]["total"], 1)
                self.assertEqual(response.context["estados"][0]["total"], 1)
                self.assertEqual(response.context["responsables"][0]["total"], 1)
                self.assertEqual(response.context["casos_resultado"][0]["total"], aprobados)
                self.assertEqual([p["codigo"] for p in response.context["detalle_pruebas"]], [codigo])
                self.assertContains(response, 'name="categoria" value="' + categoria + '"')

    def test_filtros_especificos_y_parametros_ajenos(self):
        response = self.consultar(categoria="aplicativos", proyecto=self.proyecto.pk, protocolo="invalido")
        self.assertEqual(response.context["total"], 1)
        self.assertIn("proyecto", response.context["formulario_filtro"].fields)
        self.assertNotIn("protocolo", response.context["formulario_filtro"].fields)
        response = self.consultar(categoria="maquinas", protocolo=self.protocolo.pk)
        self.assertEqual(response.context["total"], 1)
        self.assertIn("protocolo", response.context["formulario_filtro"].fields)
        self.assertNotIn("proyecto", response.context["formulario_filtro"].fields)
        response = self.consultar(categoria="maquinas", protocolo=999999)
        self.assertEqual(response.context["total"], 0)
        self.assertIn("protocolo", response.context["formulario_filtro"].errors)

    def test_detalle_y_cambio_de_categoria_conservan_contexto(self):
        response = self.consultar(categoria="maquinas", protocolo=self.protocolo.pk,
                                  encargado=self.usuario.pk, detalle=self.prueba_maquina.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("categoria=maquinas", response.context["querystring_filtros"])
        for opcion in response.context["opciones_estadisticas"]:
            destino = self.client.get(reverse("pruebas:EstadisticasPruebas") + opcion["url"])
            self.assertFalse(destino.context["mostrar_filtros"])
            self.assertContains(destino, 'id="statistics-filters" hidden')
            params = parse_qs(urlsplit(opcion["url"]).query)
            self.assertEqual(params["encargado"], [str(self.usuario.pk)])
            self.assertNotIn("protocolo", params)
            self.assertNotIn("detalle", params)
        self.assertEqual(self.consultar(categoria="maquinas", detalle=self.prueba_app.pk).status_code, 404)

    def test_fechas_invalidas_y_categoria_desconocida(self):
        response = self.consultar(fecha_desde="2026-10-20", fecha_hasta="2026-10-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], 0)
        self.assertIn("fecha_hasta", response.context["formulario_filtro"].errors)
        response = self.consultar(categoria="desconocida")
        self.assertEqual(response.context["categoria"], "generales")
        self.assertEqual(response.context["total"], 2)

    def test_nombre_maquina_registro_consulta_y_estadisticas(self):
        registro = PruebasMaquinas.objects.get(idPrueba=self.prueba_maquina)
        datos = {
            "codigoPrueba": "MAQ-NUEVA", "nombreJuego": "Prueba de gabinete",
            "idFamilia": registro.idFamilia_id, "idMaquina": registro.idMaquina_id,
            "idTipoJuego": registro.idTipoJuego_id, "idProtocolo": registro.idProtocolo_id,
            "versionSistemaCaja": "1", "versionNexus": "1",
            "idEncargado": self.usuario.pk, "idEstado": self.prueba_maquina.idEstado_id,
            "fechaPuestaPunto": timezone.localdate().isoformat(),
        }
        url = reverse("pruebas:PruebasMaquinas")
        response = self.client.post(url, datos)
        self.assertEqual(response.status_code, 302)
        nuevo = PruebasMaquinas.objects.get(codigoPrueba="MAQ-NUEVA")
        self.assertEqual(nuevo.nombreJuego, "Prueba de gabinete")
        response = self.client.get(url, {"nombreJuego": "gabinete"})
        self.assertContains(response, "Prueba de gabinete")
        self.assertEqual(list(response.context["pruebas_maquinas"]), [nuevo])
        for categoria in ("generales", "maquinas"):
            response = self.consultar(categoria=categoria)
            detalle = next(p for p in response.context["detalle_pruebas"] if p["id"] == nuevo.idPrueba_id)
            self.assertEqual(detalle["nombre"], nuevo.nombreJuego)
        response = self.consultar(categoria="maquinas", detalle=nuevo.idPrueba_id)
        self.assertContains(response, "Prueba de gabinete")

    def test_editar_nombre_maquina_sin_crear_otra_prueba(self):
        registro = PruebasMaquinas.objects.get(idPrueba=self.prueba_maquina)
        registro.nombreJuego = "Nombre original"
        registro.save()
        url = reverse("pruebas:PruebasMaquinas")
        response = self.client.get(url, {"editar": registro.pk})
        self.assertContains(response, "Nombre original")
        datos = {
            "accion": "editar", "idPruebaMaquina": registro.pk,
            "nombreJuego": "Nombre actualizado", "idEstado": self.prueba_maquina.idEstado_id,
            "numAprobado": 7, "numNoAprobado": 0, "numAprobadoMenos": 0, "numCasosPrueba": 10,
            "fechaPuestaPunto": timezone.localdate().isoformat(),
        }
        total = Pruebas.objects.count()
        response = self.client.post(url, datos)
        self.assertEqual(response.status_code, 302)
        registro.refresh_from_db()
        self.assertEqual(registro.nombreJuego, "Nombre actualizado")
        self.assertEqual(Pruebas.objects.count(), total)
        datos["nombreJuego"] = "x" * 151
        response = self.client.post(url, datos)
        self.assertEqual(response.status_code, 200)
        self.assertIn("nombreJuego", response.context["formulario_edicion"].errors)
        registro.refresh_from_db()
        self.assertEqual(registro.nombreJuego, "Nombre actualizado")

    def test_generales_compara_pruebas_por_categoria_con_filtros(self):
        response = self.consultar(categoria="generales")
        self.assertEqual([dato["total"] for dato in response.context["pruebas_por_categoria"]], [1, 1])
        self.assertNotContains(response, "Resultados de casos")
        self.assertContains(response, "Pruebas por categor\u00eda")
        self.prueba_maquina.fechaPuestaPunto = timezone.localdate() - timezone.timedelta(days=60)
        self.prueba_maquina.save()
        response = self.consultar(categoria="generales")
        self.assertEqual([dato["total"] for dato in response.context["pruebas_por_categoria"]], [1, 0])
        response = self.consultar(categoria="generales", encargado=999999)
        self.assertEqual([dato["total"] for dato in response.context["pruebas_por_categoria"]], [0, 0])
        self.assertContains(self.consultar(categoria="aplicativos"), "Resultados de casos")
        self.assertNotContains(self.consultar(categoria="maquinas"), "Resultados de casos")

    def test_graficas_maquinas_agrupadas_y_filtradas(self):
        response = self.consultar(categoria="maquinas")
        for clave, nombre in (("tipos_juego_estadisticas", "Juego A"),
                              ("proveedores_estadisticas", "Proveedor A"),
                              ("protocolos_estadisticas", "Protocolo A")):
            self.assertEqual(response.context[clave][0]["nombre"], nombre)
            self.assertEqual(response.context[clave][0]["total"], 1)
            self.assertEqual(response.context[clave][0]["porcentaje"], 100)
        self.assertEqual(response.context["total_protocolos"], 1)
        self.assertContains(response, "Pruebas por tipo de juego")
        self.assertContains(response, "Pruebas por proveedor")
        self.assertContains(response, "stats-provider-chart")
        self.assertContains(response, "Pruebas por protocolo")
        self.assertNotContains(self.consultar(categoria="generales"), "Pruebas por proveedor")
        self.assertNotContains(self.consultar(categoria="aplicativos"), "Pruebas por protocolo")
        registro = PruebasMaquinas.objects.get(idPrueba=self.prueba_maquina)
        registro.idProtocolo = None
        registro.save()
        response = self.consultar(categoria="maquinas")
        self.assertEqual(response.context["protocolos_estadisticas"][0]["nombre"], "Sin protocolo")
        response = self.consultar(categoria="maquinas", protocolo=self.protocolo.pk)
        for clave in ("tipos_juego_estadisticas", "proveedores_estadisticas", "protocolos_estadisticas"):
            self.assertEqual(response.context[clave], [])
        self.assertEqual(response.context["total_protocolos"], 0)

    def test_graficas_aplicativos_proyectos_y_tipos(self):
        response = self.consultar(categoria="aplicativos")
        self.assertContains(response, "Pruebas por proyecto")
        self.assertContains(response, "Pruebas por tipo de aplicativo")
        self.assertContains(response, "machine-charts-grid")
        self.assertEqual(response.context["proyectos_estadisticas"][0]["nombre"], "Proyecto A")
        self.assertEqual(response.context["proyectos_estadisticas"][0]["total"], 1)
        self.assertEqual(response.context["tipos_aplicativo_estadisticas"][0]["nombre"], "Web")
        self.assertEqual(response.context["tipos_aplicativo_estadisticas"][0]["porcentaje"], 100)
        self.assertEqual(response.context["total_tipos_aplicativo"], 1)
        self.assertNotContains(self.consultar(categoria="generales"), "Pruebas por proyecto")
        self.assertNotContains(self.consultar(categoria="maquinas"), "Pruebas por tipo de aplicativo")
        response = self.consultar(categoria="aplicativos", proyecto=999999)
        self.assertEqual(response.context["proyectos_estadisticas"], [])
        self.assertEqual(response.context["tipos_aplicativo_estadisticas"], [])
        self.assertEqual(response.context["total_tipos_aplicativo"], 0)

    def test_filtro_resultado_y_grafica_por_categoria(self):
        from .models import Resultados
        aprobado = Resultados.objects.create(nombreResultado="Aprobado")
        self.prueba_app.idResultado = aprobado
        self.prueba_app.save()
        for categoria in ("generales", "maquinas", "aplicativos"):
            response = self.consultar(categoria=categoria, resultado=aprobado.pk)
            self.assertIn("resultado", response.context["formulario_filtro"].fields)
            self.assertEqual(response.context["total"], 0 if categoria == "maquinas" else 1)
            for opcion in response.context["opciones_estadisticas"]:
                self.assertEqual(parse_qs(urlsplit(opcion["url"]).query)["resultado"], [str(aprobado.pk)])
        for categoria, nombre in (("maquinas", "Pendiente"), ("aplicativos", "Aprobado")):
            response = self.consultar(categoria=categoria)
            self.assertContains(response, "Pruebas por resultado")
            self.assertNotContains(response, "Pruebas por responsable")
            self.assertEqual(response.context["resultados_estadisticas"][0]["nombre"], nombre)
            self.assertEqual(response.context["resultados_estadisticas"][0]["total"], 1)
        self.assertContains(self.consultar(categoria="generales"), "Pruebas por responsable")

    def test_generales_casos_y_resultados_de_ambas_categorias(self):
        response = self.consultar(categoria="generales")
        self.assertContains(response, "Casos resueltos")
        self.assertContains(response, "Pruebas por resultado")
        self.assertContains(response, "machine-charts-grid")
        self.assertEqual(response.context["casos_resultado"][0]["total"], 10)
        self.assertEqual(response.context["resultados_estadisticas"][0]["total"], 2)
        self.prueba_maquina.fechaPuestaPunto = timezone.localdate() - timezone.timedelta(days=60)
        self.prueba_maquina.save()
        response = self.consultar(categoria="generales")
        self.assertEqual(response.context["casos_resultado"][0]["total"], 3)
        self.assertEqual(response.context["resultados_estadisticas"][0]["total"], 1)

    def test_porcentaje_aprobado_calculo_y_actualizacion(self):
        from decimal import Decimal
        prueba = self.prueba_maquina
        prueba.refresh_from_db()
        self.assertEqual(prueba.porcentajeAprobado, Decimal("70.00"))
        prueba.numAprobado = 1
        prueba.numCasosPrueba = 3
        prueba.save(update_fields=["numAprobado", "numCasosPrueba"])
        prueba.refresh_from_db()
        self.assertEqual(prueba.porcentajeAprobado, Decimal("33.33"))
        prueba.numAprobado = 0
        prueba.numCasosPrueba = 0
        prueba.save(update_fields=["numAprobado", "numCasosPrueba"])
        prueba.refresh_from_db()
        self.assertEqual(prueba.porcentajeAprobado, Decimal("0.00"))

    def test_porcentaje_aprobado_en_tablas_y_modal(self):
        for ruta, porcentaje in (("PruebasMaquinas", "70.00%"), ("PruebasAplicativos", "60.00%")):
            response = self.client.get(reverse("pruebas:" + ruta))
            self.assertContains(response, "Aprobado (%)")
            self.assertContains(response, porcentaje)
        response = self.consultar(categoria="generales", detalle=self.prueba_maquina.pk)
        self.assertContains(response, "Porcentaje aprobado")
        self.assertContains(response, "70.00%")
        detalle = next(p for p in response.context["detalle_pruebas"] if p["id"] == self.prueba_maquina.pk)
        self.assertEqual(float(detalle["porcentaje_aprobado"]), 70)
