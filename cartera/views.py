from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from .forms import ImportarCarteraForm, BuscarClienteForm
from .models import (
    ImportacionCartera,
    ClienteCartera,
)
from .services.importador_cartera import ImportadorCartera


def dashboard(request):

    ultima = ImportacionCartera.objects.order_by("-fecha").first()

    return render(
        request,
        "cartera/dashboard.html",
        {
            "ultima": ultima
        }
    )


def importar_cartera(request):

    form = ImportarCarteraForm()

    if request.method == "POST":

        form = ImportarCarteraForm(request.POST, request.FILES)

        if form.is_valid():

            archivo = request.FILES["archivo"]

            try:

                importador = ImportadorCartera(archivo)

                resultado = importador.importar()

                messages.success(
                    request,
                    f"""
Importación realizada correctamente.

Archivo: {resultado['archivo']}

Clientes importados: {resultado['clientes']}

Facturas importadas: {resultado['facturas']}

Valor total de la cartera: ${resultado['valor']:,.2f}

Tiempo de importación: {resultado['tiempo']} segundos.
                    """
                )

                return redirect("dashboard_cartera")

            except Exception as e:

                messages.error(
                    request,
                    f"Error durante la importación: {str(e)}"
                )

                return redirect("importar_cartera")

    return render(
        request,
        "cartera/importar.html",
        {
            "form": form
        }
    )


# ===========================
# MÓDULO 2
# ===========================

def consultar_cliente(request):

    form = BuscarClienteForm()

    clientes = None

    if request.method == "POST":

        form = BuscarClienteForm(request.POST)

        if form.is_valid():

            busqueda = form.cleaned_data["busqueda"].strip()

            clientes = ClienteCartera.objects.filter(
                Q(nit__icontains=busqueda) |
                Q(cliente__icontains=busqueda)
            ).order_by("cliente")

            if not clientes.exists():

                messages.error(
                    request,
                    "No se encontraron clientes."
                )

    return render(
        request,
        "cartera/consultar_cliente.html",
        {
            "form": form,
            "clientes": clientes,
        },
    )


def ver_cliente(request, id):

    cliente = get_object_or_404(
        ClienteCartera,
        id=id
    )

    facturas = sorted(
        cliente.facturas.all(),
        key=lambda x: x.dias_mora,
        reverse=True
    )

    return render(
        request,
        "cartera/ver_cliente.html",
        {
            "cliente": cliente,
            "facturas": facturas,
        },
    )