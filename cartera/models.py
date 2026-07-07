from django.db import models


class ClienteCartera(models.Model):

    nit = models.CharField(max_length=30, unique=True)

    cliente = models.CharField(max_length=250)

    telefono = models.CharField(max_length=50, blank=True)

    celular = models.CharField(max_length=50, blank=True)

    correo = models.EmailField(blank=True)

    ciudad = models.CharField(max_length=150, blank=True)

    barrio = models.CharField(max_length=150, blank=True)

    asesor = models.CharField(max_length=150, blank=True)

    cobrador = models.CharField(max_length=150, blank=True)

    zona = models.CharField(max_length=100, blank=True)

    saldo_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )

    cantidad_facturas = models.IntegerField(default=0)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nit} - {self.cliente}"
    
from datetime import date

class FacturaCartera(models.Model):

    cliente = models.ForeignKey(
        ClienteCartera,
        on_delete=models.CASCADE,
        related_name="facturas"
    )

    factura = models.CharField(max_length=50)

    tipo = models.CharField(max_length=20, blank=True)

    forma_pago = models.CharField(max_length=80, blank=True)

    valor = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )

    saldo = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )

    fecha_expedicion = models.DateField(null=True, blank=True)

    fecha_vencimiento = models.DateField(null=True, blank=True)

    detalle = models.TextField(blank=True)

    estado = models.CharField(
        max_length=30,
        default="VENCIDA"
    )

    @property
    def dias_mora(self):

        if not self.fecha_vencimiento:
            return 0

        return max(
            (date.today() - self.fecha_vencimiento).days,
            0
        )

    def __str__(self):
        return self.factura
    
class ImportacionCartera(models.Model):

    fecha = models.DateTimeField(auto_now_add=True)

    nombre_archivo = models.CharField(max_length=255)

    clientes = models.IntegerField(default=0)

    facturas = models.IntegerField(default=0)

    valor_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.nombre_archivo} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"