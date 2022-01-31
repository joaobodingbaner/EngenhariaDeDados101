'use strict';

const express = require('express');
const bodyParser = require('body-parser')
const Pool = require('pg').Pool

// Constants
const PORT = 8082;
const HOST = '0.0.0.0';
const pool = new Pool({
  user: 'postgres',
  host: 'db',
  database: 'postgres',
  password: 'lead',
  port: 5432,
})



// App
const app = express();
app.use(bodyParser.json());

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/listar_cripto_aportes', (req,res) => {
  pool.query('SELECT * FROM treinamento_lead.aporte', (error, result) => {
    if(error) {
      throw error
    }
    res.status(200).json(result.rows)
  })
})

app.post('/criar_aporte', (req,res) => {
  const {user_id, cripto, valor_do_aporte} = req.body;
  pool.query("INSERT INTO treinamento_lead.aporte (user_id,cripto,valor_do_aporte) VALUES($1,$2,$3)", [user_id, cripto, valor_do_aporte], (error,result) => {
    if (error) {
      throw error
    }
    res.status(201).send('aporte criado com sucesso')
  })
} )


app.listen(PORT, HOST);