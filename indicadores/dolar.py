import os
import requests
from datetime import datetime
from decimal import Decimal
from peewee import Model, CharField, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar
from dotenv import load_dotenv

load_dotenv()
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

class Dolar(Model):
    cd_moeda = AutoField()
    valor = DecimalField(max_digits=18, decimal_places=5)
    status = BooleanField(default=True, null=False)
    moeda = CharField(max_length=4, null=False)
    dt_referencia = DateTimeField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_moeda"

    @staticmethod
    def buscar():
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
        headers = {"x-api-key": AWESOME_API_KEY}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def tratar_dados(dados_api):
        dolar = dados_api["USDBRL"]
        dt_referencia = datetime.strptime(dolar["create_date"], "%Y-%m-%d %H:%M:%S")
        dt_atualizacao = datetime.now()
        return [{"valor": Decimal(dolar["bid"]),
                 "status": True,
                 "moeda": "USDC",
                 "dt_referencia": dt_referencia,
                 "dt_atualizacao": dt_atualizacao
                },
                {
                 "valor": Decimal(dolar["ask"]),
                 "status": True,
                 "moeda": "USDV",
                 "dt_referencia": dt_referencia,
                 "dt_atualizacao": dt_atualizacao
                }
               ]

    @staticmethod
    def atualizar_dolar():
        dados_api = Dolar.buscar()
        dolares = Dolar.tratar_dados(dados_api)
        with conectar():
            for dolar in dolares:
                (Dolar.insert(**dolar)
                    .on_conflict(
                        conflict_constraint="uq_tb_moeda_referencia",
                        update={Dolar.valor: dolar["valor"],
                                Dolar.status: dolar["status"],
                                Dolar.dt_atualizacao: dolar["dt_atualizacao"]}).execute())