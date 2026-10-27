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
    moeda = CharField(max_length=5, null=False)
    dt_referencia = DateTimeField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_moeda"

    @staticmethod
    def buscar():
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,USD-BRLT"
        headers = {"x-api-key": AWESOME_API_KEY}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def tratar_dados(dados_api):
        dolarc = dados_api["USDBRL"]
        dolart = dados_api["USDBRLT"]

        dt_comercial = datetime.strptime(dolarc["create_date"], "%Y-%m-%d %H:%M:%S")
        dt_turismo = datetime.strptime(dolart["create_date"], "%Y-%m-%d %H:%M:%S")
        dt_atualizacao = datetime.now()

        return [
            {"valor": Decimal(dolarc["bid"]), "status": True, "moeda": "USDCC",
            "dt_referencia": dt_comercial, "dt_atualizacao": dt_atualizacao},

            {"valor": Decimal(dolarc["ask"]), "status": True, "moeda": "USDCV",
            "dt_referencia": dt_comercial, "dt_atualizacao": dt_atualizacao},

            {"valor": Decimal(dolart["bid"]), "status": True, "moeda": "USDTC",
            "dt_referencia": dt_turismo, "dt_atualizacao": dt_atualizacao},

            {"valor": Decimal(dolart["ask"]), "status": True, "moeda": "USDTV",
            "dt_referencia": dt_turismo, "dt_atualizacao": dt_atualizacao}
        ]

    @staticmethod
    def atualizar():
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


    @staticmethod
    def carregar_historico(qtd=30):
        headers = {"x-api-key": AWESOME_API_KEY}
        moedas = {"USD-BRL": ("USDCC", "USDCV"),
                  "USD-BRLT": ("USDTC", "USDTV")}

        registros = []

        for par, (compra, venda) in moedas.items():
            url = f"https://economia.awesomeapi.com.br/json/daily/{par}/{qtd}"
            resposta = requests.get(url, headers=headers, timeout=30)
            resposta.raise_for_status()

            for item in resposta.json():
                dt_referencia = datetime.fromtimestamp(int(item["timestamp"]))
                dt_atualizacao = datetime.now()

                for codigo, campo in ((compra, "bid"), (venda, "ask")):
                    registros.append({
                        "valor": Decimal(item[campo]),
                        "status": True,
                        "moeda": codigo,
                        "dt_referencia": dt_referencia,
                        "dt_atualizacao": dt_atualizacao
                    })

        with conectar():
            for registro in registros:
                (Dolar.insert(**registro)
                    .on_conflict(
                        conflict_constraint="uq_tb_moeda_referencia",
                        update={
                            Dolar.valor: registro["valor"],
                            Dolar.status: registro["status"],
                            Dolar.dt_atualizacao: registro["dt_atualizacao"]
                        }
                    ).execute())

        print(f"Histórico processado: {len(registros)} registros.")                