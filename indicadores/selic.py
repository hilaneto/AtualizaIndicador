import requests
from datetime import datetime, timedelta
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Selic(Model):
    cd_selic = AutoField()
    indice = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_selic"

    @staticmethod
    def buscar():
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=600)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        # API Banco Central ---------------------------------------------
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados"

        parametros = {"formato": "json", "dataInicial": data_inicial, "dataFinal": data_final}
        resposta = requests.get(url, params=parametros, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar_selic():
        dados = Selic.buscar()

        if not dados:
            return

        registro = dados[-1]

        valor_api = Decimal(registro["valor"])
        data_api = datetime.strptime(
            registro["data"], "%d/%m/%Y"
        ).date()

        with conectar():

            ultimo = (
                Selic
                .select()
                .where(Selic.status == True)
                .order_by(Selic.dt_referencia.desc())
                .first()
            )

            # Primeira carga
            if ultimo is None:
                Selic.create(
                    indice=valor_api,
                    status=True,
                    dt_referencia=data_api,
                    dt_atualizacao=datetime.now()
                )

            # Mesma Selic: prolonga a vigência
            elif ultimo.indice == valor_api:
                ultimo.dt_referencia = data_api
                ultimo.dt_atualizacao = datetime.now()
                ultimo.save()

            # Selic mudou: inicia nova vigência
            else:
                Selic.create(
                    indice=valor_api,
                    status=True,
                    dt_referencia=data_api,
                    dt_atualizacao=datetime.now()
                )