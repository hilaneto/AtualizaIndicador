import requests
from datetime import datetime
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Inpc(Model):
    cd_inpc = AutoField()
    indice = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_inpc"

    @staticmethod
    def buscar(ultimos=6):
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.188/dados/ultimos/{ultimos}?formato=json"
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()  # Valida a resposta HTTP; se houver erro, não deixa o código continuar.
        return resposta.json()

    @staticmethod
    def atualizar_inpc():
        dados = Inpc.buscar(6)
        if not dados:
            return

        with conectar():
            for registro in dados:
                indice = Decimal(registro["valor"])
                dt_referencia = datetime.strptime(registro["data"], "%d/%m/%Y").date()
                Inpc.insert(indice=indice, status=True, dt_referencia=dt_referencia).on_conflict_ignore().execute()