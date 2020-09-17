import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, timezone
import time
from sklearn.linear_model import Ridge, LinearRegression

db = sqlite3.connect('owasso_covid.db')
today = datetime.utcnow()
date_window = datetime.strftime(today - timedelta(days=7),'%Y-%m-%d')
dates = [ datetime.strftime(today - timedelta(days=x),'%m/%d/%Y') for x in range(4) ]
dates.reverse()

def get_numbers(type, city):
  dbc = db.cursor()

  query = f'SELECT {type} FROM daily_numbers WHERE city = ? AND date <= date(?) ORDER BY date ASC'
  res_list = []
  for entry in dbc.execute(query, (city, date_window,)):
    res_list.append(entry[0])

  dbc.close()

  return res_list

def gen_line_graph_with_markers(name, owasso, collinsville):
  # multiple line plot
  plt.plot( dates, owasso, marker='o', markerfacecolor='blue', markersize=6, color='skyblue', linewidth=2, label='Owasso')
  plt.plot( dates, collinsville, marker='o', markerfacecolor='green', markersize=6, color='olive', linewidth=2, label="Collinsville")
  plt.ylabel(name)
  plt.legend()
  plt.savefig(name.lower().replace(' ','_') + ".png")
  plt.close()

def gen_line_graph(name, owasso, collinsville):
  # multiple line plot
  plt.plot( dates, owasso, marker='', color='skyblue', linewidth=2, label="Owasso")
  plt.plot( dates, collinsville, marker='', color='olive', linewidth=2, label="Collinsville")
  plt.yticks(range(max(owasso+collinsville)),range(max(owasso+collinsville)))
  plt.ylabel(name)
  plt.legend()
  plt.savefig(name.lower().replace(' ','_') + ".png")
  plt.close()

def gen_bar_graph_with_trends(name, owassoNums, collinsvilleNums):
  # Bars
  barWidth = 0.3

  # The x position of bars
  r1 = np.arange(len(owassoNums))
  r2 = [x + barWidth for x in r1]
  
  # Create Owasso bars
  plt.bar(r1, owassoNums, width = barWidth, color = 'blue', edgecolor = 'black', capsize=7, label='Owasso')
  # Create Collinsville bars
  plt.bar(r2, collinsvilleNums, width = barWidth, color = 'green', edgecolor = 'black', capsize=7, label='Collinsville')
  
  # Trendline
  tupleArr = list(map(lambda x, y:(x,y), range(4), [1,1,1,1])) 
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
  plt.savefig(name.lower().replace(' ','_') + ".png")
  plt.close()

def main():
  owasso_active = get_numbers('active','OWASSO')
  collinsville_active = get_numbers('active','COLLINSVILLE')
  owasso_new = get_numbers('new','OWASSO')
  collinsville_new = get_numbers('new','COLLINSVILLE')
  owasso_avg = get_numbers('average','OWASSO')
  collinsville_avg = get_numbers('average','COLLINSVILLE')

  gen_line_graph_with_markers('Active Cases',owasso_active,collinsville_active)
  gen_line_graph('New Cases',owasso_new,collinsville_new)
  gen_bar_graph_with_trends('Avg New Cases',owasso_avg,collinsville_avg)

if __name__ == "__main__":
  main()