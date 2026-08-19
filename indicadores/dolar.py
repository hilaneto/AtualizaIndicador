import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from peewee import Model, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar

load_dotenv()
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

class Dolar(Model):
    cd_dolar = AutoField()
    valor = DecimalField(max_digits=10, decimal_places=2)
    variacao = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateTimeField(default=datetime.now, null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_dolar"

    @staticmethod
    def buscar():
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
        headers = { "x-api-key": AWESOME_API_KEY }
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

def atualizar_dolar():
    try:
        dados_api = Dolar.buscar()
        dolar_api = dados_api["USDBRL"]

        dados = {"valor": dolar_api["bid"],
                 "variacao": dolar_api["pctChange"],
                 "dt_referencia": datetime.strptime(dolar_api["create_date"],"%Y-%m-%d %H:%M:%S"),
                 "dt_atualizacao": datetime.now(),
                 "status": True}

    except Exception as erro:
        dados = {"valor": 0,
                 "variacao": 0,
                 "dt_referencia": datetime.now(),
                 "dt_atualizacao": datetime.now(),
                 "status": False}

        print(f"Erro ao atualizar dólar: {erro}")

    with conectar():
        Dolar.create(**dados)
