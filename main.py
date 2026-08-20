from apscheduler.schedulers.blocking import BlockingScheduler
from indicadores.dolar import Dolar
from indicadores.ipca import Ipca

def atualizar_indicadores():
    Dolar.atualizar_dolar()
    Ipca.atualizar_ipca

def main():
    scheduler = BlockingScheduler()
    scheduler.add_job( atualizar_indicadores, trigger="cron", day_of_week="mon-fri", hour="8-19", minute="0,30" )
    print("Scheduler iniciado.")
    print("Atualização dos indicadores a cada 30 minutos.")
    atualizar_indicadores()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler encerrado.")

if __name__ == "__main__":
    main()