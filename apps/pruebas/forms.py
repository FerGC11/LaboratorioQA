from django import forms

from apps.maquinas.models import Maquinas
from apps.usuarios.models import Usuario

from .models import (
    Estados,
    Juegos,
    Proveedores,
    PruebasAplicativos,
    PruebasMaquinas,
    Resultados,
    TiposAplicativos,
    TiposPruebas,
)


class FormularioPruebaMaquina(forms.Form):
    codigoPrueba = forms.CharField(label="Código de prueba", max_length=100)
    idEncargado = forms.ModelChoiceField(label="Encargado", queryset=Usuario.objects.none())
    idTipoPrueba = forms.ModelChoiceField(label="Tipo de prueba", queryset=TiposPruebas.objects.none())
    idResultado = forms.ModelChoiceField(label="Resultado", queryset=Resultados.objects.none())
    idEstado = forms.ModelChoiceField(label="Estado", queryset=Estados.objects.none())
    idProveedor = forms.ModelChoiceField(label="Proveedor", queryset=Proveedores.objects.none())
    idJuego = forms.ModelChoiceField(label="Juego", queryset=Juegos.objects.none())
    idMaquina = forms.ModelChoiceField(label="Máquina", queryset=Maquinas.objects.none())
    fechaPuestaPunto = forms.DateField(label="Fecha de puesta a punto", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaInicio = forms.DateField(label="Fecha de inicio", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaFin = forms.DateField(label="Fecha de finalización", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    observaciones = forms.CharField(label="Observaciones", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["idEncargado"].queryset = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["idTipoPrueba"].queryset = TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba")
        self.fields["idResultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["idEstado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        self.fields["idProveedor"].queryset = Proveedores.objects.filter(activo=True).order_by("nombreProveedor")
        self.fields["idJuego"].queryset = Juegos.objects.filter(activo=True).order_by("nombreJuego")
        self.fields["idMaquina"].queryset = Maquinas.objects.filter(activa=True).order_by("nombreMaquina")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Seleccionar"

    def clean_codigoPrueba(self):
        codigo = self.cleaned_data["codigoPrueba"].strip()
        if PruebasMaquinas.objects.filter(codigoPrueba__iexact=codigo).exists():
            raise forms.ValidationError("Ya existe una prueba con este código.")
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("fechaInicio")
        fin = cleaned_data.get("fechaFin")
        if inicio and fin and fin < inicio:
            self.add_error("fechaFin", "La fecha de finalización no puede ser anterior al inicio.")
        return cleaned_data


class FiltroPruebaMaquina(forms.Form):
    codigo = forms.CharField(label="Código", required=False, max_length=100)
    fechaDesde = forms.DateField(label="Fecha desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaHasta = forms.DateField(label="Fecha hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    encargado = forms.ModelChoiceField(label="Encargado", required=False, queryset=Usuario.objects.none())
    tipoPrueba = forms.ModelChoiceField(label="Tipo de prueba", required=False, queryset=TiposPruebas.objects.none())
    resultado = forms.ModelChoiceField(label="Resultado", required=False, queryset=Resultados.objects.none())
    estado = forms.ModelChoiceField(label="Estado", required=False, queryset=Estados.objects.none())
    proveedor = forms.ModelChoiceField(label="Proveedor", required=False, queryset=Proveedores.objects.none())
    juego = forms.ModelChoiceField(label="Juego", required=False, queryset=Juegos.objects.none())
    maquina = forms.ModelChoiceField(label="Máquina", required=False, queryset=Maquinas.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["encargado"].queryset = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["tipoPrueba"].queryset = TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba")
        self.fields["resultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["estado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        self.fields["proveedor"].queryset = Proveedores.objects.filter(activo=True).order_by("nombreProveedor")
        self.fields["juego"].queryset = Juegos.objects.filter(activo=True).order_by("nombreJuego")
        self.fields["maquina"].queryset = Maquinas.objects.filter(activa=True).order_by("nombreMaquina")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Todos"

    def clean(self):
        cleaned_data = super().clean()
        desde = cleaned_data.get("fechaDesde")
        hasta = cleaned_data.get("fechaHasta")
        if desde and hasta and hasta < desde:
            self.add_error("fechaHasta", "La fecha final no puede ser anterior a la inicial.")
        return cleaned_data


class FormularioPruebaAplicativo(forms.Form):
    codigoPrueba = forms.CharField(label="Código de prueba", max_length=100)
    idEncargado = forms.ModelChoiceField(label="Encargado", queryset=Usuario.objects.none())
    idDesarrollador = forms.ModelChoiceField(label="Desarrollador", queryset=Usuario.objects.none())
    idTipoPrueba = forms.ModelChoiceField(label="Tipo de prueba", queryset=TiposPruebas.objects.none())
    idTipoAplicativo = forms.ModelChoiceField(label="Tipo de aplicativo", queryset=TiposAplicativos.objects.none())
    idResultado = forms.ModelChoiceField(label="Resultado", queryset=Resultados.objects.none())
    idEstado = forms.ModelChoiceField(label="Estado", queryset=Estados.objects.none())
    fechaPuestaPunto = forms.DateField(label="Fecha de puesta a punto", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaInicio = forms.DateField(label="Fecha de inicio", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaFin = forms.DateField(label="Fecha de finalización", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    observaciones = forms.CharField(label="Observaciones", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usuarios = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["idEncargado"].queryset = usuarios
        self.fields["idDesarrollador"].queryset = usuarios
        self.fields["idTipoPrueba"].queryset = TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba")
        self.fields["idTipoAplicativo"].queryset = TiposAplicativos.objects.filter(activo=True).order_by("nombreTipoAplicativo")
        self.fields["idResultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["idEstado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Seleccionar"

    def clean_codigoPrueba(self):
        codigo = self.cleaned_data["codigoPrueba"].strip()
        if PruebasAplicativos.objects.filter(codigoPrueba__iexact=codigo).exists():
            raise forms.ValidationError("Ya existe una prueba de aplicativo con este código.")
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("fechaInicio")
        fin = cleaned_data.get("fechaFin")
        if inicio and fin and fin < inicio:
            self.add_error("fechaFin", "La fecha de finalización no puede ser anterior al inicio.")
        return cleaned_data


class FiltroPruebaAplicativo(forms.Form):
    codigo = forms.CharField(label="Código", required=False, max_length=100)
    fechaDesde = forms.DateField(label="Fecha desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    fechaHasta = forms.DateField(label="Fecha hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    encargado = forms.ModelChoiceField(label="Encargado", required=False, queryset=Usuario.objects.none())
    desarrollador = forms.ModelChoiceField(label="Desarrollador", required=False, queryset=Usuario.objects.none())
    tipoPrueba = forms.ModelChoiceField(label="Tipo de prueba", required=False, queryset=TiposPruebas.objects.none())
    tipoAplicativo = forms.ModelChoiceField(label="Tipo de aplicativo", required=False, queryset=TiposAplicativos.objects.none())
    resultado = forms.ModelChoiceField(label="Resultado", required=False, queryset=Resultados.objects.none())
    estado = forms.ModelChoiceField(label="Estado", required=False, queryset=Estados.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usuarios = Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username")
        self.fields["encargado"].queryset = usuarios
        self.fields["desarrollador"].queryset = usuarios
        self.fields["tipoPrueba"].queryset = TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba")
        self.fields["tipoAplicativo"].queryset = TiposAplicativos.objects.filter(activo=True).order_by("nombreTipoAplicativo")
        self.fields["resultado"].queryset = Resultados.objects.filter(activo=True).order_by("nombreResultado")
        self.fields["estado"].queryset = Estados.objects.filter(activo=True).order_by("nombreEstado")
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Todos"

    def clean(self):
        cleaned_data = super().clean()
        desde = cleaned_data.get("fechaDesde")
        hasta = cleaned_data.get("fechaHasta")
        if desde and hasta and hasta < desde:
            self.add_error("fechaHasta", "La fecha final no puede ser anterior a la inicial.")
        return cleaned_data