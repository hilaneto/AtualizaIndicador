import os
import requests
from datetime import datetime
from peewee import Model, AutoField, IntegerField, UUIDField, DateField, CharField, BooleanField, TextField, DateTimeField
from dotenv import load_dotenv
from database.conexao import db
from indicadores.temperatura import Capital

load_dotenv()

class Feriado(Model):
    cd_feriado = AutoField()
    cd_capital = IntegerField()
    id_api = UUIDField()
    dt_feriado = DateField()
    nome = CharField(max_length=150)
    tipo = CharField(max_length=20)
    uf = CharField(max_length=2, null=True)
    codigo_ibge = CharField(max_length=10, null=True)
    bancario = BooleanField(default=False)
    descricao = TextField(null=True)
    dt_atualizacao = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = "tb_feriado"
        indexes = ((("cd_capital", "id_api"), True),)

    # =========================================================
    # Buscar feriados de uma capital
    # =========================================================
    @staticmethod
    def buscar(codigo_ibge, ano=None):
        if ano is None:
            ano = datetime.now().year

        api_key = os.getenv("FERIADOS_API_KEY")

        if not api_key:
            raise ValueError("Variável FERIADOS_API_KEY não encontrada no .env.")

        api_key = api_key.strip()

        url = (f"https://feriadosapi.com/api/v1/feriados/cidade/{codigo_ibge}")

        resposta = requests.get(url, params={"ano": ano}, headers={"Authorization": f"Bearer {api_key}"}, timeout=30)

        # -----------------------------------------------------
        # Erros HTTP
        # -----------------------------------------------------
        try:
            resposta.raise_for_status()

        except requests.HTTPError as erro:
            print("\nErro ao consultar Feriados API")
            print(f"URL: {resposta.url}")
            print(f"Status: {resposta.status_code}")
            print(f"Resposta: {resposta.text[:500]}")
            raise erro

        # -----------------------------------------------------
        # Converter resposta para JSON
        # -----------------------------------------------------
        try:
            dados = resposta.json()

        except requests.exceptions.JSONDecodeError:
            print("\nResposta da API não é JSON.")
            print(f"URL: {resposta.url}")
            print(f"Status: {resposta.status_code}")
            print("Content-Type:", resposta.headers.get("Content-Type"))
            print(f"Resposta: {resposta.text[:1000]}")
            raise

        # -----------------------------------------------------
        # Validar estrutura
        # -----------------------------------------------------
        if "feriados" not in dados:
            raise ValueError("Resposta da API não contém a chave 'feriados'.")

        # -----------------------------------------------------
        # Padronizar dados
        # -----------------------------------------------------
        feriados = []
        for item in dados["feriados"]:
            feriados.append(
                {"id_api": item["id"],
                 "dt_feriado": datetime.strptime(item["data"],"%d/%m/%Y").date(),
                 "nome": item["nome"],
                 "tipo": item["tipo"],
                 "uf": item.get("uf"),
                 "codigo_ibge": item.get("codigo_ibge"),
                 "bancario": item.get("bancario", False),
                 "descricao": item.get("descricao")})

        return feriados

    @staticmethod
    def atualizar_feriado():

        # =========================================================
        # Somente capitais reais
        # 100 = Brasil
        # 101 = Estado
        # =========================================================
        capitais = (Capital.select().where(Capital.cd_capital < 100).order_by(Capital.cd_capital))

        # =========================================================
        # Controle de duplicidade durante a execução
        # =========================================================
        feriados_nacionais = set()
        feriados_estaduais = set()

        # =========================================================
        # Percorrer as capitais
        # =========================================================
        for capital in capitais:
            print(f"Buscando: {capital.cidade} "
                  f"({capital.cd_ibge})"
                 )

            dados_api = Feriado.buscar(codigo_ibge=capital.cd_ibge)

            # =====================================================
            # Percorrer feriados retornados pela API
            # =====================================================
            for feriado in dados_api:
                dt_feriado = feriado["dt_feriado"]
                nome = feriado["nome"]
                tipo = feriado["tipo"]
                tipo_normalizado = tipo.strip().lower()

                # =================================================
                # FERIADO NACIONAL
                # =================================================
                if tipo_normalizado == "nacional":
                    chave = (dt_feriado,nome)

                    # Já processado nesta execução
                    if chave in feriados_nacionais:
                        continue
                    feriados_nacionais.add(chave)
                    cd_capital = 100
                    uf = "BR"
                    codigo_ibge = None

                # =================================================
                # FERIADO ESTADUAL
                # =================================================
                elif tipo_normalizado == "estadual":

                    # UF do próprio estado
                    uf = capital.uf
                    chave = (uf, dt_feriado, nome)

                    # Já processado para esta UF
                    if chave in feriados_estaduais:
                        continue

                    feriados_estaduais.add(chave)
                    cd_capital = 101
                    codigo_ibge = None

                # =================================================
                # FERIADO MUNICIPAL
                # =================================================
                else:
                    cd_capital = capital.cd_capital
                    uf = capital.uf
                    codigo_ibge = str(capital.cd_ibge)

                # =================================================
                # Dados para gravação
                # =================================================
                dados = {"cd_capital": cd_capital,
                         "id_api": feriado["id_api"],
                         "dt_feriado": dt_feriado,
                         "nome": nome,
                         "tipo": tipo,
                         "uf": uf,
                         "codigo_ibge": codigo_ibge,
                         "bancario": feriado["bancario"],
                         "descricao": feriado["descricao"],
                         "dt_atualizacao": datetime.now()
                        }

                # =================================================
                # INSERT / UPDATE
                # =================================================
                (Feriado.insert(**dados)
                        .on_conflict(
                         conflict_target=[Feriado.cd_capital, Feriado.id_api],
                         preserve=[Feriado.dt_feriado,
                                   Feriado.nome,
                                   Feriado.tipo,
                                   Feriado.uf,
                                   Feriado.codigo_ibge,
                                   Feriado.bancario,
                                   Feriado.descricao,
                                   Feriado.dt_atualizacao
                                  ]).execute()
                )