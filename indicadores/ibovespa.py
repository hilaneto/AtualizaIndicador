import os
import requests
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from peewee import Model, AutoField, DecimalField, DateField, DateTimeField, BooleanField
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
    dt_pregao = DateField(null=False)
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

        dt_referencia = datetime.fromisoformat(
            ibov["regularMarketTime"].replace("Z", "+00:00")
        ).astimezone(ZoneInfo("America/Sao_Paulo"))

        return {
            "pontos": Decimal(str(ibov["regularMarketPrice"])),
            "variacao": Decimal(str(ibov["regularMarketChangePercent"])),
            "variacao_pontos": Decimal(str(ibov["regularMarketChange"])),
            "abertura": Decimal(str(ibov["regularMarketOpen"])),
            "maxima": Decimal(str(ibov["regularMarketDayHigh"])),
            "minima": Decimal(str(ibov["regularMarketDayLow"])),
            "fechamento_anterior": Decimal(str(ibov["regularMarketPreviousClose"])),
            "status": True,
            "dt_pregao": dt_referencia.date(),
            "dt_referencia": dt_referencia,
            "dt_atualizacao": datetime.now()
        }

    @staticmethod
    def atualizar():
        dados_api = Ibovespa.buscar()
        ibovespa = Ibovespa.tratar_dados(dados_api)

        with conectar():
            (Ibovespa.insert(**ibovespa)
                .on_conflict(
                    conflict_constraint="uq_tb_ibovespa_pregao",
                    update={
                        Ibovespa.pontos: ibovespa["pontos"],
                        Ibovespa.variacao: ibovespa["variacao"],
                        Ibovespa.variacao_pontos: ibovespa["variacao_pontos"],
                        Ibovespa.abertura: ibovespa["abertura"],
                        Ibovespa.maxima: ibovespa["maxima"],
                        Ibovespa.minima: ibovespa["minima"],
                        Ibovespa.fechamento_anterior: ibovespa["fechamento_anterior"],
                        Ibovespa.dt_referencia: ibovespa["dt_referencia"],
                        Ibovespa.status: ibovespa["status"],
                        Ibovespa.dt_atualizacao: ibovespa["dt_atualizacao"]
                    }
                ).execute())


    @staticmethod
    def carregar_historico(periodo="5y"):
        url = "https://brapi.dev/api/quote/%5EBVSP"
        headers = {"Authorization": f"Bearer {BRAPI_KEY}"}
        params = {"range": periodo, "interval": "1d"}

        resposta = requests.get(url, headers=headers, params=params, timeout=30)
        resposta.raise_for_status()

        historico = resposta.json()["results"][0].get("historicalDataPrice", [])

        if not historico:
            print("Nenhum registro histórico retornado pela BRAPI.")
            return

        fuso = ZoneInfo("America/Sao_Paulo")
        registros = []

        for item in sorted(historico, key=lambda x: x["date"]):
            if item.get("close") is None:
                continue

            dt_referencia = datetime.fromtimestamp(item["date"], tz=fuso)
            pontos = Decimal(str(item["close"]))
            abertura = Decimal(str(item["open"])) if item.get("open") is not None else None
            maxima = Decimal(str(item["high"])) if item.get("high") is not None else None
            minima = Decimal(str(item["low"])) if item.get("low") is not None else None

            registros.append({
                "pontos": pontos,
                "abertura": abertura,
                "maxima": maxima,
                "minima": minima,
                "dt_pregao": dt_referencia.date(),
                "dt_referencia": dt_referencia,
                "dt_atualizacao": datetime.now(),
                "status": True
            })

        with conectar():
            for i, registro in enumerate(registros):
                anterior = registros[i - 1]["pontos"] if i > 0 else None

                if anterior is None or anterior == 0:
                    continue

                registro["fechamento_anterior"] = anterior
                registro["variacao_pontos"] = registro["pontos"] - anterior
                registro["variacao"] = registro["variacao_pontos"] / anterior * 100

                (Ibovespa.insert(**registro)
                    .on_conflict(
                        conflict_constraint="uq_tb_ibovespa_pregao",
                        update={
                            Ibovespa.pontos: registro["pontos"],
                            Ibovespa.variacao: registro["variacao"],
                            Ibovespa.variacao_pontos: registro["variacao_pontos"],
                            Ibovespa.abertura: registro["abertura"],
                            Ibovespa.maxima: registro["maxima"],
                            Ibovespa.minima: registro["minima"],
                            Ibovespa.fechamento_anterior: registro["fechamento_anterior"],
                            Ibovespa.dt_referencia: registro["dt_referencia"],
                            Ibovespa.dt_atualizacao: registro["dt_atualizacao"]
                        }
                    ).execute())

        print(f"Histórico processado: {len(registros) - 1} registros.")            