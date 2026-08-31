import requests
from peewee import Model, AutoField, CharField, BooleanField, ForeignKeyField
from database.conexao import db, conectar

# ============================================================
# MODELO CAPITAL
# ============================================================
class Capital(Model):
    cd_capital = AutoField()
    cidade = CharField(max_length=50)
    cidade_busca = CharField(max_length=50)
    uf = CharField(max_length=2)
    regiao = CharField(max_length=20)
    cd_ibge = CharField(max_length=7, unique=True)

    class Meta:
        database = db
        table_name = "tb_capital"

# ============================================================
# MODELO ESTAÇÃO x CAPITAL
# ============================================================
class EstacaoCapital(Model):
    cd_estacao = AutoField()
    capital = ForeignKeyField(Capital, field=Capital.cd_capital, column_name="cd_capital", backref="estacoes")
    wigos = CharField(max_length=60, unique=True)
    nome_estacao = CharField(max_length=100)
    status = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "tb_estacao_capital"

# ============================================================
# CRUD ESTAÇÃO
# ============================================================
class CrudEstacao:
    URL_ESTACOES = ("https://wis2bra.inmet.gov.br/oapi/collections/stations/items")

    # --------------------------------------------------------
    # Buscar estações no INMET
    # --------------------------------------------------------
    @staticmethod
    def buscar_estacoes_inmet():
        estacoes = []
        url = CrudEstacao.URL_ESTACOES
        parametros = {"limit": 1000}

        while url:
            response = requests.get(url, params=parametros, timeout=30)
            response.raise_for_status()
            dados = response.json()
            estacoes.extend(dados.get("features", []))
            proxima_pagina = None

            for link in dados.get("links", []):
                if link.get("rel") == "next":
                    proxima_pagina = link.get("href")
                    break

            url = proxima_pagina

            # A URL de "next" já contém os parâmetros
            parametros = None
        return estacoes

    # --------------------------------------------------------
    # Associar estações às capitais
    # --------------------------------------------------------
    @staticmethod
    def associar_estacoes_capitais():
        estacoes_api = (CrudEstacao.buscar_estacoes_inmet())

        with conectar():
            capitais = list(Capital.select())

        estacoes = []

        for capital in capitais:
            codigo_ibge = (capital.cd_ibge.strip())

            # Dois primeiros dígitos do código IBGE
            # representam a UF
            codigo_uf = codigo_ibge[:2]

            # cidade_busca já está sem acentos
            # e em formato apropriado para pesquisa
            nome_capital = (capital.cidade_busca.upper().strip())

            for item in estacoes_api:
                propriedades = item.get("properties", {})
                wigos = propriedades.get("wigos_station_identifier"                )
                nome_estacao = propriedades.get("name")

                if not wigos or not nome_estacao:
                    continue

                nome_estacao_busca = (nome_estacao.upper().strip())

                # ============================================
                # REGRA 1
                # Código IBGE completo no WIGOS
                # Exemplo São Paulo:
                # IBGE:
                # 3550308
                # WIGOS:
                # 0-76-0-3550308000000089
                # ============================================

                match_ibge = (wigos.startswith(f"0-76-0-{codigo_ibge}"))

                # ============================================
                # REGRA 2
                # Nome completo da capital
                # Exemplos válidos:
                # SAO PAULO
                # SAO PAULO - MIRANTE
                # SAO PAULO (IAG)
                # Exemplos rejeitados:
                # SAO CARLOS
                # SAO MIGUEL ARCANJO
                # SAO SIMAO
                # ============================================

                match_nome = (nome_estacao_busca == nome_capital
                              or
                              nome_estacao_busca.startswith(nome_capital + " ")
                              or
                              nome_estacao_busca.startswith(nome_capital + "-")
                             )

                # ============================================
                # REGRA 3 - FALLBACK
                # Mesmo Estado + nome completo da capital
                # Usado principalmente quando o código
                # municipal da estação não coincide com
                # o código IBGE da capital.
                # ============================================

                match_fallback = (wigos.startswith(f"0-76-0-{codigo_uf}") and match_nome)

                # ============================================
                # ESTAÇÃO VÁLIDA
                # ============================================

                if match_ibge or match_fallback:
                    estacoes.append({"cd_capital":capital.cd_capital,
                                     "wigos":wigos,
                                     "nome_estacao":nome_estacao,
                                     "status":True
                                    })
        return estacoes

    # --------------------------------------------------------
    # Atualizar tb_estacao_capital
    # --------------------------------------------------------
    @staticmethod
    def atualizar_estacoes():
        estacoes = (CrudEstacao.associar_estacoes_capitais())

        with conectar():
            for registro in estacoes:
                (EstacaoCapital.insert(capital=registro["cd_capital"],
                                       wigos=registro["wigos"],
                                       nome_estacao=registro["nome_estacao"],
                                       status=registro["status"]
                                      ).on_conflict(conflict_target=[EstacaoCapital.wigos],
                                        update={EstacaoCapital.capital:registro["cd_capital"],
                                                EstacaoCapital.nome_estacao:registro["nome_estacao"]}
                                    ).execute())
        return len(estacoes)
