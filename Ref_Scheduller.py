
from apscheduler.schedulers.blocking import BlockingScheduler
from indicadores.dolar import atualizar_dolar

scheduler = BlockingScheduler()

def atualizar_indicadores():
    atualizar_dolar()

# A cada 30 minutos, contando a partir da inicialização
scheduler.add_job( atualizar_indicadores, trigger="interval", minutes=30 )

# A cada 1 horas, contando a partir da inicialização
scheduler.add_job( atualizar_indicadores, trigger="interval", hours=1)

# A cada hora cheia: 08:00, 09:00, 10:00...
scheduler.add_job( atualizar_indicadores, trigger="cron", minute=0 )

# A cada hora cheia, somente entre 07:00 e 22:00
scheduler.add_job( atualizar_indicadores, trigger="cron", hour="7-22", minute=0 )

# Segunda a sexta, entre 08:00 e 19:30, a cada 30 minutos
scheduler.add_job( atualizar_indicadores, trigger="cron", day_of_week="mon-fri", hour="8-19", minute="0,30" )
