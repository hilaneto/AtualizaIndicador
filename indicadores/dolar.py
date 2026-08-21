import requests
from datetime import datetime, timedelta
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar
from decimal import Decimal

class Dolar(Model):
    cd_dolar = AutoField()
    valor = DecimalField(max_digits=10, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_dolar"

    @staticmethod
    def buscar():
        # Datas -------------------------------------------------------
        hoje = datetime.now().strftime("%m-%d-%Y")
        
        url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)")
        parametros = {"@moeda":"'USD'" , "@dataCotacao":f"'{hoje}'" , "$format":"json"}
        resposta = requests.get( url, params=parametros, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def tratar_dados(dados_api):
        boletins = dados_api["value"]
        if not boletins:
            raise ValueError("API do Banco Central não retornou cotação.")
        ultimo = boletins[-1]
        return {"valor": Decimal(str(ultimo["cotacaoVenda"])),
                "status": True,
                "dt_referencia": datetime.strptime(
                ultimo["dataHoraCotacao"],
                "%Y-%m-%d %H:%M:%S.%f"),
                "dt_atualizacao": datetime.now()
                }

    @staticmethod
    def atualizar_dolar():
        dados_api = Dolar.buscar()
        dolar = Dolar.tratar_dados(dados_api)
        with conectar():
            (Dolar.insert(**dolar).on_conflict(
                    conflict_target=[Dolar.dt_referencia],
                    update={Dolar.valor: dolar["valor"],
                            Dolar.status: dolar["status"],
                            Dolar.dt_atualizacao: dolar["dt_atualizacao"]}).execute()
            )

