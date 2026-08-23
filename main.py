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
    Bitcoin.atualizar_bitcoin()
    Ipca.atualizar_ipca()
    Selic.atualizar_selic()
    Salario.atualizar_salario()

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