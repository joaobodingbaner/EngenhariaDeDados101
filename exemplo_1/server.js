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



app.listen(PORT, HOST);