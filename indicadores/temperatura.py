import requests

from datetime import datetime, timezone, timedelta

from peewee import (
    Model,
    AutoField,
    ForeignKeyField,
    DecimalField,
    DateTimeField,
    BooleanField,
    CharField
)

from database.conexao import db, conectar


# ==============================================================
# CAPITAL
# ==============================================================
class Capital(Model):

    cd_capital = AutoField()
    cidade = CharField(max_length=50)
    cidade_busca = CharField(max_length=50)
    uf = CharField(max_length=2)
    regiao = CharField(max_length=20)
    cd_ibge = CharField(max_length=7)

    class Meta:
        database = db
        table_name = "tb_capital"


# ==============================================================
# ESTAÇÃO DA CAPITAL
# ==============================================================
class EstacaoCapital(Model):

    cd_estacao = AutoField()

    capital = ForeignKeyField(
        Capital,
        field=Capital.cd_capital,
        column_name="cd_capital",
        backref="estacoes"
    )

    wigos = CharField(
        max_length=60,
        unique=True
    )

    nome_estacao = CharField(
        max_length=100
    )

    status = BooleanField(
        default=True
    )

    class Meta:
        database = db
        table_name = "tb_estacao_capital"


# ==============================================================
# TEMPERATURA
# ==============================================================
class Temperatura(Model):

    cd_temperatura = AutoField()

    capital = ForeignKeyField(
        Capital,
        field=Capital.cd_capital,
        column_name="cd_capital",
        backref="temperaturas"
    )

    temperatura = DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True
    )

    dt_referencia = DateTimeField()

    dt_atualizacao = DateTimeField(
        default=datetime.now
    )

    status = BooleanField(
        default=True
    )

    class Meta:
        database = db
        table_name = "tb_temperatura"

        indexes = (
            (("capital", "dt_referencia"), True),
        )

    # ==========================================================
    # CARREGAR ESTAÇÕES ATIVAS
    # ==========================================================
    @staticmethod
    def carregar_estacoes():

        with conectar():

            consulta = (
                EstacaoCapital
                .select(
                    EstacaoCapital.wigos,
                    EstacaoCapital.capital
                )
                .where(
                    EstacaoCapital.status == True
                )
            )

            estacoes = {
                registro.wigos:
                    registro.capital.cd_capital

                for registro in consulta
            }

        return estacoes

    # ==========================================================
    # CARREGAR CAPITAIS
    # ==========================================================
    @staticmethod
    def carregar_capitais():

        with conectar():

            capitais = list(
                Capital.select()
            )

        return capitais

    # ==========================================================
    # BUSCAR TEMPERATURAS
    # ==========================================================
    @staticmethod
    def buscar():

        estacoes = Temperatura.carregar_estacoes()
        capitais = Temperatura.carregar_capitais()

        agora = datetime.now(timezone.utc)

        # Janela de busca no INMET
        inicio = agora - timedelta(hours=24)

        url = (
            "https://wis2bra.inmet.gov.br/"
            "oapi/collections/"
            "urn:wmo:md:br-inmet:synop/items"
        )

        parametros = {
            "f": "json",
            "limit": 1000,
            "datetime": (
                f"{inicio.isoformat()}/"
                f"{agora.isoformat()}"
            )
        }

        temperaturas_capitais = {}

        while url:

            resposta = requests.get(
                url,
                params=parametros,
                timeout=30
            )

            resposta.raise_for_status()

            dados = resposta.json()

            for observacao in dados.get(
                "features",
                []
            ):

                propriedades = observacao.get(
                    "properties",
                    {}
                )

                # ----------------------------------------------
                # Apenas temperatura do ar
                # ----------------------------------------------
                if (
                    propriedades.get("name")
                    != "air_temperature"
                ):
                    continue

                wigos = propriedades.get(
                    "wigos_station_identifier"
                )

                # Descobre a qual capital
                # pertence a estação
                cd_capital = estacoes.get(
                    wigos
                )

                if cd_capital is None:
                    continue

                valor = propriedades.get(
                    "value"
                )

                dt_referencia = propriedades.get(
                    "phenomenonTime"
                )

                if (
                    valor is None
                    or not dt_referencia
                ):
                    continue

                dt_referencia = (
                    datetime.fromisoformat(
                        dt_referencia.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                temperatura_atual = (
                    temperaturas_capitais.get(
                        cd_capital
                    )
                )

                # ----------------------------------------------
                # Mantém apenas a observação mais recente
                # de cada capital
                # ----------------------------------------------
                if (
                    temperatura_atual is None

                    or

                    dt_referencia
                    > temperatura_atual[
                        "dt_referencia"
                    ]
                ):

                    temperaturas_capitais[
                        cd_capital
                    ] = {

                        "cd_capital":
                            cd_capital,

                        "temperatura":
                            valor,

                        "dt_referencia":
                            dt_referencia,

                        "status":
                            True
                    }

            # ----------------------------------------------
            # Próxima página da API
            # ----------------------------------------------
            proximo = next(
                (
                    link.get("href")

                    for link in dados.get(
                        "links",
                        []
                    )

                    if link.get("rel")
                    == "next"
                ),
                None
            )

            url = proximo

            # A URL da próxima página já
            # contém os parâmetros
            parametros = None

        # ======================================================
        # GARANTIR AS 27 CAPITAIS NO RESULTADO
        # ======================================================
        resultado = []

        for capital in capitais:

            registro = (
                temperaturas_capitais.get(
                    capital.cd_capital
                )
            )

            if registro:

                resultado.append(
                    registro
                )

            else:

                resultado.append({
                    "cd_capital":
                        capital.cd_capital,

                    "temperatura":
                        None,

                    "dt_referencia":
                        agora,

                    "status":
                        False
                })

        return resultado

    # ==========================================================
    # ATUALIZAR TB_TEMPERATURA
    # ==========================================================
    @staticmethod
    def atualizar_temperatura():

        temperaturas = (
            Temperatura.buscar()
        )

        agora = datetime.now()

        with conectar():

            for registro in temperaturas:

                (
                    Temperatura
                    .insert(
                        capital=
                            registro[
                                "cd_capital"
                            ],

                        temperatura=
                            registro[
                                "temperatura"
                            ],

                        dt_referencia=
                            registro[
                                "dt_referencia"
                            ],

                        dt_atualizacao=
                            agora,

                        status=
                            registro[
                                "status"
                            ]
                    )

                    .on_conflict(
                        conflict_target=[
                            Temperatura.capital,
                            Temperatura.dt_referencia
                        ],

                        update={
                            Temperatura.temperatura:
                                registro[
                                    "temperatura"
                                ],

                            Temperatura.dt_atualizacao:
                                agora,

                            Temperatura.status:
                                registro[
                                    "status"
                                ]
                        }
                    )

                    .execute()
                )

        return len(temperaturas)