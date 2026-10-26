

SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

select * from tb_usuario;
select * from tb_contato;
select * from tb_logacesso;

select * from tb_contato;
select * from tb_logacesso;
select * from tb_indicador_info;
select * from tb_indicador;
select * from tb_moeda;
select * from tb_ibovespa;
select * from tb_pib_valores;
select * from tb_capital; 			-- popular manualmente
select * from tb_estacao_capital; 	-- popular manualmente
select * from tb_feriado; 			-- popular manualmente
select * from vw_temperatura_atual;

select * from vw_temperatura_atual;



select * from tb_indicador_info;

-- tabelas indicadores únicas ------------------------
select * from tb_moeda;
select * from tb_ibovespa;
select * from tb_temperatura;
select * from tb_pib_valores;

-- tabela indicadores unificada --------------------------------------------
-- ipca, selic, inpc, cdi, tr, igpm, pib_variacao, populacao, salariominimo
-- -------------------------------------------------------------------------

select * from tb_indicador_info;

select * from tb_indicador;

select b.nm_indicador, a.* from tb_indicador a inner join tb_indicador_info b
on a.cd_indicador = b.cd_indicador
where a.cd_indicador in (6)

where a.cd_indicador not in (5,9,6,10,11,7,14,15)


SELECT nm_indicador, COUNT(*) AS registros,
       MIN(h.dt_referencia) AS primeira_data,
       MAX(h.dt_referencia) AS ultima_data
FROM tb_indicador h
JOIN tb_indicador_info i ON i.cd_indicador = h.cd_indicador
WHERE i.nm_indicador in ('INPC','IGPM')
group by nm_indicador;

SELECT i.nm_indicador, COUNT(*) AS registros,
       MIN(h.dt_referencia) AS primeira_data,
       MAX(h.dt_referencia) AS ultima_data
FROM tb_indicador h
JOIN tb_indicador_info i ON i.cd_indicador = h.cd_indicador
WHERE i.nm_indicador = 'IGPM'
GROUP BY i.nm_indicador;

SELECT i.nm_indicador, COUNT(*) AS registros,
       MIN(h.dt_referencia) AS primeira_data,
       MAX(h.dt_referencia) AS ultima_data
FROM tb_indicador h
JOIN tb_indicador_info i ON i.cd_indicador = h.cd_indicador
WHERE i.nm_indicador in ('SALARIO')
GROUP BY i.nm_indicador;

carga_historica("INPC", 188)

SELECT i.nm_indicador, COUNT(*) AS registros,
       MIN(h.dt_referencia) AS primeira_data,
       MAX(h.dt_referencia) AS ultima_data
FROM tb_indicador h
JOIN tb_indicador_info i ON i.cd_indicador = h.cd_indicador
GROUP BY i.nm_indicador
ORDER BY i.nm_indicador;


--TRUNCATE TABLE tb_tr RESTART IDENTITY CASCADE;


-- ====================================================================================
-- Insert tb_indicador_info ----------------------------------------------------------
-- ====================================================================================
INSERT INTO tb_indicador_info
(nm_indicador, titulo, descricao, periodicidade, fonte, url_fonte)
VALUES
('DOLAR_COMERCIAL', 'Dólar Comercial',
 'Cotação do dólar utilizada em operações comerciais e financeiras, como importações, exportações e transações entre instituições. Os valores de compra e venda são apresentados em reais (R$).',
 'Dias úteis', 'Banco Central do Brasil', 'https://www.bcb.gov.br'),

('DOLAR_TURISMO', 'Dólar Turismo',
 'Cotação do dólar utilizada como referência em operações de turismo, como compra de moeda estrangeira para viagens. Os valores de compra e venda são apresentados em reais (R$) e podem variar conforme a instituição.',
 'Dias úteis', 'Fonte de cotações cambiais', NULL),

('EURO', 'Euro',
 'Cotação do euro em relação ao real (EUR/BRL). O euro é a moeda oficial de grande parte dos países da União Europeia e sua cotação varia conforme o mercado de câmbio.',
 'Dias úteis', 'Fonte de cotações cambiais', NULL),

('BITCOIN', 'Bitcoin',
 'Cotação do Bitcoin (BTC), criptoativo digital negociado em mercados globais. Seu preço apresenta oscilações frequentes, inclusive aos finais de semana e feriados.',
 'Contínua', 'Mercado de criptoativos', NULL),

('IPCA', 'Índice Nacional de Preços ao Consumidor Amplo',
 'Principal indicador da inflação oficial brasileira, calculado pelo IBGE. Mede a variação dos preços de produtos e serviços consumidos por famílias com rendimentos de 1 a 40 salários mínimos.',
 'Mensal', 'IBGE', 'https://www.ibge.gov.br'),

('INPC', 'Índice Nacional de Preços ao Consumidor',
 'Indicador de inflação calculado pelo IBGE, que acompanha a variação dos preços de produtos e serviços consumidos por famílias com rendimentos de 1 a 5 salários mínimos.',
 'Mensal', 'IBGE', 'https://www.ibge.gov.br'),

('IGPM', 'Índice Geral de Preços - Mercado',
 'Indicador de inflação calculado pela Fundação Getulio Vargas (FGV). Acompanha variações de preços em diferentes etapas da economia e é frequentemente utilizado no reajuste de contratos, incluindo aluguéis.',
 'Mensal', 'FGV IBRE', 'https://portalibre.fgv.br'),

('IBOVESPA', 'Ibovespa',
 'Principal índice de referência do mercado brasileiro de ações. Representa o desempenho de uma carteira teórica composta por ações e outros ativos de maior representatividade negociados na B3.',
 'Dias de negociação', 'B3', 'https://www.b3.com.br'),

('SELIC', 'Taxa Selic',
 'Taxa básica de juros da economia brasileira, definida pelo Comitê de Política Monetária (Copom) do Banco Central. Influencia os juros de empréstimos, financiamentos e investimentos.',
 'Conforme Copom', 'Banco Central do Brasil', 'https://www.bcb.gov.br'),

('CDI', 'Taxa CDI',
 'Taxa de referência baseada nas operações de empréstimo de curtíssimo prazo entre instituições financeiras. É amplamente utilizada como referência de rentabilidade em investimentos de renda fixa.',
 'Dias úteis', 'B3', 'https://www.b3.com.br'),

('TR', 'Taxa Referencial',
 'Taxa calculada pelo Banco Central do Brasil, utilizada em determinadas operações financeiras, incluindo a remuneração da poupança e a atualização de contratos previstos em lei.',
 'Diária', 'Banco Central do Brasil', 'https://www.bcb.gov.br'),

('SALARIO', 'Salário Mínimo',
 'Menor remuneração mensal legalmente estabelecida para trabalhadores no Brasil. Seu valor é definido pelo Governo Federal e também serve como referência para diversos benefícios previdenciários e assistenciais.',
 'Conforme legislação', 'Governo Federal', 'https://www.gov.br'),

('TEMPERATURA', 'Temperatura nas Capitais Brasileiras',
 'As temperaturas das capitais brasileiras são apresentadas em graus Celsius (°C), conforme os dados disponibilizados pelo INMET. O símbolo -- indica ausência de informação para a cidade na última atualização, podendo ocorrer por indisponibilidade da estação meteorológica ou falta de dados na fonte consultada.',
 'Conforme disponibilidade', 'INMET', 'https://portal.inmet.gov.br'),

('PIB', 'Produto Interno Bruto (PIB) Brasileiro',
 'O Produto Interno Bruto (PIB) representa o valor dos bens e serviços finais produzidos no Brasil. O valor monetário é apresentado a preços correntes, em trilhões de reais, sem descontar os efeitos da inflação. A variação percentual representa o crescimento real do PIB em relação ao mesmo trimestre do ano anterior, conforme divulgado pelo IBGE. As informações são trimestrais e obtidas das tabelas 1846 (valores monetários) e 5932 (variação real) do SIDRA/IBGE.',
 'Trimestral', 'IBGE', 'https://sidra.ibge.gov.br/tabela/1846'),

('POPULACAO', 'População Brasileira — Estimativa Anual',
 'Apresenta a estimativa da população residente no Brasil, expressa em número de habitantes. O indicador é elaborado pelo IBGE e utiliza como referência o dia 1º de julho de cada ano. As estimativas populacionais são importantes para o planejamento de políticas públicas, estudos demográficos e análises socioeconômicas.',
 'Anual', 'IBGE', 'https://sidra.ibge.gov.br/tabela/6579')
ON CONFLICT (nm_indicador) DO UPDATE SET
    titulo = EXCLUDED.titulo,
    descricao = EXCLUDED.descricao,
    periodicidade = EXCLUDED.periodicidade,
    fonte = EXCLUDED.fonte,
    url_fonte = EXCLUDED.url_fonte,
    dt_atualizacao = CURRENT_TIMESTAMP;
-- ===========================================================================================================================

-- Inflação -----------------------------------------
WITH ultimos AS (
    SELECT indice, dt_referencia
    FROM tb_ipca
    WHERE status = TRUE
    ORDER BY dt_referencia DESC
    LIMIT 12)
select * from ultimos    
    
SELECT MAX(dt_referencia) AS dt_referencia,
ROUND(((EXP(SUM(LN(1 + indice / 100.0))) - 1) * 100)::numeric, 2) AS inflacao_12m
FROM ultimos
HAVING COUNT(*) = 12;

select * from tb_feriado
where uf = 'AC'

select moeda, count(*) as qtd from tb_moeda
group by moeda;

-- =================================================================
-- Feriados --------------------------------------------------------
-- =================================================================
select cd_feriado, b.cd_capital, b.cidade, a.dt_feriado, nome, tipo, b.uf, bancario, descricao, dt_atualizacao
from tb_feriado a left join tb_capital b
on a.cd_capital = b.cd_capital

select a.dt_feriado , nome, descricao
from tb_feriado a left join tb_capital b
on a.cd_capital = b.cd_capital
where a.bancario is true
order by a.dt_feriado

select * from tb_feriado
where tipo = 'NACIONAL'

select * from tb_feriado
where nome = 'Sexta-feira Santa'



-- =================================================================
-- Temperatura -----------------------------------------------------
-- =================================================================

select * from tb_capital;
select * from tb_estacao_capital;
select * from tb_temperatura;
select * from tb_feriado;

select * from tb_capital
where cd_capital = 3

select * from vw_temperatura_atual;

select * from vw_temperatura_atual
where temperatura is null;
-- 8 nulas

select * from tb_temperatura;

SELECT
    cd_capital,
    cidade,
    temperatura,
    temperatura_exibicao,
    status
FROM vw_temperatura_atual
ORDER BY cd_capital;

SELECT
    b.cd_capital,
    b.cidade,
    t.temperatura,
    t.dt_referencia,
    t.dt_atualizacao,
    t.status
FROM tb_temperatura t
JOIN tb_capital b ON b.cd_capital = t.cd_capital
ORDER BY t.dt_referencia DESC, b.cidade
LIMIT 100;


SELECT
    dt_referencia,
    COUNT(*) AS registros,
    COUNT(temperatura) AS com_temperatura,
    COUNT(*) - COUNT(temperatura) AS sem_temperatura
FROM tb_temperatura
GROUP BY dt_referencia
ORDER BY dt_referencia DESC
LIMIT 10;

select max(dt_atualizacao) from tb_temperatura



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

