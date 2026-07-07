from django.db import models


class ClienteCartera(models.Model):
    nit = models.CharField(max_length=30, unique=True)
    cliente = models.CharField(max_length=250)

    direccion = models.CharField(max_length=250, blank=True)
    ciudad = models.CharField(max_length=120, blank=True)

    telefono = models.CharField(max_length=50, blank=True)
    celular = models.CharField(max_length=50, blank=True)

    correo = models.EmailField(blank=True)

    asesor = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.nit} - {self.cliente}"


class FacturaCartera(models.Model):

    cliente = models.ForeignKey(
        ClienteCartera,
        on_delete=models.CASCADE,
        related_name="facturas"
    )

    factura = models.CharField(max_length=50)

    fecha_expedicion = models.DateField(null=True, blank=True)

    fecha_vencimiento = models.DateField(null=True, blank=True)

    dias_mora = models.IntegerField(default=0)

    saldo = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )

    class Meta:
        ordering = ["-dias_mora"]

    def __str__(self):
        return self.factura