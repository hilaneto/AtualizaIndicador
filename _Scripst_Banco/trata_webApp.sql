

select * from tb_capital; 			-- popular manualmente
select * from tb_estacao_capital; 	-- popular manualmente
select * from tb_feriado; 			-- popular manualmente
select * from tb_ipca;
select * from tb_moeda;
select * from tb_salariominimo;
select * from tb_selic;
select * from tb_temperatura;
select * from tb_usuario;
select * from tb_contato;

select cd_feriado, b.cd_capital, b.cidade, a.dt_feriado , nome, tipo, b.uf, bancario, descricao, dt_atualizacao
from tb_feriado a left join tb_capital b
on a.cd_capital = b.cd_capital

select * from tb_feriado
where tipo = 'NACIONAL'

select * from tb_feriado
where nome = 'Sexta-feira Santa'


select * from tb_capital
where cd_capital = 3

select * from vw_temperatura_atual;

select max(dt_atualizacao) from tb_temperatura

select * from tb_capital;
select * from tb_estacao_capital;
select * from tb_temperatura;
select * from tb_feriado;

select * from tb_feriado
where cd_capital = 15

select * from tb_estacao_capital
where cd_capital = 25

select * from tb_temperatura
where cd_capital = 25



select distinct cd_capital from tb_feriado;

select * from tb_temperatura
where cd_capital = 25


-- -------------------------------------------------------
select * from tb_capital a inner join tb_estacao_capital b
on a.cd_capital = b.cd_capital
inner join tb_temperatura c
on b.cd_capital = c.cd_capital


-- drop view public.vw_temperatura_atual;
CREATE OR REPLACE VIEW public.vw_temperatura_atual as
select a.cd_capital, b.cidade, b.uf, b.regiao, a.temperatura, a.dt_referencia from 
(select a.cd_capital, a.temperatura, a.dt_referencia from tb_temperatura a inner join
(select a.cd_capital, max(a.dt_referencia) as dt_referencia from tb_temperatura a group by a.cd_capital) b
on a.cd_capital = b.cd_capital and a.dt_referencia = b.dt_referencia) a
inner join tb_capital b
on a.cd_capital = b.cd_capital
where a.cd_capital not in (100,101)
order by cidade;
-- --------------------------------
select * from vw_temperatura_atual;



select * from
(select a.cd_capital, max(a.dt_referencia) as dt_referencia from tb_temperatura a inner join tb_capital b
 on a.cd_capital = b.cd_capital
 group by a.cd_capital) a
 inner join
 (select * from tb_temperatura) b
 on a.cd_capital = b.cd_capital 


select cidade, a.temperatura, a.dt_referencia from
(
select a.cd_temperatura, a.cd_capital, a.temperatura, a.dt_referencia from tb_temperatura a
 inner join (select cd_temperatura, max(dt_referencia) as dt_referencia from tb_temperatura group by cd_temperatura) b
 on a.cd_temperatura = b.cd_temperatura
 ) a inner join tb_capital b
 on a.cd_capital = b.cd_capital

where cidade = 'Palmas'

and uf = 'SP'

select b.cd_capital, cidade, max(temperatura) from tb_capital a inner join tb_estacao_capital b
on a.cd_capital = b.cd_capital
inner join tb_temperatura c
on b.cd_capital = c.cd_capital
where a.cd_capital in
(select distinct cd_capital from tb_temperatura where temperatura is null)
group by b.cd_capital, cidade

select * from tb_temperatura

select * from tb_estacao_capital
where cd_capital = 25

SELECT c.cidade, c.uf, e.nome_estacao, e.wigos, e.homologada, e.status
FROM tb_estacao_capital e
JOIN tb_capital c ON c.cd_capital = e.cd_capital
ORDER BY c.cidade, e.nome_estacao;

where cidade = 'VITORIA'

UPDATE tb_temperatura
SET cidade = 'Vitória'
where cidade = 'Vitoria'

where cidade = 'Salvador'




select * from 

show tables

select * from pg_catalog.pg_tables;

SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

SELECT COUNT(*) AS qt_capitais
FROM public.tb_capital;

SELECT
    cd_capital,
    cidade,
    cidade_busca,
    uf,
    regiao,
    cd_ibge
FROM public.tb_capital
ORDER BY cd_capital;


SELECT
    conname,
    conrelid::regclass AS tabela,
    confrelid::regclass AS tabela_referenciada
FROM pg_constraint
WHERE contype = 'f'
  AND connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text;

SELECT
    table_name,
    column_name,
    is_identity,
    identity_generation
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'tb_moeda',
      'tb_ipca',
      'tb_selic',
      'tb_salariominimo',
      'tb_capital',
      'tb_estacao_capital',
      'tb_temperatura',
      'tb_feriado'
  )
  AND is_identity = 'YES'
ORDER BY table_name;

