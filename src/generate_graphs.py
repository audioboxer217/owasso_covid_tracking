from update_db import update_db, clean_db
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, timezone
import time
from sklearn.linear_model import Ridge, LinearRegression
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dbfile", dest="sqliteFile", help="Specify a SQLite File", default="/db/owasso_covid.db")
parser.add_argument("--output", help="Location to store the generated graphs", default="/output")
args = parser.parse_args()

update_db(args.sqliteFile)
clean_db(args.sqliteFile)
db = sqlite3.connect(args.sqliteFile)
today = datetime.utcnow()
dbc = db.cursor()
dbc.execute('SELECT EXISTS(SELECT 1 FROM daily_numbers WHERE date=?);', (datetime.strftime(today,'%Y-%m-%d'),))
row_exists = dbc.fetchone()[0]
dbc.close()
if not row_exists:
  today = today - timedelta(days=1)
date_window = datetime.strftime(today - timedelta(days=6),'%Y-%m-%d')
dates = [ datetime.strftime(today - timedelta(days=x),'%m/%d') for x in range(7) ]
dates.reverse()

def gen_tick_arr(owasso, collinsville):
  top_num = max(owasso+collinsville)
  bottom_num = min(owasso+collinsville)
  if bottom_num > 10:
    num_size = min([len(str(top_num)),len(str(bottom_num)),len(str(top_num-bottom_num))])-1
    tick_interval = int("1" + "0" * num_size)
    top_tick = math.ceil(top_num/tick_interval)*tick_interval
    bottom_tick = math.floor(bottom_num/tick_interval)*tick_interval
    ticks = range(bottom_tick,top_tick,tick_interval)
  elif bottom_num < 1:
    ticks = np.arange(bottom_num,top_num,0.1)
  else:
    ticks = range(1,11)

  return ticks

def get_numbers(type, city):
  dbc = db.cursor()

  query = f'SELECT {type} FROM daily_numbers WHERE city = ? AND date >= ? ORDER BY date ASC'
  res_list = []
  for entry in dbc.execute(query, (city, date_window,)):
    res_list.append(entry[0])

  dbc.close()

  return res_list

def gen_line_graph_with_markers(name, owasso, collinsville):
  # multiple line plot
  plt.plot( dates, owasso, marker='o', markerfacecolor='blue', markersize=6, color='skyblue', linewidth=2, label='Owasso')
  for x, y in zip(dates, owasso):
    plt.text(x, y+0.25, str(y))
  plt.plot( dates, collinsville, marker='o', markerfacecolor='green', markersize=6, color='olive', linewidth=2, label="Collinsville")
  for x, y in zip(dates, collinsville):
    plt.text(x, y+0.25, str(y))
  plt.yticks(gen_tick_arr(owasso,collinsville))
  plt.ylabel(name)
  plt.legend()
  plt.savefig(args.output + "/" + name.lower().replace(' ','_') + ".png")
  plt.close()

def gen_line_graph(name, owasso, collinsville):
  # multiple line plot
  plt.plot( dates, owasso, marker='', color='skyblue', linewidth=2, label="Owasso")
  for x, y in zip(dates, owasso):
    if y > 1:
      plt.text(x, y+0.25, str(y))
    else:
      plt.text(x, y+0.002, str(y))
  plt.plot( dates, collinsville, marker='', color='olive', linewidth=2, label="Collinsville")
  for x, y in zip(dates, collinsville):
    if y > 1:
      plt.text(x, y+0.25, str(y))
    else:
      plt.text(x, y+0.002, str(y))
  plt.yticks(gen_tick_arr(owasso,collinsville))
  plt.ylabel(name)
  plt.legend()
  plt.savefig(args.output + "/" + name.lower().replace(' ','_') + ".png")
  plt.close()

def gen_bar_graph_with_trends(name, owassoNums, collinsvilleNums):
  # Bars
  barWidth = 0.3

  # The x position of bars
  r1 = np.arange(len(owassoNums))
  r2 = [x + barWidth for x in r1]
  
  # Create Owasso bars
  plt.bar(r1, owassoNums, width = barWidth, color = 'blue', edgecolor = 'black', capsize=7, label='Owasso')
  for i, v in enumerate(owassoNums):
    plt.text(i, v, str(round(v,1)), ha='center')
  # Create Collinsville bars
  plt.bar(r2, collinsvilleNums, width = barWidth, color = 'green', edgecolor = 'black', capsize=7, label='Collinsville')
  for i, v in enumerate(collinsvilleNums):
    plt.text(r2[i], v, str(round(v,1)), ha='center')
  
  # Trendline
  tupleArr = list(map(lambda x, y:(x,y), range(7), [1,1,1,1,1,1,1])) 
  owassoLr = Ridge()
  owassoLr.fit(tupleArr, owassoNums)
  plt.plot(tupleArr, owassoLr.coef_*tupleArr+owassoLr.intercept_, color='skyblue')
  collinsvilleLr = Ridge()
  collinsvilleLr.fit(tupleArr, collinsvilleNums)
  plt.plot(tupleArr, collinsvilleLr.coef_*tupleArr+collinsvilleLr.intercept_, color='olive')
  
  # general layout
  plt.xticks([r + barWidth for r in range(len(owassoNums))], dates)
  plt.ylabel(name)
  plt.legend()
  plt.savefig(args.output + "/" + name.lower().replace(' ','_') + ".png")
  plt.close()

def main():
  owasso_active = get_numbers('active','OWASSO')
  collinsville_active = get_numbers('active','COLLINSVILLE')
  owasso_new = get_numbers('new','OWASSO')
  collinsville_new = get_numbers('new','COLLINSVILLE')
  owasso_avg = get_numbers('average','OWASSO')
  collinsville_avg = get_numbers('average','COLLINSVILLE')
  owasso_total = get_numbers('total', 'OWASSO')
  collinsville_total = get_numbers('total','COLLINSVILLE')
  owasso_deaths = get_numbers('deaths', 'OWASSO')
  collinsville_deaths = get_numbers('deaths','COLLINSVILLE')
  owasso_fatality = [round((i / j)*100,2) for i, j in zip(owasso_deaths,owasso_total)]
  collinsville_fatality = [round((i / j)*100,2) for i, j in zip(collinsville_deaths,collinsville_total)]

  print("Generating graphs:")
  print("  - Active Cases")
  gen_line_graph_with_markers('Active Cases',owasso_active,collinsville_active)
  print("  - New Cases")
  gen_line_graph_with_markers('New Cases',owasso_new,collinsville_new)
  print("  - Avg New Cases")
  gen_bar_graph_with_trends('Avg New Cases',owasso_avg,collinsville_avg)
  print("  - Total Cases")
  gen_line_graph('Total Cases',owasso_total,collinsville_total)
  print("  - Deaths")
  gen_line_graph('Deaths',owasso_deaths,collinsville_deaths)
  print("  - Case Fatality Rate")
  gen_line_graph('Case Fatality Rate (%)',owasso_fatality,collinsville_fatality)

if __name__ == "__main__":
  main()