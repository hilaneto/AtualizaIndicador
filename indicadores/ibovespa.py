import os
import requests
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from peewee import Model, AutoField, DecimalField, DateTimeField, BooleanField
from database.conexao import db, conectar
from dotenv import load_dotenv

load_dotenv()
BRAPI_KEY = os.getenv("BRAPI_KEY")


class Ibovespa(Model):
    cd_ibovespa = AutoField()
    pontos = DecimalField(max_digits=12, decimal_places=2)
    variacao = DecimalField(max_digits=8, decimal_places=2)
    variacao_pontos = DecimalField(max_digits=12, decimal_places=2)
    abertura = DecimalField(max_digits=12, decimal_places=2, null=True)
    maxima = DecimalField(max_digits=12, decimal_places=2, null=True)
    minima = DecimalField(max_digits=12, decimal_places=2, null=True)
    fechamento_anterior = DecimalField(max_digits=12, decimal_places=2, null=True)
    status = BooleanField(default=True, null=False)
    dt_referencia = DateTimeField(null=False)
    dt_atualizacao = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db
        table_name = "tb_ibovespa"

    @staticmethod
    def buscar():
        url = "https://brapi.dev/api/quote/%5EBVSP"
        headers = {"Authorization": f"Bearer {BRAPI_KEY}"}
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    @staticmethod
    def tratar_dados(dados_api):
        ibov = dados_api["results"][0]

        dt_referencia = (datetime.fromisoformat(ibov["regularMarketTime"].replace("Z", "+00:00")).astimezone(ZoneInfo("America/Sao_Paulo")))

        return {"pontos": Decimal(str(ibov["regularMarketPrice"])),
                "variacao": Decimal(str(ibov["regularMarketChangePercent"])),
                "variacao_pontos": Decimal(str(ibov["regularMarketChange"])),
                "abertura": Decimal(str(ibov["regularMarketOpen"])),
                "maxima": Decimal(str(ibov["regularMarketDayHigh"])),
                "minima": Decimal(str(ibov["regularMarketDayLow"])),
                "fechamento_anterior": Decimal(str(ibov["regularMarketPreviousClose"])),
                "status": True,
                "dt_referencia": dt_referencia,
                "dt_atualizacao": datetime.now()
                }

    @staticmethod
    def atualizar_ibovespa():
        dados_api = Ibovespa.buscar()
        ibovespa = Ibovespa.tratar_dados(dados_api)

        with conectar():
            (Ibovespa.insert(**ibovespa)
                .on_conflict(
                    conflict_constraint="uq_tb_ibovespa_referencia",
                    update={Ibovespa.pontos: ibovespa["pontos"],
                            Ibovespa.variacao: ibovespa["variacao"],
                            Ibovespa.variacao_pontos: ibovespa["variacao_pontos"],
                            Ibovespa.abertura: ibovespa["abertura"],
                            Ibovespa.maxima: ibovespa["maxima"],
                            Ibovespa.minima: ibovespa["minima"],
                            Ibovespa.fechamento_anterior: ibovespa["fechamento_anterior"],
                            Ibovespa.status: ibovespa["status"],
                            Ibovespa.dt_atualizacao: ibovespa["dt_atualizacao"]
                            }).execute())
