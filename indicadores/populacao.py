
import requests
from datetime import datetime, date
from peewee import Model, AutoField, BigIntegerField, BooleanField, DateField, DateTimeField
from database.conexao import db, conectar


class Populacao(Model):
    cd_populacao = AutoField()
    populacao = BigIntegerField()
    status = BooleanField(default=True)
    dt_referencia = DateField()
    dt_atualizacao = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = "tb_populacao"

    @staticmethod
    def buscar():
        url = "https://apisidra.ibge.gov.br/values/t/6579/n1/1/v/9324/p/all"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()[1:]

    @staticmethod
    def atualizar():
        dados = Populacao.buscar()
        registros = []
        for item in dados:
            if item["V"].isdigit():
                registros.append({
                    "populacao": int(item["V"]),
                    "dt_referencia": date(int(item["D3C"]), 7, 1)
                })

        if not registros:
            return 0

        with conectar():
            for i in range(0, len(registros), 100):
                Populacao.insert_many(registros[i:i + 100]).on_conflict_ignore().execute()
        return len(registros)

    @staticmethod
    def atual():
        with conectar():
            return (Populacao.select()
                    .where(Populacao.status == True)
                    .order_by(Populacao.dt_referencia.desc())
                    .first())
