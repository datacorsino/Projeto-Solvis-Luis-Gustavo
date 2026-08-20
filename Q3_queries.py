"""
Consultas SQL via DuckDB - Q3
Views sobre parquet simulam tabelas PostgreSQL.
"""

import duckdb
import urllib.request
from pathlib import Path

# --- usuário: define a pasta de saída na Área de Trabalho ---
USUARIO  = 'Luis Gustavo'
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR  = Path.home() / 'Desktop' / f'Teste Técnico - {USUARIO}'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- download automático dos parquets se ainda não existirem ---
_REPO = 'https://raw.githubusercontent.com/solvis-engineering/analytics_teste_analista_dados/main/nivel_pleno'
_ARQUIVOS = ['answers.parquet', 'evaluations.parquet', 'stores.parquet', 'questions.parquet', 'choices.parquet']

def _baixar_dados():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pendentes = [f for f in _ARQUIVOS if not (DATA_DIR / f).exists()]
    if not pendentes:
        return
    print(f'Baixando {len(pendentes)} arquivo(s) do repositório...')
    for nome in pendentes:
        print(f'  {nome}...', end=' ', flush=True)
        urllib.request.urlretrieve(f'{_REPO}/{nome}', DATA_DIR / nome)
        print(f'{(DATA_DIR / nome).stat().st_size / 1024 / 1024:.1f} MB')
    print('Download concluído.\n')

_baixar_dados()

con = duckdb.connect()

con.execute(f"CREATE OR REPLACE VIEW raw_evaluations AS SELECT * FROM read_parquet('{DATA_DIR}/evaluations.parquet')")
con.execute(f"CREATE OR REPLACE VIEW answers   AS SELECT * FROM read_parquet('{DATA_DIR}/answers.parquet')")
con.execute(f"CREATE OR REPLACE VIEW stores    AS SELECT * FROM read_parquet('{DATA_DIR}/stores.parquet')")
con.execute(f"CREATE OR REPLACE VIEW choices   AS SELECT * FROM read_parquet('{DATA_DIR}/choices.parquet')")
con.execute(f"CREATE OR REPLACE VIEW questions AS SELECT * FROM read_parquet('{DATA_DIR}/questions.parquet')")

# evaluations tem 24.316 linhas duplicadas por id; manter apenas a primeira ocorrencia
con.execute("""
CREATE OR REPLACE VIEW evaluations AS
SELECT DISTINCT ON (id) id, date_time, store_id
FROM raw_evaluations
ORDER BY id, date_time
""")

print("Q3a - loja mais satisfeita por regiao e atributo")

Q3A = """
WITH base AS (
    SELECT
        s.region,
        s.name AS store_name,
        q.name AS question_name,
        AVG(c.value) AS avg_satisfaction
    FROM answers a
    JOIN evaluations e ON a.id = e.id
    JOIN stores s ON e.store_id = s.id
    JOIN choices c ON a.choice_id = c.id
    JOIN questions q ON a.question_id = q.id
    GROUP BY s.region, s.name, q.name
),
ranked AS (
    SELECT *,
        RANK() OVER (
            PARTITION BY region, question_name
            ORDER BY avg_satisfaction DESC
        ) AS rk
    FROM base
)
SELECT
    region,
    question_name,
    store_name,
    ROUND(avg_satisfaction, 1) AS satisfacao_pct
FROM ranked
WHERE rk = 1
ORDER BY region, question_name;
"""

result_3a = con.execute(Q3A).df()
print(result_3a.to_string(index=False))

print("\nQ3b - materialized view de satisfacao por loja e atributo")

Q3B_CREATE = """
CREATE OR REPLACE TABLE mv_store_satisfaction AS
SELECT
    s.region,
    s.id AS store_id,
    s.name AS store_name,
    q.name AS question_name,
    COUNT(*) AS total_responses,
    ROUND(AVG(c.value), 1) AS satisfacao_pct
FROM answers a
JOIN evaluations e ON a.id = e.id
JOIN stores s ON e.store_id = s.id
JOIN choices c ON a.choice_id = c.id
JOIN questions q ON a.question_id = q.id
GROUP BY s.region, s.id, s.name, q.name;
"""
con.execute(Q3B_CREATE)
print("mv_store_satisfaction criada.\n")

Q3B_USE = """
SELECT
    region,
    question_name,
    SUM(total_responses) AS total_respostas,
    ROUND(AVG(satisfacao_pct), 1) AS satisfacao_media_pct
FROM mv_store_satisfaction
GROUP BY region, question_name
ORDER BY region, satisfacao_media_pct DESC;
"""
result_3b = con.execute(Q3B_USE).df()
print(result_3b.to_string(index=False))

print("\nQ3c - convencao de particao mensal e query dinamica")

# Nomenclatura recomendada: <tabela>_YYYYMM (ex: evaluations_202601)
# Ordenavel lexicograficamente, compativel com partition pruning e legivel.

Q3C_POSTGRES = """\
-- PostgreSQL: gera e executa query sobre os ultimos 6 meses particionados
-- Particoes nomeadas como evaluations_YYYYMM

DO $$
DECLARE
    v_suffix TEXT;
    v_sql    TEXT := '';
    i        INT;
BEGIN
    FOR i IN 1..6 LOOP
        v_suffix := TO_CHAR(
            DATE_TRUNC('month', CURRENT_DATE) - (i || ' months')::INTERVAL,
            'YYYYMM'
        );
        IF i > 1 THEN v_sql := v_sql || ' UNION ALL '; END IF;
        v_sql := v_sql || 'SELECT * FROM evaluations_' || v_suffix;
    END LOOP;
    RAISE NOTICE 'Query gerada: %', v_sql;
    EXECUTE v_sql;
END $$;
"""
print(Q3C_POSTGRES)

# equivalente executavel em DuckDB
Q3C_DUCKDB = """
SELECT
    STRFTIME(DATE_TRUNC('month', date_time), '%Y%m') AS particao_YYYYMM,
    COUNT(*) AS total_avaliacoes
FROM evaluations
WHERE date_time >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '6 months'
  AND date_time <  DATE_TRUNC('month', CURRENT_DATE)
GROUP BY particao_YYYYMM
ORDER BY particao_YYYYMM;
"""
result_3c = con.execute(Q3C_DUCKDB).df()
print(result_3c.to_string(index=False))

con.close()
