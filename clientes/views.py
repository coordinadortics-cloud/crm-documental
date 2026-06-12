# =========================
# IMPORTS
# =========================

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required
)

from django.core.exceptions import PermissionDenied

import openpyxl

from .models import *
from .forms import *

from django import forms


# =========================
# VALIDAR ACCESO CLIENTES
# =========================

def validar_cliente_usuario(request, cliente):

    if request.user.is_superuser:

        return True

    asesor = Asesor.objects.filter(
        usuario=request.user
    ).first()

    if asesor and cliente.asesor == asesor:

        return True

    raise PermissionDenied


# =========================
# LISTA CLIENTES
# =========================

@login_required
def lista_clientes(request):

    busqueda = request.GET.get('busqueda')
    asesor_id = request.GET.get('asesor')

    # =========================
    # ADMIN VE TODO
    # =========================

    if request.user.is_superuser:

        clientes = Cliente.objects.all()

    else:

        asesor = Asesor.objects.filter(
            usuario=request.user
        ).first()

        if asesor:

            clientes = Cliente.objects.filter(
                asesor=asesor
            )

        else:

            clientes = Cliente.objects.none()

    # =========================
    # FILTROS
    # =========================

    if busqueda:

        clientes = clientes.filter(
            nombre__icontains=busqueda
        )

    if asesor_id and request.user.is_superuser:

        clientes = clientes.filter(
            asesor_id=asesor_id
        )

    # =========================
    # DOCUMENTOS
    # =========================

    documentos_requeridos = [
        'vinculacion',
        'rut',
        'camara',
        'cedula'
    ]

    data = []

    for cliente in clientes:

        documentos = Documento.objects.filter(
            cliente=cliente
        )

        # mapa por tipo (más eficiente)
        documentos_por_tipo = {
            d.tipo: d for d in documentos
        }

        completo = True
        faltantes = []

        for doc in documentos_requeridos:

            documento = documentos_por_tipo.get(doc)

            # NO existe documento
            if not documento:
                completo = False
                faltantes.append(doc)
                continue

            # existe pero NO aprobado
            if documento.estado != 'aprobado':
                completo = False

        data.append({
            'cliente': cliente,
            'faltantes': faltantes,
            'completo': completo
        })

    asesores = Asesor.objects.all()

    total_clientes = clientes.count()

    clientes_completos = len([
        x for x in data if x['completo']
    ])

    clientes_incompletos = len([
        x for x in data if not x['completo']
    ])

    total_asesores = asesores.count()

    return render(
        request,
        'clientes/lista_clientes.html',
        {
            'data': data,
            'asesores': asesores,
            'total_clientes': total_clientes,
            'clientes_completos': clientes_completos,
            'clientes_incompletos': clientes_incompletos,
            'total_asesores': total_asesores
        }
    )
# =========================
# CREAR CLIENTE
# =========================

@login_required
@permission_required(
    'clientes.add_cliente',
    raise_exception=True
)
def crear_cliente(request):

    if request.method == 'POST':

        form = ClienteForm(request.POST)

        if form.is_valid():

            cliente = form.save(commit=False)

            # =========================
            # ASIGNAR ASESOR AUTOMÁTICO
            # =========================

            if not request.user.is_superuser:

                asesor = Asesor.objects.filter(
                    usuario=request.user
                ).first()

                if asesor:

                    cliente.asesor = asesor

            cliente.save()

            Auditoria.objects.create(

                usuario=request.user,

                accion=f'Creó cliente {cliente.nombre}'
            )

            return redirect('lista_clientes')

    else:

        form = ClienteForm()

    # =========================
    # OCULTAR CAMPO ASESOR
    # =========================

    if not request.user.is_superuser:

        form.fields['asesor'].widget = forms.HiddenInput()

    return render(

        request,

        'clientes/crear_cliente.html',

        {
            'form': form
        }
    )


# =========================
# EDITAR CLIENTE
# =========================

@login_required
@permission_required(
    'clientes.change_cliente',
    raise_exception=True
)
def editar_cliente(request, cliente_id):

    cliente = Cliente.objects.get(
        id=cliente_id
    )

    validar_cliente_usuario(
        request,
        cliente
    )

    form = ClienteForm(

        request.POST or None,

        instance=cliente
    )

    if form.is_valid():

        form.save()

        Auditoria.objects.create(

            usuario=request.user,

            accion=f'Editó cliente {cliente.nombre}'
        )

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


# =========================
# ELIMINAR CLIENTE
# =========================

@login_required
@permission_required(
    'clientes.delete_cliente',
    raise_exception=True
)
def eliminar_cliente(request, cliente_id):

    cliente = Cliente.objects.get(
        id=cliente_id
    )

    validar_cliente_usuario(
        request,
        cliente
    )

    Auditoria.objects.create(

        usuario=request.user,

        accion=f'Eliminó cliente {cliente.nombre}'
    )

    cliente.delete()

    return redirect(
        'lista_clientes'
    )


# =========================
# SUBIR DOCUMENTO
# =========================

# =========================
# SUBIR DOCUMENTO
# =========================

@login_required
@permission_required(
    'clientes.add_documento',
    raise_exception=True
)
def subir_documento(request):

    cliente_id = request.GET.get('cliente')

    tipo = request.GET.get('tipo')

    form = DocumentoForm(

        request.POST or None,

        request.FILES or None
    )

    # =========================
    # AUTOCOMPLETAR CLIENTE
    # =========================

    if cliente_id:

        form.fields['cliente'].initial = cliente_id

    # =========================
    # AUTOCOMPLETAR TIPO
    # =========================

    if tipo:

        form.fields['tipo'].initial = tipo

    # =========================
    # FILTRAR CLIENTES ASESOR
    # =========================

    if not request.user.is_superuser:

        asesor = Asesor.objects.filter(
            usuario=request.user
        ).first()

        if asesor:

            form.fields['cliente'].queryset = Cliente.objects.filter(
                asesor=asesor
            )

    if form.is_valid():

        documento = form.save()

        Auditoria.objects.create(

            usuario=request.user,

            accion=f'Subió documento {documento.tipo} de {documento.cliente.nombre}'
        )

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
# =========================
# VER DOCUMENTOS
# =========================

@login_required
def ver_documentos(request, cliente_id):

    cliente = Cliente.objects.get(
        id=cliente_id
    )

    validar_cliente_usuario(
        request,
        cliente
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

    # =========================
    # DOCUMENTOS REQUERIDOS
    # =========================

    for clave, nombre in documentos_requeridos.items():

        documento = documentos.filter(
            tipo=clave
        ).first()

        data.append({

            'nombre': nombre,

            'tipo': clave,

            'existe': documento is not None,

            'archivo': documento

        })

    # =========================
    # DOCUMENTOS PERSONALIZADOS
    # =========================

    for documento in documentos_personalizados:

        data.append({

            'nombre': documento.nombre_personalizado,

            'tipo': 'otro',

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
# =========================
# ACTUALIZAR DOCUMENTO
# =========================

@login_required
@permission_required(
    'clientes.change_documento',
    raise_exception=True
)
def actualizar_documento(request, documento_id):

    documento = Documento.objects.get(
        id=documento_id
    )

    validar_cliente_usuario(
        request,
        documento.cliente
    )

    form = DocumentoForm(

        request.POST or None,

        request.FILES or None,

        instance=documento
    )

    if form.is_valid():

        form.save()

        Auditoria.objects.create(

            usuario=request.user,

            accion=f'Actualizó documento de {documento.cliente.nombre}'
        )

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


# =========================
# ELIMINAR DOCUMENTO
# =========================

@login_required
@permission_required(
    'clientes.delete_documento',
    raise_exception=True
)
def eliminar_documento(request, documento_id):

    documento = Documento.objects.get(
        id=documento_id
    )

    validar_cliente_usuario(
        request,
        documento.cliente
    )

    cliente_id = documento.cliente.id

    Auditoria.objects.create(

        usuario=request.user,

        accion=f'Eliminó documento de {documento.cliente.nombre}'
    )

    documento.delete()

    return redirect(
        'ver_documentos',
        cliente_id=cliente_id
    )

# =========================
# LISTA ASESORES
# =========================

@login_required
@permission_required(
    'clientes.view_asesor',
    raise_exception=True
)
def lista_asesores(request):

    asesores = Asesor.objects.all()

    return render(

        request,

        'clientes/lista_asesores.html',

        {
            'asesores': asesores
        }
    )


# =========================
# CREAR ASESOR
# =========================

@login_required
@permission_required(
    'clientes.add_asesor',
    raise_exception=True
)
def crear_asesor(request):

    form = AsesorForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        Auditoria.objects.create(

            usuario=request.user,

            accion='Creó un asesor'
        )

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


# =========================
# EDITAR ASESOR
# =========================

@login_required
@permission_required(
    'clientes.change_asesor',
    raise_exception=True
)
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

        Auditoria.objects.create(

            usuario=request.user,

            accion=f'Editó asesor {asesor.nombre}'
        )

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


# =========================
# ELIMINAR ASESOR
# =========================

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

# =========================
# EXPORTAR EXCEL
# =========================

@login_required
@permission_required(
    'clientes.view_cliente',
    raise_exception=True
)
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

    # =========================
    # SUPERUSUARIO VE TODO
    # =========================

    if request.user.is_superuser:

        clientes = Cliente.objects.all()

    else:

        asesor = Asesor.objects.filter(
            usuario=request.user
        ).first()

        clientes = Cliente.objects.filter(
            asesor=asesor
        )

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

# =========================
# LOGIN
# =========================

def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            'lista_clientes'
        )

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(

            request,

            username=username,

            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            Auditoria.objects.create(

                usuario=user,

                accion='Inició sesión'
            )

            return redirect(
                'lista_clientes'
            )

    return render(

        request,

        'clientes/login.html'
    )


# =========================
# LOGOUT
# =========================

@login_required
def logout_view(request):

    Auditoria.objects.create(

        usuario=request.user,

        accion='Cerró sesión'
    )

    logout(request)

    return redirect(
        'login'
    )


# =========================
# PANEL AUDITORIA
# =========================

@login_required
@permission_required(
    'clientes.view_auditoria',
    raise_exception=True
)
def panel_auditoria(request):

    busqueda = request.GET.get(
        'busqueda'
    )

    auditorias = Auditoria.objects.all().order_by(
        '-fecha'
    )

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

@login_required
@permission_required(
    'clientes.change_documento',
    raise_exception=True
)
def revisar_documento(request, documento_id):

    documento = Documento.objects.get(
        id=documento_id
    )

    form = RevisarDocumentoForm(

        request.POST or None,

        instance=documento
    )

    if form.is_valid():

        form.save()

        Auditoria.objects.create(

            usuario=request.user,

            accion=f'Revisó documento {documento.tipo} de {documento.cliente.nombre}'
        )

        return redirect(

            'ver_documentos',

            cliente_id=documento.cliente.id
        )

    return render(

        request,

        'clientes/revisar_documento.html',

        {
            'form': form,
            'documento': documento
        }
    )