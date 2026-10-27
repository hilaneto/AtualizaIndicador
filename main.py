import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from indicadores.dolar import Dolar
from indicadores.euro import Euro
from indicadores.bitcoin import Bitcoin
from indicadores.ipca import Ipca
from indicadores.inpc import Inpc
from indicadores.cdi import Cdi
from indicadores.tr import Tr
from indicadores.selic import Selic
from indicadores.igpm import Igpm
from indicadores.salario import Salario
from indicadores.temperatura import Temperatura
from indicadores.feriado import Feriado
from indicadores.ibovespa import Ibovespa
from indicadores.pib_variacao import Pib_Variacao
from indicadores.pib_valores import Pib_Valores
from indicadores.populacao import Populacao


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
    executar_atualizacao("Dólar", Dolar.atualizar)
    executar_atualizacao("Euro", Euro.atualizar)
    executar_atualizacao("IPCA", Ipca.atualizar)
    executar_atualizacao("INPC", Inpc.atualizar)
    executar_atualizacao("CDI", Cdi.atualizar)
    executar_atualizacao("TR", Tr.atualizar)
    executar_atualizacao("Selic", Selic.atualizar)
    executar_atualizacao("Igpm", Igpm.atualizar)
    executar_atualizacao("Salário mínimo", Salario.atualizar)
    executar_atualizacao("Ibovespa", Ibovespa.atualizar)
    
def atualizar_24h7():
    executar_atualizacao("Bitcoin", Bitcoin.atualizar)
    executar_atualizacao("Temperatura", Temperatura.atualizar)

def atualizar_anual():
    executar_atualizacao("Feriados", Feriado.atualizar)

def atualizar_ibge():
    executar_atualizacao("PIB - Variação", Pib_Variacao.atualizar)
    executar_atualizacao("PIB - Valores", Pib_Valores.atualizar)
    executar_atualizacao("População", Populacao.atualizar)

def main():
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

    # Indicadores: segunda a sexta, 08:00 às 19:30
    scheduler.add_job(atualizar_seg_sex, trigger="cron", day_of_week="mon-fri", hour="8-19", minute="0,30",)

    # Bitcoin e temperatura: todos os dias, minutos 00 e 30
    scheduler.add_job(atualizar_24h7, trigger="cron", minute="0,30",)

    # Feriados: 31 de dezembro, às 08:00
    scheduler.add_job(atualizar_anual, trigger="cron", month=12, day=31, hour=8, minute=0,)

    # PIB e População: primeiro dia de cada mês, às 08:15
    scheduler.add_job(atualizar_ibge, trigger="cron", day=1, hour=8, minute=15)

    try:
        logger.info("Programa iniciado.")
        logger.info("Executando atualizações iniciais.")

        atualizar_seg_sex()
        atualizar_24h7()

        logger.info("Iniciando scheduler.")
        logger.info("Indicadores: seg-sex, das 08:00 às 19:30.")
        logger.info("Bitcoin e temperatura: 24/7, a cada 30 minutos.")
        logger.info("Feriados: 31/12, às 08:00.")

        logger.info("PIB e População: dia 1 de cada mês, às 08:15.")

        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler encerrado.")

    except Exception:
        logger.exception("Erro fatal no programa.")
        raise

if __name__ == "__main__":
    main()