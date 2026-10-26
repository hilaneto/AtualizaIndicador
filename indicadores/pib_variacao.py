import requests
from peewee import Model, AutoField, DecimalField, BooleanField, DateField, DateTimeField
from database.conexao import db, conectar
from datetime import datetime, date
from decimal import Decimal


class Pib_Variacao(Model):
    cd_pib = AutoField()
    indice = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True)
    dt_referencia = DateField()
    dt_atualizacao = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = "tb_pib_variacao"


    @staticmethod
    def buscar():
        url = "https://apisidra.ibge.gov.br/values/t/5932/n1/1/v/6561/p/all/c11255/90707"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()[1:]

    @staticmethod
    def data_trimestre(codigo):
        ano = int(codigo[:4])
        trimestre = int(codigo[4:])
        return date(ano, trimestre * 3, (31, 30, 30, 31)[trimestre - 1])

    @staticmethod
    def atualizar():
        dados = Pib_Variacao.buscar()
        registros = []
        for item in dados:
            if item["V"] in ("...", "-", ""):
                continue
            registros.append({"indice": Decimal(item["V"]),
                              "dt_referencia": Pib_Variacao.data_trimestre(item["D3C"])})
        if not registros:
            return 0

        with conectar():
            for i in range(0, len(registros), 100):
                Pib_Variacao.insert_many(registros[i:i + 100]).on_conflict_ignore().execute()

        return len(registros)


    @staticmethod
    def atual():
        with conectar():
            return (Pib_Variacao.select().where(Pib_Variacao.status == True).order_by(Pib_Variacao.dt_referencia.desc()).first())

