import os
import requests
from datetime import datetime
from decimal import Decimal
from peewee import Model, CharField, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar
from dotenv import load_dotenv

load_dotenv()
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

class Bitcoin(Model):
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
        url = "https://economia.awesomeapi.com.br/json/last/BTC-BRL"
        headers = {"x-api-key": AWESOME_API_KEY}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def tratar_dados(dados_api):
        bitcoin = dados_api["BTCBRL"]
        return {"valor": Decimal(bitcoin["bid"]),
                "status": True,
                "moeda": str(bitcoin["code"]),
                "dt_referencia": datetime.strptime(
                bitcoin["create_date"],
                "%Y-%m-%d %H:%M:%S"),
                "dt_atualizacao": datetime.now()
                }

    @staticmethod
    def atualizar_bitcoin():
        dados_api = Bitcoin.buscar()
        bitcoin = Bitcoin.tratar_dados(dados_api)
        with conectar():
            (Bitcoin.insert(**bitcoin).on_conflict(
                    conflict_constraint="uq_tb_moeda_referencia",
                    update={Bitcoin.valor: bitcoin["valor"],
                            Bitcoin.status: bitcoin["status"],
                            Bitcoin.dt_atualizacao: bitcoin["dt_atualizacao"]}).execute())