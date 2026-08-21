import requests
from datetime import datetime, timedelta
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Dolar(Model):
    cd_dolar = AutoField()
    valor = DecimalField(max_digits=10, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
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

    @staticmethod
    def atualizar_dolar():
        dados = Dolar.buscar()
        with conectar():
            for registro in dados:
                dolar = {"valor": Decimal(registro["valor"]),
                        "status": True,
                        "dt_referencia": datetime.strptime(registro["data"],"%d/%m/%Y").date(),
                        "dt_atualizacao": datetime.now()}
                
                Dolar.insert(**dolar).on_conflict(
                conflict_target=[Dolar.dt_referencia],
                update={Dolar.valor: dolar["valor"],
                        Dolar.status: dolar["status"],
                        Dolar.dt_atualizacao: dolar["dt_atualizacao"]}).execute()
