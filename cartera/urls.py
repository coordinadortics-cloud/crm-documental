from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard_cartera"
    ),

    path(
        "importar/",
        views.importar_cartera,
        name="importar_cartera",
    ),

    path(
        "consultar/",
        views.consultar_cliente,
        name="consultar_cliente",
    ),

    path(
        "cliente/<int:id>/",
        views.ver_cliente,
        name="ver_cliente",
    ),

]