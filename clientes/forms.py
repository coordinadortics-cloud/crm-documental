import os
from django import forms
from .models import *
from django.core.exceptions import ValidationError



class ClienteForm(forms.ModelForm):

    class Meta:

        model = Cliente

        fields = [
            'nombre',
            'documento',
            'telefono',
            'correo',
            'asesor'
            
        ]



class DocumentoForm(forms.ModelForm):

    class Meta:
        model = Documento
        fields = [
            'cliente',
            'tipo',
            'nombre_personalizado',
            'archivo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # el archivo no es obligatorio al editar
        self.fields['archivo'].required = False

    def clean_archivo(self):

        archivo = self.cleaned_data.get('archivo')

        # =========================
        # SI ESTÁ EDITANDO Y NO SUBE ARCHIVO
        # =========================
        if not archivo:
            if self.instance and self.instance.pk:
                return self.instance.archivo

            raise forms.ValidationError('Debe subir un archivo')

        # =========================
        # VALIDAR EXTENSIÓN
        # =========================
        extension = os.path.splitext(archivo.name)[1].lower()

        extensiones_permitidas = [
            '.pdf',
            '.png',
            '.jpg',
            '.jpeg',
            '.doc',
            '.docx',
            '.xlsx'
        ]

        if extension not in extensiones_permitidas:
            raise forms.ValidationError('Tipo de archivo no permitido')

        # =========================
        # VALIDAR PESO
        # =========================
        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError('El archivo supera los 10MB')

        return archivo
class RevisarDocumentoForm(forms.ModelForm):

    class Meta:

        model = Documento

        fields = [

            'estado',
            'observacion'
        ]

        widgets = {

            'estado': forms.Select(

                attrs={
                    'class': 'form-select'
                }
            ),

            'observacion': forms.Textarea(

                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            )
        }



class AsesorForm(forms.ModelForm):

    class Meta:
        model = Asesor
        fields = [
            'codigo',
            'nombre'
        ]