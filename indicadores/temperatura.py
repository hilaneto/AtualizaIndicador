
import requests
from peewee import Model, AutoField, CharField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar
from datetime import datetime, timezone, timedelta
from decimal import Decimal

class Temperatura(Model):
    cd_temperatura = AutoField()
    regiao = CharField(max_length=20)
    cidade = CharField(max_length=50)
    temperatura = DecimalField(max_digits=5, decimal_places=2, null=True)
    dt_referencia = DateTimeField(null=True)
    dt_atualizacao = DateTimeField(default=datetime.now)
    status = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "tb_temperatura"
        indexes = ((("cidade", "dt_referencia"), True),)


    @staticmethod
    def buscar():
        url = "https://wis2bra.inmet.gov.br/oapi/collections/stations/items"

        todas_estacoes = []
        capitais_regioes = {
            "BRASILIA": {"cidade": "Brasília", "regiao": "Centro-Oeste"},
            "GOIANIA": {"cidade": "Goiânia", "regiao": "Centro-Oeste"},
            "CUIABA": {"cidade": "Cuiabá", "regiao": "Centro-Oeste"},
            "CAMPO GRANDE": {"cidade": "Campo Grande", "regiao": "Centro-Oeste"},
            "MACEIO": {"cidade": "Maceió","regiao": "Nordeste"},
            "SALVADOR": {"cidade": "Salvador", "regiao": "Nordeste"},
            "FORTALEZA": {"cidade": "Fortaleza", "regiao": "Nordeste"},
            "SAO LUIS": {"cidade": "São Luís", "regiao": "Nordeste"},
            "JOAO PESSOA": {"cidade": "João Pessoa", "regiao": "Nordeste"},
            "RECIFE": {"cidade": "Recife", "regiao": "Nordeste"},
            "TERESINA": {"cidade": "Teresina", "regiao": "Nordeste"},
            "NATAL": {"cidade": "Natal", "regiao": "Nordeste"},
            "ARACAJU": {"cidade": "Aracaju", "regiao": "Nordeste"},
            "RIO BRANCO": {"cidade": "Rio Branco", "regiao": "Norte"},
            "MACAPA": {"cidade": "Macapá", "regiao": "Norte"},
            "MANAUS": {"cidade": "Manaus", "regiao": "Norte"},
            "BELEM": {"cidade": "Belém", "regiao": "Norte"},
            "PORTO VELHO": {"cidade": "Porto Velho", "regiao": "Norte"},
            "BOA VISTA": {"cidade": "Boa Vista", "regiao": "Norte"},
            "PALMAS": {"cidade": "Palmas", "regiao": "Norte"},
            "VITORIA": {"cidade": "Vitória", "regiao": "Sudeste"},
            "BELO HORIZONTE": {"cidade": "Belo Horizonte", "regiao": "Sudeste"},
            "RIO DE JANEIRO": {"cidade": "Rio de Janeiro", "regiao": "Sudeste"},
            "SAO PAULO": {"cidade": "São Paulo", "regiao": "Sudeste"},
            "CURITIBA": {"cidade": "Curitiba", "regiao": "Sul"},
            "PORTO ALEGRE": {"cidade": "Porto Alegre", "regiao": "Sul"},
            "FLORIANOPOLIS": {"cidade": "Florianópolis", "regiao": "Sul"}
        }

        # Estaćões das Capitais -----------------------------------------------------------------------
        while url:
            resposta = requests.get(url, params={"f": "json", "limit": 1000}, timeout=30)
            resposta.raise_for_status()
            dados = resposta.json()
            todas_estacoes.extend(dados["features"])
            url = next( (link["href"]
                        for link in dados.get("links", [])
                        if link.get("rel") == "next"),None)
        estacoes_capitais = {}
        for estacao in todas_estacoes:
            prop = estacao["properties"]
            nome = prop["name"].upper()
            for cidade_busca, capital in capitais_regioes.items():
                if cidade_busca in nome:
                    estacoes_capitais[prop["wigos_station_identifier"]] = {"cidade": capital["cidade"], "regiao": capital["regiao"]}

        # Todas as observaćões -----------------------------------------------------------------------
        url = ("https://wis2bra.inmet.gov.br/oapi/collections/urn:wmo:md:br-inmet:synop/items")

        agora = datetime.now(timezone.utc)
        inicio = agora - timedelta(hours=6)

        todas_observacoes = []

        parametros = {"f": "json", "limit": 1000, "datetime": f"{inicio.isoformat()}/{agora.isoformat()}"}

        while url:
            resposta = requests.get(url, params=parametros, timeout=30)
            resposta.raise_for_status()
            dados = resposta.json()
            todas_observacoes.extend(dados["features"])

            url = next( (link["href"]
                        for link in dados.get("links", [])
                        if link.get("rel") == "next" ), None)

            parametros = None

        # Temperaturas por capitais ---------------------------------------------------------
        temperaturas_capitais = {}

        for obs in todas_observacoes:
            prop = obs["properties"]

            if prop["name"] != "air_temperature":
                continue

            wigos = prop["wigos_station_identifier"]

            capital = estacoes_capitais.get(wigos)

            if capital is None:
                continue

            cidade = capital["cidade"]

            dt_referencia = datetime.fromisoformat(
                prop["phenomenonTime"].replace("Z", "+00:00"))

            nova_temperatura = {
                "regiao": capital["regiao"],
                "cidade": cidade,
                "temperatura": prop["value"],
                "dt_referencia": dt_referencia,
                "status": True}

            temperatura_atual = temperaturas_capitais.get(cidade)

            if (temperatura_atual is None or dt_referencia > temperatura_atual["dt_referencia"]):
                temperaturas_capitais[cidade] = nova_temperatura

        # Capitais sem temperatura disponível
        for capital in capitais_regioes.values():
            cidade = capital["cidade"]
            regiao = capital["regiao"]            
            if cidade not in temperaturas_capitais:
                temperaturas_capitais[cidade] = {
                    "regiao": regiao,
                    "cidade": cidade,
                    "temperatura": None,
                    "dt_referencia": agora,
                    "status": False}
        temperaturas = list(temperaturas_capitais.values())
        return temperaturas

    @staticmethod
    def atualizar_temperatura():

        dados = Temperatura.buscar()

        with conectar():
            for registro in dados:

                temperatura = {"regiao": registro["regiao"],
                               "cidade": registro["cidade"],
                               "temperatura": (Decimal(str(registro["temperatura"]))
                        if registro["temperatura"] is not None else None),
                    "status": registro["status"],
                    "dt_referencia": registro["dt_referencia"],
                    "dt_atualizacao": datetime.now()}

                (Temperatura
                 .insert(**temperatura)
                 .on_conflict(conflict_target=[Temperatura.cidade, Temperatura.dt_referencia],
                 update={Temperatura.regiao: temperatura["regiao"],
                         Temperatura.temperatura: temperatura["temperatura"],
                         Temperatura.status: temperatura["status"],
                         Temperatura.dt_atualizacao: temperatura["dt_atualizacao"]}).execute())
