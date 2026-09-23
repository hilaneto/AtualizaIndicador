import requests
from datetime import datetime, timedelta
from peewee import Model, AutoField, DecimalField, DateTimeField, DateField, BooleanField
from database.conexao import db, conectar

class Selic(Model):
    cd_selic = AutoField()
    indice = DecimalField(max_digits=8, decimal_places=5)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_selic"


    @staticmethod
    def buscar():
        hoje = datetime.now()
        data_inicial = (hoje - timedelta(days=365)).strftime("%d/%m/%Y")
        data_final = hoje.strftime("%d/%m/%Y")

        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"

        # Gera dados brutos
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados_brutos = resposta.json() # lista de dicionários
        return dados_brutos


    @staticmethod
    def transformar():
        # Exlui duplicidade diária
        dados_selic = []
        valor_anterior = None
        dados_brutos = Selic.buscar()
        for registro in dados_brutos:
            if registro["valor"] != valor_anterior:
                dados_selic.append(registro)
                valor_anterior = registro["valor"]

        # Transforma dados para o formato da tabela Selic
        registro_selic=[]
        for registro in dados_selic:
            registro_selic.append({"indice": registro["valor"],
                                   "status": True,
                                   "dt_referencia": datetime.strptime(registro["data"], "%d/%m/%Y").date()
                                  })
        return registro_selic


    @staticmethod
    def atualizar_selic():
        dados = Selic.transformar()

        if not dados:
            return

        with conectar():
            Selic.insert_many(dados).on_conflict_ignore().execute()            