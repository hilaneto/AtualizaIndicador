import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from indicadores.dolar import Dolar
from indicadores.euro import Euro
from indicadores.bitcoin import Bitcoin
from indicadores.ipca import Ipca
from indicadores.selic import Selic
from indicadores.salario import Salario
from indicadores.temperatura import Temperatura
from indicadores.feriado import Feriado

# Log: arquivo no diretório de trabalho do programa
logging.basicConfig(filename="atualizador.log",
                    encoding="utf-8",
                    level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",)

logger = logging.getLogger(__name__)

def executar_atualizacao(nome, funcao):
    logger.info("Iniciando atualização: %s", nome)

    try:
        funcao()
    except Exception:
        logger.exception("Falha na atualização: %s", nome)
    else:
        logger.info("Atualização finalizada sem exceções: %s", nome)

def atualizar_seg_sex():
    executar_atualizacao("Dólar", Dolar.atualizar_dolar)
    executar_atualizacao("Euro", Euro.atualizar_euro)
    executar_atualizacao("IPCA", Ipca.atualizar_ipca)
    executar_atualizacao("Selic", Selic.atualizar_selic)
    executar_atualizacao("Salário mínimo", Salario.atualizar_salario)

def atualizar_24h7():
    executar_atualizacao("Bitcoin", Bitcoin.atualizar_bitcoin)
    executar_atualizacao("Temperatura", Temperatura.atualizar_temperatura)

def atualizar_anual():
    executar_atualizacao("Feriados", Feriado.atualizar_feriado)

def main():
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

    # Indicadores: segunda a sexta, 08:00 às 19:30
    scheduler.add_job(atualizar_seg_sex, trigger="cron", day_of_week="mon-fri", hour="8-19", minute="0,30",)

    # Bitcoin e temperatura: todos os dias, minutos 00 e 30
    scheduler.add_job(atualizar_24h7, trigger="cron", minute="0,30",)

    # Feriados: 31 de dezembro, às 08:00
    scheduler.add_job(atualizar_anual, trigger="cron", month=12, day=31, hour=8, minute=0,)

    try:
        logger.info("Programa iniciado.")
        logger.info("Executando atualizações iniciais.")

        atualizar_seg_sex()
        atualizar_24h7()

        logger.info("Iniciando scheduler.")
        logger.info("Indicadores: seg-sex, das 08:00 às 19:30.")
        logger.info("Bitcoin e temperatura: 24/7, a cada 30 minutos.")
        logger.info("Feriados: 31/12, às 08:00.")

        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler encerrado.")

    except Exception:
        logger.exception("Erro fatal no programa.")
        raise


if __name__ == "__main__":
    main()