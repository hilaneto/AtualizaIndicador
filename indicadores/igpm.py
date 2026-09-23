import requests
from datetime import datetime
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Igpm(Model):
    cd_igpm = AutoField()
    indice = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_igpm"

    @staticmethod
    def buscar(ultimos=12):
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados/ultimos/{ultimos}?formato=json"
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar_igpm():
        dados = Igpm.buscar(12)
        if not dados:
            return

        with conectar():
            for registro in dados:
                indice = Decimal(registro["valor"])
                dt_referencia = datetime.strptime(registro["data"], "%d/%m/%Y").date()
                Igpm.insert(indice=indice, status=True, dt_referencia=dt_referencia).on_conflict_ignore().execute()