from django import forms

from apps.maquinas.models import Maquinas
from apps.usuarios.models import Usuario
from .models import (Estados, FamiliasJuegos, Protocolo, Proyectos, PruebasAplicativos,
    PruebasMaquinas, Resultados, TipoJuego, TiposAplicativos, TiposPruebas)


class FormularioBasePrueba(forms.Form):
    idEncargado = forms.ModelChoiceField(label="Encargado", queryset=Usuario.objects.none())
    idEstado = forms.ModelChoiceField(label="Estado", queryset=Estados.objects.none())
    fechaPuestaPunto = forms.DateField(label="Fecha de puesta a punto", required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idEncargado"].queryset = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["idEstado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Seleccionar"

class FormularioPruebaMaquina(FormularioBasePrueba):
    codigoPrueba = forms.CharField(label="Código de prueba", max_length=100)
    nombreJuego = forms.CharField(label="Nombre de la prueba", max_length=150, required=False)
    idFamilia = forms.ModelChoiceField(label="Familia de juego", queryset=FamiliasJuegos.objects.none())
    idMaquina = forms.ModelChoiceField(label="Gabinete", queryset=Maquinas.objects.none())
    idTipoJuego = forms.ModelChoiceField(label="Tipo de juego", queryset=TipoJuego.objects.none())
    idProtocolo = forms.ModelChoiceField(label="Protocolo", queryset=Protocolo.objects.none())
    versionSistemaCaja = forms.CharField(label="Versión del sistema de caja", max_length=100)
    versionNexus = forms.CharField(label="Versión Nexus", max_length=100)
    idResultado = forms.ModelChoiceField(label="Resultado", required=False, queryset=Resultados.objects.none())
    fechaInicio = forms.DateField(label="Fecha de inicio", required=False, input_formats=["%Y-%m-%d"], widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    fechaFin = forms.DateField(label="Fecha de finalización", required=False, input_formats=["%Y-%m-%d"], widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    fechaPuestaPunto = forms.DateField(label="Fecha de puesta a punto", required=False, input_formats=["%Y-%m-%d"], widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    numAprobado = forms.IntegerField(label="Aprobados", min_value=0, required=False, initial=0)
    numNoAprobado = forms.IntegerField(label="No aprobados", min_value=0, required=False, initial=0)
    numAprobadoMenos = forms.IntegerField(label="Aprobados menos", min_value=0, required=False, initial=0)
    numCasosPrueba = forms.IntegerField(label="Casos de prueba", min_value=0, required=False, initial=0)
    documentoPruebas = forms.URLField(
        label="Enlace al documento de pruebas",
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://ejemplo.com/documento"}),
    )
    observaciones = forms.CharField(label="Observaciones", required=False, widget=forms.Textarea(attrs={"rows": 3}))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idResultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["idResultado"].empty_label = "Pendiente"
        self.fields["idFamilia"].queryset = FamiliasJuegos.objects.filter(activo=True).order_by("nombreFamilia")
        self.fields["idMaquina"].queryset = Maquinas.objects.filter(activo=True).order_by("nombreGabinete")
        self.fields["idProtocolo"].queryset = Protocolo.objects.filter(activo=True).order_by("nombreProtocolo")
        self.fields["idTipoJuego"].queryset = TipoJuego.objects.filter(activo=True).order_by("nombre")
        for name in ("idFamilia", "idMaquina", "idTipoJuego", "idProtocolo"):
            self.fields[name].empty_label = "Seleccionar"

    def clean_codigoPrueba(self):
        codigo = self.cleaned_data["codigoPrueba"].strip()
        if PruebasMaquinas.objects.filter(codigoPrueba__iexact=codigo).exists():
            raise forms.ValidationError("Ya existe una prueba con este código.")
        return codigo


    def clean(self):
        data = super().clean()
        inicio, fin = data.get("fechaInicio"), data.get("fechaFin")
        if inicio and fin and fin < inicio:
            self.add_error("fechaFin", "La fecha de finalización no puede ser anterior al inicio.")
        for campo in ("numAprobado", "numNoAprobado", "numAprobadoMenos", "numCasosPrueba"):
            if campo in data:
                data[campo] = data[campo] or 0
        total = data.get("numCasosPrueba", 0)
        ejecutados = sum(data.get(campo, 0) for campo in ("numAprobado", "numNoAprobado", "numAprobadoMenos"))
        if ejecutados > total:
            raise forms.ValidationError("La suma de aprobados, no aprobados y aprobados menos no puede superar el total de casos de prueba.")
        return data


class FormularioPruebaAplicativo(FormularioBasePrueba):
    codigoPrueba = forms.CharField(label="Código de prueba", max_length=100)
    nombrePrueba = forms.CharField(label="Nombre de la prueba", max_length=150, required=False)
    versionAplicacion = forms.CharField(label="Versión de la aplicación", max_length=100, required=False)
    idTipoAplicativo = forms.ModelChoiceField(label="Tipo de aplicativo", queryset=TiposAplicativos.objects.none())
    idProyecto = forms.ModelChoiceField(label="Proyecto", queryset=Proyectos.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields((
            "codigoPrueba",
            "nombrePrueba",
            "idProyecto",
            "idTipoAplicativo",
            "versionAplicacion",
            "idEncargado",
            "idEstado",
            "fechaPuestaPunto",
        ))
        self.fields["idTipoAplicativo"].queryset = TiposAplicativos.objects.filter(activo=True).order_by("nombreTipoAplicativo")
        self.fields["idProyecto"].queryset = Proyectos.objects.filter(activo=True).order_by("nombreProyecto")
        self.fields["idTipoAplicativo"].empty_label = "Seleccionar"
        self.fields["idProyecto"].empty_label = "Seleccionar"

    def clean_codigoPrueba(self):
        codigo = self.cleaned_data["codigoPrueba"].strip()
        if PruebasAplicativos.objects.filter(codigoPrueba__iexact=codigo).exists():
            raise forms.ValidationError("Ya existe una prueba de aplicativo con este código.")
        return codigo


class FormularioEditarPruebaAplicativo(forms.Form):
    idEstado = forms.ModelChoiceField(label="Estado", queryset=Estados.objects.none())
    idResultado = forms.ModelChoiceField(label="Resultado", required=False, queryset=Resultados.objects.none())
    fechaInicio = forms.DateField(label="Fecha de inicio", required=False, input_formats=["%Y-%m-%d"], widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    fechaFin = forms.DateField(label="Fecha de finalización", required=False, input_formats=["%Y-%m-%d"], widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    fechaPuestaPunto = forms.DateField(label="Fecha de puesta a punto", required=False, input_formats=["%Y-%m-%d"], widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    numAprobado = forms.IntegerField(label="Aprobados", min_value=0)
    numNoAprobado = forms.IntegerField(label="No aprobados", min_value=0)
    numAprobadoMenos = forms.IntegerField(label="Aprobados menos", min_value=0)
    numCasosPrueba = forms.IntegerField(label="Casos de prueba", min_value=0)
    documentoPruebas = forms.URLField(
        label="Enlace al documento de pruebas",
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://ejemplo.com/documento"}),
    )
    observaciones = forms.CharField(label="Observaciones", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, prueba=None, registro=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prueba = prueba
        self.registro = registro
        self.fields["idEstado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        self.fields["idResultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["idResultado"].empty_label = "Pendiente"
        if prueba and not self.is_bound:
            self.initial.update({
                "idEstado": prueba.idEstado,
                "idResultado": prueba.idResultado,
                "fechaInicio": prueba.fechaInicio,
                "fechaFin": prueba.fechaFin,
                "fechaPuestaPunto": prueba.fechaPuestaPunto,
                "numAprobado": prueba.numAprobado or 0,
                "numNoAprobado": prueba.numNoAprobado or 0,
                "numAprobadoMenos": prueba.numAprobadoMenos or 0,
                "numCasosPrueba": prueba.numCasosPrueba,
                "documentoPruebas": prueba.documentoPruebas,
                "observaciones": prueba.observaciones,
            })

    def clean_fechaFin(self):
        fecha_fin = self.cleaned_data.get("fechaFin")
        fecha_inicio = self.cleaned_data.get("fechaInicio")
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise forms.ValidationError("La fecha de finalización no puede ser anterior al inicio.")
        return fecha_fin

    def clean(self):
        data = super().clean()
        total = data.get("numCasosPrueba")
        resultados = (
            (data.get("numAprobado") or 0)
            + (data.get("numNoAprobado") or 0)
            + (data.get("numAprobadoMenos") or 0)
        )
        if total is not None and resultados > total:
            raise forms.ValidationError(
                "La suma de aprobados, no aprobados y aprobados menos no puede superar el total de casos de prueba."
            )
        return data


class FormularioEditarPruebaMaquina(FormularioEditarPruebaAplicativo):
    nombreJuego = forms.CharField(label="Nombre de la prueba", max_length=150, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["nombreJuego"] + [name for name in self.fields if name != "nombreJuego"])
        if self.registro and not self.is_bound:
            self.initial["nombreJuego"] = self.registro.nombreJuego


class FiltroBasePrueba(forms.Form):
    codigo = forms.CharField(label="Código", required=False, max_length=100)
    fechaDesde = forms.DateField(label="Fecha desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaHasta = forms.DateField(label="Fecha hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    encargado = forms.ModelChoiceField(label="Encargado", required=False, queryset=Usuario.objects.none())
    tipoPrueba = forms.ModelChoiceField(label="Tipo de prueba", required=False, queryset=TiposPruebas.objects.none())
    resultado = forms.ModelChoiceField(label="Resultado", required=False, queryset=Resultados.objects.none())
    estado = forms.ModelChoiceField(label="Estado", required=False, queryset=Estados.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["encargado"].queryset = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["tipoPrueba"].queryset = TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba")
        self.fields["resultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["estado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Todos"

    def clean(self):
        data = super().clean()
        if data.get("fechaDesde") and data.get("fechaHasta") and data["fechaHasta"] < data["fechaDesde"]:
            self.add_error("fechaHasta", "La fecha final no puede ser anterior a la inicial.")
        return data


class FiltroPruebaMaquina(FiltroBasePrueba):
    nombreJuego = forms.CharField(label="Nombre de la prueba", max_length=150, required=False)
    familia = forms.ModelChoiceField(label="Familia de juego", required=False, queryset=FamiliasJuegos.objects.none())
    tipoJuego = forms.ModelChoiceField(label="Tipo de juego", required=False, queryset=TipoJuego.objects.none())
    maquina = forms.ModelChoiceField(label="Gabinete", required=False, queryset=Maquinas.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["familia"].queryset = FamiliasJuegos.objects.filter(activo=True).order_by("nombreFamilia")
        self.fields["tipoJuego"].queryset = TipoJuego.objects.filter(activo=True).order_by("nombre")
        self.fields["maquina"].queryset = Maquinas.objects.filter(activo=True).order_by("nombreGabinete")
        for name in ("familia", "tipoJuego", "maquina"):
            self.fields[name].empty_label = "Todos"


class FiltroPruebaAplicativo(FiltroBasePrueba):
    tipoAplicativo = forms.ModelChoiceField(label="Tipo de aplicativo", required=False, queryset=TiposAplicativos.objects.none())
    proyecto = forms.ModelChoiceField(label="Proyecto", required=False, queryset=Proyectos.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipoAplicativo"].queryset = TiposAplicativos.objects.filter(activo=True).order_by("nombreTipoAplicativo")
        self.fields["proyecto"].queryset = Proyectos.objects.filter(activo=True).order_by("nombreProyecto")
        self.fields["tipoAplicativo"].empty_label = "Todos"
        self.fields["proyecto"].empty_label = "Todos"



class FiltroEstadisticas(forms.Form):
    fecha_desde = forms.DateField(label="Fecha desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fecha_hasta = forms.DateField(label="Fecha hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    encargado = forms.ModelChoiceField(label="Asignado a", required=False, queryset=Usuario.objects.none())
    tipo = forms.ModelChoiceField(label="Tipo de prueba", required=False, queryset=TiposPruebas.objects.none())
    resultado = forms.ModelChoiceField(label="Resultado", required=False, queryset=Resultados.objects.none())
    estado = forms.ModelChoiceField(label="Estado", required=False, queryset=Estados.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["encargado"].queryset = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["tipo"].queryset = TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba")
        self.fields["resultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["estado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Todos"

    def clean(self):
        data = super().clean()
        if data.get("fecha_desde") and data.get("fecha_hasta") and data["fecha_hasta"] < data["fecha_desde"]:
            self.add_error("fecha_hasta", "La fecha final no puede ser anterior a la inicial.")
        return data


class FiltroEstadisticasAplicativos(FiltroEstadisticas):
    proyecto = forms.ModelChoiceField(label="Proyecto", required=False, queryset=Proyectos.objects.none())
    tipoAplicativo = forms.ModelChoiceField(label="Tipo de aplicativo", required=False, queryset=TiposAplicativos.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("tipo")
        self.fields["proyecto"].queryset = Proyectos.objects.filter(activo=True).order_by("nombreProyecto")
        self.fields["tipoAplicativo"].queryset = TiposAplicativos.objects.filter(activo=True).order_by("nombreTipoAplicativo")


class FiltroEstadisticasMaquinas(FiltroEstadisticas):
    maquina = forms.ModelChoiceField(label="Gabinete", required=False, queryset=Maquinas.objects.none())
    familia = forms.ModelChoiceField(label="Familia de juego", required=False, queryset=FamiliasJuegos.objects.none())
    tipoJuego = forms.ModelChoiceField(label="Tipo de juego", required=False, queryset=TipoJuego.objects.none())
    protocolo = forms.ModelChoiceField(label="Protocolo", required=False, queryset=Protocolo.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("tipo")
        self.fields["maquina"].queryset = Maquinas.objects.filter(activo=True).order_by("nombreGabinete")
        self.fields["familia"].queryset = FamiliasJuegos.objects.filter(activo=True).order_by("nombreFamilia")
        self.fields["tipoJuego"].queryset = TipoJuego.objects.filter(activo=True).order_by("nombre")
        self.fields["protocolo"].queryset = Protocolo.objects.filter(activo=True).order_by("nombreProtocolo")
