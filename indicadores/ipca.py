import requests
from datetime import datetime
from decimal import Decimal
from database.conexao import conectar
from indicadores.indicador import Indicador, IndicadorInfo


class Ipca:

    @staticmethod
    def buscar(ultimos=12):
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/{ultimos}?formato=json"
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def atualizar_ipca():
        dados = Ipca.buscar(12)
        if not dados:
            return

        with conectar():
            indicador = IndicadorInfo.get(IndicadorInfo.nm_indicador == "IPCA")

            for registro in dados:
                valor = Decimal(registro["valor"])
                dt_referencia = datetime.strptime(registro["data"], "%d/%m/%Y").date()

                Indicador.insert(
                    cd_indicador=indicador.cd_indicador,
                    valor=valor,
                    status=True,
                    dt_referencia=dt_referencia
                ).on_conflict_ignore().execute()