import time
from decimal import Decimal

import pandas as pd
from django.db import transaction
from django.db.models import Sum

from cartera.models import (
    ClienteCartera,
    FacturaCartera,
    ImportacionCartera,
)


class ImportadorCartera:

    COLUMNAS = [
        "CEDULA",
        "CLIENTE",
        "TIPO",
        "NUMERO",
        "FORMAPAGO",
        "VALOR",
        "SALDO",
        "MCNFECHA",
        "VENCEFACT",
        "DETALLEPRO",
        "TELEFONO",
        "CELULAR",
        "CORREO",
        "CIUNOMBRE",
        "BARRIO",
        "MCNZONA",
        "VENNOMBRE",
        "MCNCOBRA",
    ]

    def __init__(self, archivo):
        self.archivo = archivo

    def leer_excel(self):
        return pd.read_excel(self.archivo)

    def validar_columnas(self, df):

        faltantes = []

        for columna in self.COLUMNAS:
            if columna not in df.columns:
                faltantes.append(columna)

        if faltantes:
            raise Exception(
                "El archivo no corresponde al formato esperado.\n\n"
                + "\n".join(faltantes)
            )

        if df.empty:
            raise Exception("El archivo está vacío.")

    def texto(self, valor):

        if pd.isna(valor):
            return ""

        valor = str(valor).strip()

        if valor.endswith(".0"):
            valor = valor[:-2]

        return valor

    def numero(self, valor):

        if pd.isna(valor):
            return Decimal("0")

        try:
            return Decimal(str(valor))
        except:
            return Decimal("0")

    def fecha(self, valor):

        if pd.isna(valor):
            return None

        fecha = pd.to_datetime(valor, errors="coerce")

        if pd.isna(fecha):
            return None

        return fecha.date()

    @transaction.atomic
    def importar(self):

        inicio = time.time()

        df = self.leer_excel()

        self.validar_columnas(df)

        # Borra la cartera anterior
        FacturaCartera.objects.all().delete()
        ClienteCartera.objects.all().delete()

        clientes = {}

        for _, fila in df.iterrows():

            nit = self.texto(fila["CEDULA"])

            if nit not in clientes:

                cliente = ClienteCartera.objects.create(

                    nit=nit,

                    cliente=self.texto(fila["CLIENTE"]),

                    telefono=self.texto(fila["TELEFONO"]),

                    celular=self.texto(fila["CELULAR"]),

                    correo=self.texto(fila["CORREO"]),

                    ciudad=self.texto(fila["CIUNOMBRE"]),

                    barrio=self.texto(fila["BARRIO"]),

                    asesor=self.texto(fila["VENNOMBRE"]),

                    cobrador=self.texto(fila["MCNCOBRA"]),

                    zona=self.texto(fila["MCNZONA"]),

                )

                clientes[nit] = cliente

            FacturaCartera.objects.create(

                cliente=clientes[nit],

                factura=self.texto(fila["NUMERO"]),

                tipo=self.texto(fila["TIPO"]),

                forma_pago=self.texto(fila["FORMAPAGO"]),

                valor=self.numero(fila["VALOR"]),

                saldo=self.numero(fila["SALDO"]),

                fecha_expedicion=self.fecha(fila["MCNFECHA"]),

                fecha_vencimiento=self.fecha(fila["VENCEFACT"]),

                detalle=self.texto(fila["DETALLEPRO"]),
            )

        # Actualizar información de cada cliente
        for cliente in ClienteCartera.objects.all():

            total = cliente.facturas.aggregate(
                total=Sum("saldo")
            )["total"] or Decimal("0")

            cliente.saldo_total = total
            cliente.cantidad_facturas = cliente.facturas.count()

            cliente.save()

        clientes_importados = ClienteCartera.objects.count()

        facturas_importadas = FacturaCartera.objects.count()

        valor_total = FacturaCartera.objects.aggregate(
            total=Sum("saldo")
        )["total"] or Decimal("0")

        tiempo = round(time.time() - inicio, 2)

        ImportacionCartera.objects.create(
            nombre_archivo=self.archivo.name,
            clientes=clientes_importados,
            facturas=facturas_importadas,
            valor_total=valor_total,
        )

        return {
            "clientes": clientes_importados,
            "facturas": facturas_importadas,
            "valor": valor_total,
            "tiempo": tiempo,
            "archivo": self.archivo.name,
        }