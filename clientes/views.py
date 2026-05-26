from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import openpyxl
from django.contrib.auth.decorators import permission_required
from .models import *
from .forms import *
from django import forms


@login_required
def lista_clientes(request):

    busqueda = request.GET.get('busqueda')

    asesor_id = request.GET.get('asesor')

    clientes = Cliente.objects.all()

    if busqueda:

        clientes = clientes.filter(
            nombre__icontains=busqueda
        )

    if asesor_id:

        clientes = clientes.filter(
            asesor_id=asesor_id
        )

    data = []

    documentos_requeridos = [
        'vinculacion',
        'rut',
        'camara',
        'cedula'
    ]

    for cliente in clientes:

        documentos_subidos = Documento.objects.filter(
            cliente=cliente
        ).values_list(
            'tipo',
            flat=True
        )

        faltantes = [

            doc for doc in documentos_requeridos

            if doc not in documentos_subidos
        ]

        data.append({

            'cliente': cliente,

            'faltantes': faltantes,

            'completo': len(faltantes) == 0

        })

    asesores = Asesor.objects.all()

    total_clientes = Cliente.objects.count()

    clientes_completos = 0

    clientes_incompletos = 0

    for item in data:

        if item['completo']:

            clientes_completos += 1

        else:

            clientes_incompletos += 1

    total_asesores = Asesor.objects.count()

    clientes_por_asesor = []

    for asesor in asesores:

        cantidad = Cliente.objects.filter(
            asesor=asesor
        ).count()

        clientes_por_asesor.append({

            'nombre': asesor.nombre,
            'cantidad': cantidad

        })

    return render(

        request,

        'clientes/lista_clientes.html',

        {

            'data': data,
            'asesores': asesores,
            'total_clientes': total_clientes,
            'clientes_completos': clientes_completos,
            'clientes_incompletos': clientes_incompletos,
            'total_asesores': total_asesores,
            'clientes_por_asesor': clientes_por_asesor

        }
    )
@login_required
@permission_required('clientes.add_cliente')
def crear_cliente(request):

    if request.method == 'POST':

        form = ClienteForm(request.POST)

        if form.is_valid():

            cliente = form.save(commit=False)

            # =========================
            # ASIGNAR ASESOR AUTOMÁTICO
            # =========================

            if not request.user.is_superuser:

                asesor = Asesor.objects.get(
                    usuario=request.user
                )

                cliente.asesor = asesor

            cliente.save()

            return redirect('lista_clientes')

    else:

        form = ClienteForm()

    # =========================
    # OCULTAR CAMPO ASESOR
    # =========================

    form.fields['asesor'].widget = forms.HiddenInput()

    return render(

        request,
        'clientes/crear_cliente.html',

        {
            'form': form
        }
    )
@login_required
def editar_cliente(request, cliente_id):

    cliente = Cliente.objects.get(
        id=cliente_id
    )

    form = ClienteForm(

        request.POST or None,

        instance=cliente
    )

    if form.is_valid():

        form.save()

        return redirect(
            'lista_clientes'
        )

    return render(

        request,

        'clientes/editar_cliente.html',

        {
            'form': form
        }
    )

@login_required
@permission_required(
    'clientes.delete_cliente',
    raise_exception=True
)
def eliminar_cliente(request, cliente_id):

    cliente = Cliente.objects.get(
        id=cliente_id
    )

    Auditoria.objects.create(

        usuario=request.user,

        accion=f'Eliminó cliente {cliente.nombre}'
    )

    cliente.delete()

    return redirect(
        'lista_clientes'
    )

@login_required
def subir_documento(request):

    form = DocumentoForm(

        request.POST or None,

        request.FILES or None
    )

    if form.is_valid():

        documento = form.save()

        Auditoria.objects.create(

            usuario=request.user,

            accion=f'Subió documento {documento.tipo} de {documento.cliente.nombre}'
        )

        return redirect(
            'lista_clientes'
        )

    return render(

        request,

        'clientes/subir_documento.html',

        {
            'form': form
        }
    )
@login_required
def ver_documentos(request, cliente_id):

    cliente = Cliente.objects.get(
        id=cliente_id
    )

    documentos = Documento.objects.filter(
        cliente=cliente
    )

    documentos_requeridos = {

        'vinculacion': 'Formato Vinculación',

        'rut': 'RUT',

        'camara': 'Cámara Comercio',

        'cedula': 'Cedula'

    }

    documentos_personalizados = documentos.filter(
        tipo='otro'
    )

    data = []

    for clave, nombre in documentos_requeridos.items():

        documento = documentos.filter(
            tipo=clave
        ).first()

        data.append({

            'nombre': nombre,

            'existe': documento is not None,

            'archivo': documento

        })

    for documento in documentos_personalizados:

        data.append({

            'nombre': documento.nombre_personalizado,

            'existe': True,

            'archivo': documento

        })

    return render(

        request,

        'clientes/ver_documentos.html',

        {

            'cliente': cliente,

            'data': data

        }
    )

@login_required
def actualizar_documento(request, documento_id):

    documento = Documento.objects.get(
        id=documento_id
    )

    form = DocumentoForm(

        request.POST or None,

        request.FILES or None,

        instance=documento
    )

    if form.is_valid():

        form.save()

        return redirect(

            'ver_documentos',

            cliente_id=documento.cliente.id
        )

    return render(

        request,

        'clientes/subir_documento.html',

        {

            'form': form

        }
    )

@login_required
def lista_asesores(request):

    asesores = Asesor.objects.all()

    return render(

        request,

        'clientes/lista_asesores.html',

        {
            'asesores': asesores
        }
    )

@login_required
def crear_asesor(request):

    form = AsesorForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect(
            'lista_asesores'
        )

    return render(

        request,

        'clientes/crear_asesor.html',

        {
            'form': form
        }
    )

@login_required
def editar_asesor(request, asesor_id):

    asesor = Asesor.objects.get(
        id=asesor_id
    )

    form = AsesorForm(

        request.POST or None,

        instance=asesor
    )

    if form.is_valid():

        form.save()

        return redirect(
            'lista_asesores'
        )

    return render(

        request,

        'clientes/crear_asesor.html',

        {
            'form': form
        }
    )

@login_required
@permission_required(
    'clientes.delete_asesor',
    raise_exception=True
)
def eliminar_asesor(request, asesor_id):

    asesor = Asesor.objects.get(
        id=asesor_id
    )

    nombre_asesor = asesor.nombre

    asesor.delete()

    Auditoria.objects.create(

        usuario=request.user,

        accion=f'Eliminó asesor {nombre_asesor}'

    )

    return redirect(
        'lista_asesores'
    )

@login_required
def exportar_excel(request):

    response = HttpResponse(

        content_type='application/ms-excel'
    )

    response['Content-Disposition'] = (

        'attachment; filename="clientes.xlsx"'
    )

    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = 'Clientes'

    columnas = [

        'Cliente',
        'Documento',
        'Asesor',
        'Estado',
        'Faltantes'
    ]

    worksheet.append(columnas)

    clientes = Cliente.objects.all()

    documentos_requeridos = [
        'vinculacion',
        'rut',
        'camara',
        'cedula'
    ]

    for cliente in clientes:

        documentos_subidos = Documento.objects.filter(
            cliente=cliente
        ).values_list(
            'tipo',
            flat=True
        )

        faltantes = [

            doc for doc in documentos_requeridos

            if doc not in documentos_subidos
        ]

        estado = (

            'Completo'

            if len(faltantes) == 0

            else 'Incompleto'
        )

        asesor = (

            f"{cliente.asesor.codigo} - {cliente.asesor.nombre}"

            if cliente.asesor

            else 'Sin asesor'
        )

        worksheet.append([

            cliente.nombre,
            cliente.documento,
            asesor,
            estado,
            ', '.join(faltantes)

        ])

    workbook.save(response)

    return response

@login_required
def eliminar_documento(request, documento_id):

    documento = Documento.objects.get(
        id=documento_id
    )

    cliente_id = documento.cliente.id

    documento.delete()

    return redirect(
        'ver_documentos',
        cliente_id=cliente_id
    )

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(

            request,

            username=username,

            password=password
        )

        if user:

            login(request, user)

            return redirect('lista_clientes')

    return render(
        request,
        'clientes/login.html'
    )


def logout_view(request):

    logout(request)

    return redirect('login')

def login_view(request):

    if request.user.is_authenticated:

        return redirect('lista_clientes')

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('lista_clientes')

    return render(
        request,
        'clientes/login.html'
    )

@login_required
def panel_auditoria(request):

    busqueda = request.GET.get('busqueda')

    auditorias = Auditoria.objects.all().order_by('-fecha')

    if busqueda:

        auditorias = auditorias.filter(

            accion__icontains=busqueda
        )

    return render(

        request,

        'clientes/panel_auditoria.html',

        {
            'auditorias': auditorias
        }
    )