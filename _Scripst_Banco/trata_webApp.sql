

select * from tb_capital; 			-- popular manualmente
select * from tb_estacao_capital; 	-- popular manualmente
select * from tb_feriado; 			-- popular manualmente
select * from tb_ipca;
select * from tb_moeda;
select * from tb_salariominimo;
select * from tb_selic;
select * from tb_temperatura;

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

