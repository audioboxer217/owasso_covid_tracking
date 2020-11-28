
import csv
from urllib.request import urlopen
import codecs
from datetime import datetime, timedelta
import sqlite3
import argparse

def update_db(dbFile):
  db = sqlite3.connect(dbFile)
  dbc = db.cursor()
  today = datetime.utcnow()

  print("Pulling latest CSV")
  csv_url = 'https://storage.googleapis.com/ok-covid-gcs-public-download/oklahoma_cases_city.csv'
  response = urlopen(csv_url)
  cr = list(csv.reader(codecs.iterdecode(response, 'utf-8')))

  today = datetime.strptime(cr[1][4], '%Y-%m-%d')
  # if cr[0][4] != datetime.strftime(today,'%Y-%m-%d'):
  #   today = today - timedelta(days=1)
  
  yesterday = datetime.strftime(today - timedelta(days=1),'%Y-%m-%d')
  dateWindow = datetime.strftime(today - timedelta(days=7),'%Y-%m-%d')
  prev_day = {}
  for entry in dbc.execute("SELECT city,total FROM daily_numbers WHERE date=?", (yesterday,)):
    prev_day[entry[0]] = entry[1]
    
  weekly_avg = {
    "OWASSO": [] ,
    "COLLINSVILLE": []  
  }
  for entry in dbc.execute("SELECT city,new FROM daily_numbers WHERE date >= date(?)", (dateWindow,)):
      weekly_avg[entry[0]].append(entry[1])

  for row in cr:
    if row[0] == 'OWASSO' or row[0] == 'COLLINSVILLE':
      weekly_avg[row[0]].append(int(row[1]) - prev_day[row[0]])
      city = row[0]
      total = int(row[1])
      new = int(row[1]) - prev_day[row[0]]
      average = sum(weekly_avg[row[0]]) / len(weekly_avg[row[0]])
      deaths = int(row[2])
      recovered = int(row[3])
      active = int(row[1]) - int(row[2]) - int(row[3])
      date = row[4]

      dbc.execute('SELECT EXISTS(SELECT 1 FROM daily_numbers WHERE date=? AND city=?);', (date,city))
      row_exists = dbc.fetchone()[0]
      if row_exists:
        dbc.execute('UPDATE daily_numbers SET city=:city,total=:total,new=:new,average=:average,deaths=:deaths,recovered=:recovered,active=:active,date=:date WHERE date=:date AND city=:city;', {"city": city, "total": total, "new": new,"average": average,"deaths": deaths,"recovered": recovered,"active": active,"date": date})
      else:
        dbc.execute('INSERT INTO daily_numbers ("city", "total", "new", "average", "deaths", "recovered", "active", "date") VALUES (?, ?, ?, ?, ?, ?, ?, ?);', (city,total,new,average,deaths,recovered,active,date))

  db.commit()
  dbc.close()
  print("DB Updated")

def clean_db(dbFile):
  db = sqlite3.connect(dbFile)
  dbc = db.cursor()
  dbc.execute("DELETE FROM daily_numbers WHERE date <= date('now','-30 day')")
  db.commit()
  dbc.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--dbfile", dest="sqliteFile", help="Specify a SQLite File", default="/db/owasso_covid.db")
  args = parser.parse_args()
  update_db(args.sqliteFile)
  clean_db(args.sqliteFile)