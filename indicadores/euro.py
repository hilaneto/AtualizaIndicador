import os
import requests
from datetime import datetime
from decimal import Decimal
from peewee import Model, CharField, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar
from dotenv import load_dotenv

load_dotenv()
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

class Euro(Model):
    cd_moeda = AutoField()
    valor = DecimalField(max_digits=18, decimal_places=5)
    status = BooleanField(default=True, null=False)
    moeda = CharField(max_length=3, null=False)
    dt_referencia = DateTimeField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_moeda"

    @staticmethod
    def buscar():
        url = "https://economia.awesomeapi.com.br/json/last/EUR-BRL"
        headers = {"x-api-key": AWESOME_API_KEY}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def tratar_dados(dados_api):
        euro = dados_api["EURBRL"]
        return {"valor": Decimal(euro["bid"]),
                "status": True,
                "moeda": str(euro["code"]),
                "dt_referencia": datetime.strptime(
                euro["create_date"],
                "%Y-%m-%d %H:%M:%S"),
                "dt_atualizacao": datetime.now()
                }

    @staticmethod
    def atualizar_euro():
        dados_api = Euro.buscar()
        euro = Euro.tratar_dados(dados_api)
        with conectar():
            (Euro.insert(**euro).on_conflict(
                    conflict_constraint="uq_tb_moeda_referencia",
                    update={Euro.valor: euro["valor"],
                            Euro.status: euro["status"],
                            Euro.dt_atualizacao: euro["dt_atualizacao"]}).execute())