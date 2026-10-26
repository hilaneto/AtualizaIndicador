import requests
from datetime import datetime
from decimal import Decimal
from database.conexao import conectar
from indicadores.indicador import Indicador, IndicadorInfo


class Inpc:

    @staticmethod
    def buscar(ultimos=6):
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.188/dados/ultimos/{ultimos}?formato=json"
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar_inpc():
        dados = Inpc.buscar(6)
        if not dados:
            return

        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "INPC")

            for registro in dados:
                valor = Decimal(registro["valor"])
                dt_referencia = datetime.strptime(registro["data"], "%d/%m/%Y").date()

                Indicador.insert(
                    cd_indicador=indicador.cd_indicador,
                    valor=valor,
                    status=True,
                    dt_referencia=dt_referencia
                ).on_conflict_ignore().execute()