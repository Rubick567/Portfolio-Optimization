# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 13:13:36 2018

@author: poeha
"""

import mysql.connector as sql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
from gurobipy import *

"""
Import Data from 'Nasdaq' database in Mysql; Including the names, indices, 
means of return, covariances,and standard deviations of 1158 
stocks in Nasdaq StockIndex from 2000.02 to 2009.12.
"""
db = sql.connect(user = 'root',
                 password = '1234',
                 host = 'localhost',
                 database = 'nasdaq')
cur1 = db.cursor()
m = list()
s = list()
symbols = list()
cur1.execute('SELECT * FROM stocks')
for row in cur1:
    m.append(row[1])
    s.append(row[2])
    symbols.append(row[0])
#Get the list of means & standard deviations
	
Q = {}
cur1.execute('SELECT * FROM cov')
for row in cur1:
    Q[(row[0],row[1])] = row[2]
#Get the matrix of covariances and 
#reform them into a dictionary
db.commit()
cur1.close()

db.close()

"""
Apply an Optimization Model through Gurobi Package into the construction 
of optimal portfolios of stocks which will achieve the lowest Risks within 
the constraints of certain target Return Rates of the portfolio.
"""

p = Model("Portfolio")
p.ModelSense = GRB.MAXIMIZE

means = m
sds = s
covars = Q
objlist = list()

#Decision Variables
a = list()

#A list for decision variables(fractions of investment into each stocks)
for i in range(0, len(m)):
   perc = p.addVar(vtype = GRB.SEMICONT, name = 'stock' + str(i+1), lb = 0, ub = 1)   
   a.append(perc)
#print(a)
    
p.update()

#Constraints
p.addConstr(sum(a) == 1, 'Ratios add to 1')

# Run the model to get the minimized return as the lower bound for our return range:
risk = 2*quicksum(a[i]*covars[(i+1,j+1)]*a[j] for i in range(0,len(a)) for j in range(i,len(a))) - quicksum(a[i]*covars[(i+1,i+1)]*a[i] for i in range(0,len(a)))
p.setObjective(risk, GRB.MINIMIZE)     
p.update()
p.optimize()
obj = p.getObjective()
min_risk = obj.getValue()
varlist = list()
for var in p.getVars():
    varlist.append(var.x)
minrisk_return = quicksum(varlist[i]*means[i] for i in range(0,len(a))) 

#Constraints
target = p.addConstr(quicksum(a[i]*means[i] for i in range(0,len(a))) == minrisk_return, 'Return')

'''
# Make the max return among the origin dataset the upper bound of the expected returns
# and minrisk return 0.0036 be the lower bound of the expected returns
# Run the loop and store the max_risks & max_returns
'''

max_risk = list()
max_return = list()
frontier = pd.Series()
for r in np.linspace(0.0036, max(means), 100):
    target.rhs = r
    p.update()
    p.optimize()
    varlist = list()
    obj = p.getObjective()
    for var in p.getVars():
        varlist.append(var.x)
    max_risk.append(obj.getValue())
    max_return.append(sum(varlist[i]*means[i] for i in range(0,len(a))))
    frontier.loc[sqrt(obj.getValue())] = r
#print(max_risk)
#print(max_return)

#for var in p.getVars():
#    print("Variable Name = {}, Optimal Value = ${}, Lower Bond = ${}, Upper Bond = {}".format(var.varName, var.x, var.lb, var.ub))
'''
# Plot the Markowitz Frontier with the portfolio's optimal combinations of risks and returns
'''

ax = plt.gca()
frontier.plot(color='Green', label='Efficient Frontier', ax=ax)
ax.axis([0.01, 0.07, 0, 0.06])
ax.set_xlabel('Volatility (standard deviation)')
ax.set_ylabel('Expected Return')
ax.legend()
ax.grid()
plt.show()

"""
Now, once we've got the objective values of RISK in certain RETURN constraints, 
we need to connect our program to mysql again and store the expRETURN and expRISK
into the 'portfolio' table in 'nasdaq' database.
"""

db = sql.connect(user = 'root',
                 password = '1234',
                 host = 'localhost',
                 database = 'nasdaq')
cur2 = db.cursor()
add_items = "INSERT INTO portfolio (expReturn, expRisk) VALUES (%s, %s)"
for i in range(0, len(max_return)):
    cur2.execute(add_items % (max_return[i], max_risk[i]))
db.commit()

cur2.close()
db.close()