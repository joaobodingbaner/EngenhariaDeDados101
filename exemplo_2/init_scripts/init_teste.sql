CREATE SCHEMA treinamento_lead;

CREATE TABLE IF NOT EXISTS treinamento_lead.data_engs(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(10),
    sobrenome VARCHAR(25)
);

INSERT INTO treinamento_lead.data_engs("nome", "sobrenome") VALUES ('thiago','beppe');