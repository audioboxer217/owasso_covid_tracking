'use strict';

// Constants
const PORT = 80;
const HOST = '0.0.0.0';
const sqlite3 = require('sqlite3');
const express = require('express');
var exphbs  = require('express-handlebars');
const sqliteFile = '/db/owasso_covid.db';
// const sqliteFile = '/Users/scott/Projects/personal/owasso_covid/.vscode/test/owasso_covid.db';
const dateWindow = getDateWindow();

// App
const app = express();
app.engine('handlebars', exphbs());
app.set('view engine', 'handlebars');

app.get('/', (req, res) => {  
  res.render('home');
});

app.get('/get_numbers/:type', (req, res) => {
  dateWindow.then(function(startDate){
    let num_array = getNumbers(req.params.type, startDate)
    num_array.then(function(results){
      res.send(results);
    });
  });
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

async function getNumbers(type, dateWindow) {
  let db = new sqlite3.Database(sqliteFile, sqlite3.OPEN_READONLY, (err) => {
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

async function getDateWindow() {
  let db = new sqlite3.Database(sqliteFile, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      return console.error(err.message);
    }
    console.log('Connected to the owasso_covid SQlite database.');
  });

  let latestDate = await getLatestDate(db);

  db.close((err) => {
    if (err) {
      return console.error(err.message);
    }
    console.log('Closed the database connection.');
  });

  var d = new Date(latestDate + 'T00:00:00.000-06:00');
  d.setDate(d.getDate() - 6);
  d.toLocaleString('en-US', { timeZone: 'America/Chicago' })
  var dateWindow = formatDate(d);

  return dateWindow;
}

function getLatestDate(db) {
  return new Promise((resolve,reject) => {
    db.get("SELECT date FROM daily_numbers ORDER BY ROWID DESC LIMIT 1", (err, row) => {
      if (err) {
        return console.error(err.message);
      }
      resolve(row.date);
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