import requests
from datetime import datetime, timedelta
from decimal import Decimal
from database.conexao import conectar
from indicadores.indicador import Indicador, IndicadorInfo


class Selic:

    @staticmethod
    def buscar():
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=365)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"

        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def transformar():
        dados_selic = []
        valor_anterior = None

        for registro in Selic.buscar():
            if registro["valor"] != valor_anterior:
                dados_selic.append(registro)
                valor_anterior = registro["valor"]

        return [{"valor": Decimal(registro["valor"]),
                 "status": True,
                 "dt_referencia": datetime.strptime(registro["data"], "%d/%m/%Y").date()}
            for registro in dados_selic]

    @staticmethod
    def atualizar_selic():
        dados = Selic.transformar()
        if not dados:
            return

        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "SELIC")

            for registro in dados:
                registro["cd_indicador"] = indicador.cd_indicador

            Indicador.insert_many(dados).on_conflict_ignore().execute()