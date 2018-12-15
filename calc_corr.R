rm(list = ls())
require(RMySQL)
require(reshape2)
require(matrixcalc)
require(svMisc)

#Read in Data frame
nas <- read.csv('C:/Users/kobe9/Optimization/Nas/NasdaqReturns.csv')
nas <- nas[-c(2,3)] #Remove unnecessary columns
symbols <- nas[1] #store stock symbols
years <- colnames(nas) #Store years
tnas <- data.frame(t(nas[-1]))

colnames(tnas) <- symbols$StockSymbol
tnas[1:5,1:5]
smcov <- cov(tnas)
smcov <- upper.triangle(smcov)
smcov[1:5,1:5]

covmelt <- melt(smcov)
covmelt <- covmelt[covmelt$value != 0,]

means <- rep(0, ncol(tnas))
sds <- rep(0,ncol(tnas))
stock_data <- data.frame(symbols$StockSymbol,means,sds)

for (stock in 1:ncol(tnas)){
  stock_data[stock,2] <- mean(tnas[,stock])
  stock_data[stock,3] <- sd(tnas[,stock])
}
  
#Recreate Stock Indices

## Temporary Subset
#covmelt <- covmelt[1:15,1:3]

covmelt$Stock1 <- as.numeric(covmelt$Var1)
covmelt$Stock2 <- as.numeric(covmelt$Var2)
  
#Rearrange Columns
covmelt <- covmelt[-c(1,2)]
covmelt <- covmelt[c(2,3,1)]
head(covmelt)
covmelt

con <- dbConnect(MySQL(), dbname = "nasdaq", username = "root", password = "1234")



base_query <- "insert into cov (stock1, stock2, covariance) values"
values_string <- "(%s,%s,%s)"
#for (row in 1:nrow(covmelt)) {
#  dbSendQuery(con, sprintf(query, covmelt[row,1],covmelt[row,2],covmelt[row,3]))
#  dbCommit(con)
#}

for (t in seq(1, nrow(covmelt)-5, by = 5)){
  progress(t,max.value = nrow(covmelt), console = T)
  new_query <-  paste(base_query, sprintf(values_string, covmelt[t,1], covmelt[t,2], covmelt[t,3]))
  for (i in 1:4){
    new_query <- paste(new_query,", ", sprintf(values_string, covmelt[t+i,1], covmelt[t+i,2], covmelt[t+i,3]), sep = "")
  }
  if (t + 10 >= nrow(covmelt)) {
    for (j in (t+5):nrow(covmelt)){
      new_query <- paste(new_query,", ", sprintf(values_string, covmelt[j,1], covmelt[j,2], covmelt[j,3]), sep = "")
    }
  }
  dbSendQuery(con, new_query)

}


query <- "insert into stocks (symbol, mean, stdev) values ('%s', %s, %s)"
for (mean in 1:nrow(stock_data)) {
  progress(mean, max.value = nrow(stock_data), console = T)
  dbSendQuery(con, sprintf(query, stock_data[mean,1], stock_data[mean, 2], stock_data[mean,3]))
  dbCommit(con)
}
print("AMEN, ALLELUIA")
dbDisconnect(con)

