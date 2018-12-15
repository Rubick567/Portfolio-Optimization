# Portfolio-Optimization
A Python program which will help a user select a portfolio of NASDAQstocks, by computing an efficient frontier. 

## Overview
In this project, I got some practice integrating our toolkit, using R, MySQL, Gurobi, Python, Excel, and (possibly, for prototyping) Solver. 
In stead of producing the list of stocks since I assumed investing in all the stocks in Nasdaq, I just established a general model of selecting the stocks developed a graph of maximized returns for several different levels of risk (variance) so far.

## Setup and Deliverables
The analysis is based on the file, NasdaqReturns.csv consisting of average monthly returns for many different NASDAQ stocks over several years. My deliverables includes:
* portfolio.py - Your Python program as described in the next section.
* calc_corr.R - Your R program to populate the covariance or correlation matrix. 
* nasdaq.sql - Your final database dump (export).
* writeup.Rmd - The R Notebook used to generate your write up.
* writeup.PDF - A PDF knitted from your R notebook consisting of your grap

## Solver
Before I started optimizing the real stock data in Nasdaq, I planned to create a prototype solving a simplified problem in Excel solver(This has been proven a pretty efficient and intuitive way of solving more complicated problems). I solved the simple
portfolio maximization problem of Section 8.1 (in "Practical Management Science Six Edition") using Solver. I made sure I
got the same answer both in Excel solver and in Gurobi. This model validation step is key to solving this project efficiently (it will save much troubleshooting if I run into errors later), and is even more critical when model building
in my further career.
