from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ImportarCarteraForm
from .models import ImportacionCartera
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