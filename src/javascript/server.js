'use strict';

// Constants
const PORT = 80;
const HOST = '0.0.0.0';
const sqlite3 = require('sqlite3');
const express = require('express');
var exphbs  = require('express-handlebars');
var d = new Date();
d.setDate(d.getDate() - 6);
const dateWindow = formatDate(d);

// DB
const db = new sqlite3.Database('/db/owasso_covid.db', sqlite3.OPEN_READONLY, (err) => {
// const db = new sqlite3.Database('.vscode/test/owasso_covid.db', sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    return console.error(err.message);
  }
  console.log('Connected to the owasso_covid SQlite database.');
});

// App
const app = express();
app.engine('handlebars', exphbs());
app.set('view engine', 'handlebars');

const active_cases = getNumbers('active')
const new_cases = getNumbers('new')
const avg_new = getNumbers('average')
const total_cases = getNumbers('total')
const total_deaths = getNumbers('deaths')
// const owasso_fatality = [round((i / j)*100,2) for i, j in zip(owasso_deaths,owasso_total)]
// const collinsville_fatality = [round((i / j)*100,2) for i, j in zip(collinsville_deaths,collinsville_total)]

app.get('/', (req, res) => {  
  // res.send(active_cases)
  res.render('home');
});

app.get('/get_numbers/:type', (req, res) => {
  res.send(eval(req.params.type));
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

db.close((err) => {
  if (err) {
    return console.error(err.message);
  }
  console.log('Closed the database connection.');
});

function getNumbers(type) {
  let query = `SELECT city,${type},date FROM daily_numbers WHERE date >= ? ORDER BY date ASC`
  var owasso = [], collinsville = [];
  db.each(query, [dateWindow], (err, row) => {
    if (err) {
      throw err;
    }
    if (row.city == 'OWASSO') {
      owasso.push({x: row.date, y: row[type]});
    }
    else if (row.city == 'COLLINSVILLE') {
      collinsville.push({x: row.date, y: row[type]});
    }
  });
  
  return [
    {name: 'Owasso', points: owasso},
    {name: 'Collinsville', points: collinsville}
  ];
}

function formatDate(date) {
  var d = new Date(date),
      month = '' + (d.getMonth() + 1),
      day = '' + d.getDate(),
      year = d.getFullYear();

  if (month.length < 2) 
      month = '0' + month;
  if (day.length < 2) 
      day = '0' + day;

  return [year, month, day].join('-');
}