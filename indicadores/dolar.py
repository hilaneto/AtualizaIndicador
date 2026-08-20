import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from peewee import Model, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar

load_dotenv()
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

class Dolar(Model):
    cd_dolar = AutoField()
    valor = DecimalField(max_digits=10, decimal_places=2)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateTimeField(default=datetime.now, null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_dolar"

    @staticmethod
    def buscar():
        # Datas -------------------------------------------------------
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=62)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        # API Banco Central ---------------------------------------------
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"

        parametros = { "formato": "json", "dataInicial": data_inicial, "dataFinal": data_final }
        resposta = requests.get(url, params=parametros, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    def atualizar_dolar():
        try:
            dados_api = Dolar.buscar()
            dolar_api = dados_api["USDBRL"]

            dados = {"valor": dolar_api["bid"],
                    "dt_referencia": datetime.strptime(dolar_api["create_date"],"%Y-%m-%d %H:%M:%S"),
                    "dt_atualizacao": datetime.now(),
                    "status": True}

        except Exception as erro:
            dados = {"valor": 0,
                    "dt_referencia": datetime.now(),
                    "dt_atualizacao": datetime.now(),
                    "status": False}

            print(f"Erro ao atualizar dólar: {erro}")

        with conectar():
            Dolar.create(**dados)
