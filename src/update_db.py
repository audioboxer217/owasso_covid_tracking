
import csv
from urllib.request import urlopen
import codecs
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from git import Repo

csv_url = 'https://storage.googleapis.com/ok-covid-gcs-public-download/oklahoma_cases_city.csv'
sqliteFile = Path(__file__).parent / "owasso_covid.db"
db = sqlite3.connect(sqliteFile)
dbc = db.cursor()
today = datetime.utcnow()
yesterday = datetime.strftime(today - timedelta(days=1),'%m/%d/%Y')
dateWindow = datetime.strftime(today - timedelta(days=7),'%Y-%m-%d')

response = urlopen(csv_url)
cr = csv.reader(codecs.iterdecode(response, 'utf-8'))

prev_day = {}
for entry in dbc.execute("SELECT city,total FROM daily_numbers WHERE date=?", (yesterday,)):
  prev_day[entry[0]] = entry[1]
  
weekly_avg = {
  "OWASSO": [] ,
  "COLLINSVILLE": []  
}
for entry in dbc.execute("SELECT city,new FROM daily_numbers WHERE date <= date(?)", (dateWindow,)):
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
    date = datetime.strftime(datetime.strptime(row[4], '%Y-%m-%d'),'%m/%d/%Y')

    dbc.execute('SELECT EXISTS(SELECT 1 FROM daily_numbers WHERE date=? AND city=?);', (date,city))
    row_exists = dbc.fetchone()[0]
    if row_exists:
      dbc.execute('UPDATE daily_numbers SET city=:city,total=:total,new=:new,average=:average,deaths=:deaths,recovered=:recovered,active=:active,date=:date WHERE date=:date AND city=:city;', {"city": city, "total": total, "new": new,"average": average,"deaths": deaths,"recovered": recovered,"active": active,"date": date})
    else:
      dbc.execute('INSERT INTO daily_numbers ("city", "total", "new", "average", "deaths", "recovered", "active", "date") VALUES (?, ?, ?, ?, ?, ?, ?, ?);', (city,total,new,average,deaths,recovered,active,date))

db.commit()
dbc.close()

repo = Repo(Path(__file__).parent / "..")
if (repo.is_dirty):
  index = repo.index
  changedFiles = [ item.a_path for item in index.diff(None) ]
  if 'src/owasso_covid.db' in changedFiles:
    index.add('src/owasso_covid.db')
    commitMsg = "Update DB Entries - " + datetime.strftime(today,'%m/%d/%Y')
    index.commit(commitMsg)