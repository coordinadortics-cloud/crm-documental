from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os
import pikepdf


class Asesor(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(
        max_length=200
    )

    def __str__(self):

        return f"{self.codigo} - {self.nombre}"


class Cliente(models.Model):

    nombre = models.CharField(
        max_length=200
    )

    documento = models.CharField(
        max_length=20
    )

    telefono = models.CharField(
        max_length=20
    )

    correo = models.EmailField()

    asesor = models.ForeignKey(
        Asesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):

        return self.nombre


def ruta_documentos(instance, filename):

    extension = filename.split('.')[-1]

    nombre_archivo = (
        f"{instance.tipo}_{instance.cliente.documento}.{extension}"
    )

    return os.path.join(
        'clientes',
        instance.cliente.documento,
        nombre_archivo
    )


class Documento(models.Model):

    TIPOS = [

        ('vinculacion', 'Formato Vinculación'),
        ('rut', 'RUT'),
        ('camara', 'Cámara Comercio'),
        ('cedula', 'Cedula'),
        ('otro', 'Otro')

    ]

    # =========================
    # ESTADOS DOCUMENTO
    # =========================

    ESTADOS = [

        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado')

    ]

    cliente = models.ForeignKey(

        Cliente,

        on_delete=models.CASCADE,

        related_name='documentos'
    )

    tipo = models.CharField(

        max_length=50,

        choices=TIPOS
    )

    nombre_personalizado = models.CharField(

        max_length=200,

        blank=True,

        null=True
    )

    archivo = models.FileField(

        upload_to=ruta_documentos
    )

    # =========================
    # ESTADO REVISIÓN CARTERA
    # =========================

    estado = models.CharField(

        max_length=20,

        choices=ESTADOS,

        default='pendiente'
    )

    observacion = models.TextField(

        blank=True,

        null=True
    )

    fecha_subida = models.DateTimeField(

        auto_now_add=True
    )

    def __str__(self):

        if self.tipo == 'otro' and self.nombre_personalizado:

            return self.nombre_personalizado

        return self.get_tipo_display()

    # =========================
    # GUARDAR Y COMPRIMIR
    # =========================

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        # =========================
        # VALIDAR ARCHIVO
        # =========================

        if not self.archivo:

            return

        try:

            ruta = self.archivo.path

            extension = os.path.splitext(
                ruta
            )[1].lower()

            # =========================
            # COMPRIMIR IMAGENES
            # =========================

            if extension in [

                '.jpg',
                '.jpeg',
                '.png'
            ]:

                imagen = Image.open(ruta)

                if imagen.mode in ("RGBA", "P"):

                    imagen = imagen.convert("RGB")

                imagen.save(

                    ruta,

                    optimize=True,

                    quality=60
                )

            # =========================
            # COMPRIMIR PDF
            # =========================

            elif extension == '.pdf':

                pdf = pikepdf.Pdf.open(

                    ruta,

                    allow_overwriting_input=True
                )

                pdf.save(

                    ruta,

                    compress_streams=True
                )

        except Exception as e:

            print(

                "ERROR AL PROCESAR ARCHIVO:",
                e
            )

class Auditoria(models.Model):

    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True
    )

    accion = models.CharField(
        max_length=200
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.usuario} - {self.accion}"
    

