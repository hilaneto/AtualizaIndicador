
import requests
from datetime import datetime, date
from peewee import Model, BigAutoField, IntegerField, CharField, DecimalField, DateField, DateTimeField
from database.conexao import db, conectar


class Pib_Valores(Model):
    cd_pib_valor = BigAutoField()
    cd_setor = IntegerField()
    nm_setor = CharField(max_length=150)
    valor_milhoes = DecimalField(max_digits=18, decimal_places=2)
    dt_referencia = DateField()
    dt_atualizacao = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = "tb_pib_valores"

    @staticmethod
    def buscar():
        url = "https://apisidra.ibge.gov.br/values/t/1846/n1/1/v/585/p/all/c11255/all"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()[1:]

    @staticmethod
    def atualizar():
        dados = Pib_Valores.buscar()
        registros = []

        for item in dados:
            if item["V"].isdigit():
                trimestre = item["D3C"]
                mes = int(trimestre[-2:]) * 3

                registros.append({
                    "cd_setor": int(item["D4C"]),
                    "nm_setor": item["D4N"],
                    "valor_milhoes": int(item["V"]),
                    "dt_referencia": date(int(trimestre[:4]), mes, 1)
                })

        if not registros:
            return 0

        with conectar():
            for i in range(0, len(registros), 100):
                Pib_Valores.insert_many(registros[i:i + 100]).on_conflict_ignore().execute()

        return len(registros)

    @staticmethod
    def atual():
        with conectar():
            return (Pib_Valores.select()
                    .where(Pib_Valores.cd_setor == 90707)
                    .order_by(Pib_Valores.dt_referencia.desc())
                    .first())
