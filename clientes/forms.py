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

        fields = '__all__'

    def clean_archivo(self):

        archivo = self.cleaned_data.get('archivo')

        if archivo:

            extension = archivo.name.split('.')[-1].lower()

            extensiones_permitidas = [

                'pdf',
                'png',
                'jpg',
                'jpeg',
                'doc',
                'docx',
                'xlsx'
            ]

            if extension not in extensiones_permitidas:

                raise ValidationError(
                    'Tipo de archivo no permitido'
                )

            limite_mb = 10

            if archivo.size > limite_mb * 1024 * 1024:

                raise ValidationError(
                    'El archivo supera los 10MB'
                )

        return archivo
    def clean_archivo(self):

        archivo = self.cleaned_data.get('archivo')

        if archivo:

            extension = os.path.splitext(
                archivo.name
            )[1].lower()

            extensiones_permitidas = [

                '.pdf',
                '.png',
                '.jpg',
                '.jpeg'

            ]

            if extension not in extensiones_permitidas:

                raise forms.ValidationError(

                    'Solo se permiten PDF, JPG y PNG'

                )

            if archivo.size > 5 * 1024 * 1024:

                raise forms.ValidationError(

                    'El archivo no puede superar 5 MB'

                )

        return archivo

class AsesorForm(forms.ModelForm):

    class Meta:

        model = Asesor

        fields = [
            'codigo',
            'nombre'
        ]


