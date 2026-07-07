from django.contrib import admin
from .models import ClienteCartera, FacturaCartera
from .models import ImportacionCartera


class FacturaInline(admin.TabularInline):
    model = FacturaCartera
    extra = 0


@admin.register(ClienteCartera)
class ClienteCarteraAdmin(admin.ModelAdmin):

    list_display = (
        "nit",
        "cliente",
        "ciudad",
        "celular",
        "saldo_total",
        "cantidad_facturas",
    )

    search_fields = (
        "nit",
        "cliente",
    )

    list_filter = (
        "ciudad",
        "asesor",
    )

    inlines = [FacturaInline]


@admin.register(FacturaCartera)
class FacturaCarteraAdmin(admin.ModelAdmin):

    list_display = (
        "factura",
        "cliente",
        "valor",
        "saldo",
        "fecha_vencimiento",
        "estado",
    )

    search_fields = (
        "factura",
        "cliente__cliente",
        "cliente__nit",
    )

@admin.register(ImportacionCartera)
class ImportacionCarteraAdmin(admin.ModelAdmin):

    list_display = (
        "fecha",
        "nombre_archivo",
        "clientes",
        "facturas",
        "valor_total",
    )

    ordering = ("-fecha",)