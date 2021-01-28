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
  res.render('home');
});

app.get('/get_numbers/:type', (req, res) => {
  let num_array = getNumbers(req.params.type, startDate)
  num_array.then(function(results){
    res.send(results);
  });
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

async function getNumbers(type, dateWindow) {
  let db = new sqlite3.Database('/db/owasso_covid.db', sqlite3.OPEN_READONLY, (err) => {
  // let db = new sqlite3.Database('/Users/scott/Projects/personal/owasso_covid/.vscode/test/owasso_covid.db', sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      return console.error(err.message);
    }
    console.log('Connected to the owasso_covid SQlite database.');
  });

  let numbers = await queryDB(db, type, dateWindow);

  db.close((err) => {
    if (err) {
      return console.error(err.message);
    }
    console.log('Closed the database connection.');
  });

  return numbers
}

function queryDB(db, type, dateWindow) {
  return new Promise((resolve,reject) => {
    let query = `SELECT city,${type},date FROM daily_numbers WHERE date >= '${dateWindow}' ORDER BY date ASC`
    var owasso = [], collinsville = [];
    db.all(query, [], (err, rows) => {
      if (err) {
        throw err;
      }
      rows.forEach(row => {   
        if (row.city == 'OWASSO') {
          owasso.push({x: row.date, y: row[type]});
        }
        else if (row.city == 'COLLINSVILLE') {
          collinsville.push({x: row.date, y: row[type]});
        }
      });

      resolve([
        {name: 'Owasso', points: owasso},
        {name: 'Collinsville', points: collinsville}
      ]);
    });
  });
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