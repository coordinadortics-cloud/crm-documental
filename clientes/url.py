from django.urls import path
from . import views

urlpatterns = [

path(
        '',
        views.lista_clientes,
        name='lista_clientes'
    ),

path(
        'crear/',
        views.crear_cliente,
        name='crear_cliente'
    ),

path(
    'subir-documento/',
    views.subir_documento,
    name='subir_documento'
),

path(
    'documentos/<int:cliente_id>/',
    views.ver_documentos,
    name='ver_documentos'
),

path(
    'editar/<int:cliente_id>/',
    views.editar_cliente,
    name='editar_cliente'
),

path(
    'eliminar/<int:cliente_id>/',
    views.eliminar_cliente,
    name='eliminar_cliente'
),


path(
    'asesores/',
    views.lista_asesores,
    name='lista_asesores'
),

path(
    'asesores/crear/',
    views.crear_asesor,
    name='crear_asesor'
),

path(
    'asesores/eliminar/<int:asesor_id>/',
    views.eliminar_asesor,
    name='eliminar_asesor'
),

path(
    'asesores/editar/<int:asesor_id>/',
    views.editar_asesor,
    name='editar_asesor'
),

path(
    'exportar-excel/',
    views.exportar_excel,
    name='exportar_excel'
),

path(
    'documento/actualizar/<int:documento_id>/',
    views.actualizar_documento,
    name='actualizar_documento'
),

path(
    'documento/eliminar/<int:documento_id>/',
    views.eliminar_documento,
    name='eliminar_documento'
),

path(
        'login/',
        views.login_view,
        name='login'
    ),

path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

path(
    'auditoria/',
    views.panel_auditoria,
    name='panel_auditoria'
),

]

