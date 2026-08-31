import os
import requests
from datetime import datetime
from peewee import Model, AutoField, IntegerField, UUIDField, DateField, CharField, BooleanField, TextField, DateTimeField
from dotenv import load_dotenv
from database.conexao import db, conectar
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
        indexes = ((("cd_capital", "id_api"),True),)

    # Buscar feriados de uma capital
    @staticmethod
    def buscar(codigo_ibge, ano=None):
        if ano is None:
           ano = datetime.now().year

        api_key = os.getenv("FERIADOS_API_KEY")

        if not api_key:
            raise ValueError("Variável FERIADOS_API_KEYnão encontrada no .env.")

        api_key = api_key.strip()

        url = (f"https://feriadosapi.com/api/v1/feriados/cidade/{codigo_ibge}")

        resposta = requests.get(url,params={"ano": ano}, headers={"Authorization": f"Bearer {api_key}"}, timeout=30)

        # Erros HTTP
        try:
            resposta.raise_for_status()

        except requests.HTTPError as erro:
            print("\nErro ao consultar Feriados API")
            print(f"URL: {resposta.url}")
            print(f"Status: {resposta.status_code}")
            print(f"Resposta: {resposta.text[:500]}")
            raise erro

        # Converter resposta para JSON
        try:
            dados = resposta.json()
        except requests.exceptions.JSONDecodeError:
            print("\nResposta da API não é JSON.")
            print(f"URL: {resposta.url}")
            print(f"Status: {resposta.status_code}")
            print("Content-Type:", resposta.headers.get("Content-Type"))
            print(f"Resposta: {resposta.text[:1000]}")
            raise

        # Validar estrutura
        if "feriados" not in dados:
            raise ValueError("Resposta da API não contém a chave 'feriados'.")

        # Padronizar dados
        feriados = []
        for item in dados["feriados"]:
            feriados.append({"id_api":item["id"],
                             "dt_feriado":datetime.strptime(item["data"], "%d/%m/%Y").date(),
                             "nome":item["nome"],
                             "tipo":item["tipo"],
                             "uf":item.get("uf"),
                             "codigo_ibge":item.get("codigo_ibge"),
                             "bancario":item.get("bancario",False),
                             "descricao":item.get("descricao")})
        return feriados

    # =========================================================
    # Atualizar feriados das 27 capitais
    # Sempre ano corrente
    # =========================================================
    @staticmethod
    def atualizar_feriado():
        ano = datetime.now().year

        # Buscar capitais
        with conectar():
            capitais = list(Capital.select().order_by(Capital.cidade))

        if not capitais:
            raise ValueError("Nenhuma capital encontrada na tb_capitais.")

        total = 0

        # Percorrer as 27 capitais
        for capital in capitais:
            print(f"Buscando: "
                  f"{capital.cidade} "
                  f"({capital.cd_ibge})"            )
            try:
                dados = Feriado.buscar(codigo_ibge=capital.cd_ibge, ano=ano)

            except Exception as erro:
                print(f"Erro em {capital.cidade}: "
                      f"{erro}")

                # Não interrompe as demais capitais
                continue

            # Gravar no PostgreSQL
            with conectar():
                for registro in dados:
                    registro["cd_capital"] = (capital.cd_capital)
                    agora = datetime.now()
                    (Feriado.insert(**registro, dt_atualizacao=agora).on_conflict(
                            conflict_target=[Feriado.cd_capital, Feriado.id_api],
                            update={Feriado.dt_feriado:registro["dt_feriado"],
                                    Feriado.nome:registro["nome"],
                                    Feriado.tipo:registro["tipo"],
                                    Feriado.uf:registro["uf"],
                                    Feriado.codigo_ibge:registro["codigo_ibge"],
                                    Feriado.bancario:registro["bancario"],
                                    Feriado.descricao:registro["descricao"],
                                    Feriado.dt_atualizacao:agora
                                    }).execute())
                    total += 1

            print(f"{capital.cidade}: "
                  f"{len(dados)} feriados.")

        # Resultado
        print()
        print("========================================")
        print(f"Feriados de {ano} atualizados.")
        print(f"Capitais processadas: "
              f"{len(capitais)}")
        print(f"Total de registros processados: "
              f"{total}")
        print("========================================")