'use strict';

// Input Vars
var cmdArgs = process.argv.slice(2);

switch (cmdArgs[0]) {
case 'debug':
  var debugSqliteFile = '/Users/scott/Projects/personal/owasso_covid/.vscode/test/owasso_covid.db';
  break;
}

// Constants
const PORT = 80;
const HOST = '0.0.0.0';
const sqlite3 = require('sqlite3');
const express = require('express');
var exphbs  = require('express-handlebars');
var sqliteFile = debugSqliteFile || '/db/owasso_covid.db';


// App
const app = express();
app.engine('handlebars', exphbs());
app.set('view engine', 'handlebars');

app.get('/', (req, res) => {  
  res.render('home');
});

app.get('/get_numbers/:type', (req, res) => {
  var entryWindow = getEntryWindow();
  entryWindow.then(function(firstEntry){
    let num_array = getNumbers(req.params.type, firstEntry)
    num_array.then(function(results){
      res.send(results);
    });
  });
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

async function getNumbers(type, firstEntry) {
  let db = new sqlite3.Database(sqliteFile, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      return console.error(err.message);
    }
  });

  let numbers = await queryDB(db, type, firstEntry);

  db.close((err) => {
    if (err) {
      return console.error(err.message);
    }
  });

  return numbers
}

function queryDB(db, type, firstEntry) {
  return new Promise((resolve,reject) => {
    let query = `SELECT city,${type},date FROM daily_numbers WHERE key >= '${firstEntry}' ORDER BY key ASC`
    var owasso = [], collinsville = [];
    db.all(query, [], (err, rows) => {
      if (err) {
        throw err;
      }
      rows.forEach(row => {   
        let dateString = row.date.replace(/^[^-]*-(.*)/g, '$1'); 
        if (row.city == 'OWASSO') {
          owasso.push({x: dateString, y: row[type]});
        }
        else if (row.city == 'COLLINSVILLE') {
          collinsville.push({x: dateString, y: row[type]});
        }
      });

      resolve([
        {name: 'Owasso', points: owasso},
        {name: 'Collinsville', points: collinsville}
      ]);
    });
  });
}

async function getEntryWindow() {
  let db = new sqlite3.Database(sqliteFile, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      return console.error(err.message);
    }
  });

  let latestEntry = await getLatestEntry(db);
  db.close((err) => {
    if (err) {
      return console.error(err.message);
    }
  });

  var entryWindow = latestEntry - 7;

  return entryWindow;
}

function getLatestEntry(db) {
  return new Promise((resolve,reject) => {
    db.get("SELECT key FROM daily_numbers ORDER BY ROWID DESC LIMIT 1", (err, row) => {
      if (err) {
        return console.error(err.message);
      }
      resolve(row.key);
    });
  });
}