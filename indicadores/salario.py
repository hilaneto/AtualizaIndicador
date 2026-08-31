import requests
from datetime import datetime, timedelta
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Salario(Model):
    cd_salario = AutoField()
    vl_salario = DecimalField(max_digits=8, decimal_places=2)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)
   
    class Meta:
        database = db
        table_name = "tb_salariominimo"

    @staticmethod
    def buscar():
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=62)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        # API Banco Central ---------------------------------------------
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1619/dados"

        parametros = {"formato": "json", "dataInicial": data_inicial, "dataFinal": data_final}
        resposta = requests.get(url, params=parametros, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar_salario():
        dados = Salario.buscar()
        with conectar():
            for registro in dados:
                salario = {"vl_salario": Decimal(registro["valor"]),
                           "status": True,
                           "dt_referencia": datetime.strptime(registro["data"], "%d/%m/%Y").date(),"dt_atualizacao": datetime.now()
                          }
                (Salario.insert(**salario).on_conflict(conflict_target=[Salario.dt_referencia],action="IGNORE").execute())
