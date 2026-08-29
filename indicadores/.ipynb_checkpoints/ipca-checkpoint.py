import requests
from datetime import datetime, timedelta
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Ipca(Model):
    cd_ipca = AutoField()
    indice = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_ipca"

    @staticmethod
    def buscar():
        # Datas -------------------------------------------------------
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=62)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        # API Banco Central ---------------------------------------------
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.10844/dados"

        parametros = { "formato": "json", "dataInicial": data_inicial, "dataFinal": data_final }
        resposta = requests.get(url, params=parametros, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar_ipca():
        dados = Ipca.buscar()
        with conectar():
            for registro in dados:
                ipca = {"indice": Decimal(registro["valor"]),
                        "status": True,
                        "dt_referencia": datetime.strptime(registro["data"],"%d/%m/%Y").date(),
                        "dt_atualizacao": datetime.now()}
                
                Ipca.insert(**ipca).on_conflict(
                conflict_target=[Ipca.dt_referencia],
                update={Ipca.indice: ipca["indice"],
                        Ipca.status: ipca["status"],
                        Ipca.dt_atualizacao: ipca["dt_atualizacao"]}).execute()
