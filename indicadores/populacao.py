import requests
from datetime import date
from decimal import Decimal
from database.conexao import conectar
from indicadores.indicador import Indicador, IndicadorInfo


class Populacao:

    @staticmethod
    def buscar():
        url = "https://apisidra.ibge.gov.br/values/t/6579/n1/1/v/9324/p/all"
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()
        return resposta.json()[1:]

    @staticmethod
    def atualizar():
        dados = Populacao.buscar()
        registros = []

        for item in dados:
            if item["V"].isdigit():
                registros.append({
                    "valor": Decimal(item["V"]),
                    "dt_referencia": date(int(item["D3C"]), 7, 1),
                    "status": True
                })

        if not registros:
            return 0

        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "POPULACAO")

            for registro in registros:
                registro["cd_indicador"] = indicador.cd_indicador

            for i in range(0, len(registros), 100):
                Indicador.insert_many(registros[i:i + 100]).on_conflict_ignore().execute()

        return len(registros)

    @staticmethod
    def atual():
        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "POPULACAO")

            return (Indicador.select()
                    .where((Indicador.cd_indicador == indicador.cd_indicador) &
                           (Indicador.status == True))
                    .order_by(Indicador.dt_referencia.desc())
                    .first())