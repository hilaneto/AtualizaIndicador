import requests
from datetime import datetime, timedelta
from decimal import Decimal
from database.conexao import conectar
from indicadores.indicador import Indicador, IndicadorInfo


class Salario:

    @staticmethod
    def buscar():
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=62)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1619/dados"
        parametros = {"formato": "json", "dataInicial": data_inicial, "dataFinal": data_final}

        resposta = requests.get(url, params=parametros, timeout=30)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar():
        dados = Salario.buscar()
        if not dados:
            return 0

        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "SALARIO")

            for registro in dados:
                valor = Decimal(registro["valor"])
                dt_referencia = datetime.strptime(registro["data"], "%d/%m/%Y").date()

                Indicador.insert(
                    cd_indicador=indicador.cd_indicador,
                    valor=valor,
                    status=True,
                    dt_referencia=dt_referencia
                ).on_conflict_ignore().execute()

        return len(dados)