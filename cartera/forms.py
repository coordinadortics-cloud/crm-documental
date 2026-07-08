from django import forms


class ImportarCarteraForm(forms.Form):

    archivo = forms.FileField(
        label="Seleccione el archivo de cartera",
        help_text="Solo se permiten archivos Excel (.xlsx o .xls)"
    )

    def clean_archivo(self):

        archivo = self.cleaned_data["archivo"]

        nombre = archivo.name.lower()

        if not (
            nombre.endswith(".xlsx")
            or nombre.endswith(".xls")
        ):
            raise forms.ValidationError(
                "Debe seleccionar un archivo de Excel."
            )

        return archivo
    
    # / modulo 2


class BuscarClienteForm(forms.Form):

    busqueda = forms.CharField(
        label="Buscar Cliente",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite NIT o nombre del cliente..."
            }
        )
    )