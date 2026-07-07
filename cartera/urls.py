from django.urls import path
from . import views



urlpatterns = [

    path(
        "importar/",
        views.importar_cartera,
        name="importar_cartera",
    ),

    path(
        "",
        views.dashboard,
        name="dashboard_cartera"
    ),

    path(
        "importar/",
        views.importar_cartera,
        name="importar_cartera"
    ),

]

