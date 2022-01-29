CREATE DATABASE metabase;
CREATE SCHEMA treinamento_lead;

CREATE TABLE IF NOT EXISTS treinamento_lead.users(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(10),
    sobrenome VARCHAR(25)
);

CREATE TABLE IF NOT EXISTS treinamento_lead.aporte(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    cripto VARCHAR(25),
    valor_do_aporte NUMERIC 
);

INSERT INTO treinamento_lead.users("nome", "sobrenome") VALUES ('Thiago','Beppe');
INSERT INTO treinamento_lead.users("nome", "sobrenome") VALUES ('Lucas','Silva');
INSERT INTO treinamento_lead.users("nome", "sobrenome") VALUES ('Priscila','Alcantara');
INSERT INTO treinamento_lead.users("nome", "sobrenome") VALUES ('Whinderson','Nunes');
INSERT INTO treinamento_lead.users("nome", "sobrenome") VALUES ('Arselino','Freitas');

INSERT INTO treinamento_lead.aport("user_id","cripto","valor_do_aporte") VALUES ('1','Solana',100)
INSERT INTO treinamento_lead.aport("user_id","cripto","valor_do_aporte") VALUES ('1','Bitcoin',500)
INSERT INTO treinamento_lead.aport("user_id","cripto","valor_do_aporte") VALUES ('1','Bitcoin',0.10)
INSERT INTO treinamento_lead.aport("user_id","cripto","valor_do_aporte") VALUES ('1','Solana',50)
