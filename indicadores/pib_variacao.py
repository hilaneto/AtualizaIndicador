import requests
from datetime import date
from decimal import Decimal
from database.conexao import conectar
from indicadores.indicador import Indicador, IndicadorInfo


class Pib_Variacao:

    @staticmethod
    def buscar():
        url = "https://apisidra.ibge.gov.br/values/t/5932/n1/1/v/6561/p/all/c11255/90707"
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()
        return resposta.json()[1:]

    @staticmethod
    def data_trimestre(codigo):
        ano = int(codigo[:4])
        trimestre = int(codigo[4:])
        return date(ano, trimestre * 3, (31, 30, 30, 31)[trimestre - 1])

    @staticmethod
    def atualizar():
        dados = Pib_Variacao.buscar()
        registros = []

        for item in dados:
            if item["V"] in ("...", "-", ""):
                continue

            registros.append({
                "valor": Decimal(item["V"]),
                "dt_referencia": Pib_Variacao.data_trimestre(item["D3C"]),
                "status": True
            })

        if not registros:
            return 0

        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "PIB")

            for registro in registros:
                registro["cd_indicador"] = indicador.cd_indicador

            for i in range(0, len(registros), 100):
                Indicador.insert_many(registros[i:i + 100]).on_conflict_ignore().execute()

        return len(registros)

    @staticmethod
    def atual():
        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "PIB")

            return (Indicador.select()
                    .where((Indicador.cd_indicador == indicador.cd_indicador) &
                           (Indicador.status == True))
                    .order_by(Indicador.dt_referencia.desc())
                    .first())