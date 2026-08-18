import requests
from datetime import datetime
from peewee import Model, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar

class Ipca(Model):
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
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

def atualizar_ipca():
    pass
