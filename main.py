from apscheduler.schedulers.blocking import BlockingScheduler
from indicadores.dolar import Dolar
from indicadores.euro import Euro
from indicadores.bitcoin import Bitcoin
from indicadores.ipca import Ipca
from indicadores.selic import Selic
from indicadores.salario import Salario

def atualizar_indicadores():
    Dolar.atualizar_dolar()
    Euro.atualizar_euro()
    Ipca.atualizar_ipca()
    Selic.atualizar_selic()
    Salario.atualizar_salario()

def atualizar_bitcoin():
    Bitcoin.atualizar_bitcoin()

def main():

    scheduler = BlockingScheduler()

    # Indicadores: segunda a sexta, 08:00 às 19:30
    scheduler.add_job(atualizar_indicadores, trigger="cron", day_of_week="mon-fri", hour="8-19", minute="0,30" )

    # Bitcoin: 24 horas / 7 dias
    scheduler.add_job(atualizar_bitcoin, trigger="cron", minute="0,30")

    print("Scheduler iniciado.")
    print("Indicadores: seg-sex, das 08:00 às 19:30.")
    print("Bitcoin: 24/7, a cada 30 minutos.")

    atualizar_indicadores()
    atualizar_bitcoin()

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        print("Scheduler encerrado.")

if __name__ == "__main__":
    main()