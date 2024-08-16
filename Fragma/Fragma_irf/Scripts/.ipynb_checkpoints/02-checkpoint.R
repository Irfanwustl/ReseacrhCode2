library(data.table)
options(stringsAsFactors=F)
options(scipen=100)

args <- commandArgs(trailingOnly = TRUE)
input_path <- args[1]
output_path <- args[2]

cov <- as.data.frame(fread(paste(input_path, '/profile_cov.bed', sep=""),header=F,sep='\t'))
edgeW <- as.data.frame(fread(paste(input_path, '/profile_edgeW.bed', sep=""),header=F,sep='\t'))
edgeC <- as.data.frame(fread(paste(input_path, '/profile_edgeC.bed', sep=""),header=F,sep='\t'))

cgs <- cov[,1:3]
clvR_W <- edgeW[,4:14]
clvR_W <- format(round(clvR_W*100/cov[,4:14],9),nsmall=9)
clvR_C <- edgeC[,15:5]
clvR_C <- format(round(clvR_C*100/cov[,15:5],9),nsmall=9)

df <- cbind(cgs,clvR_W,clvR_C)
colnames(df) <- c('chr','p1','p2',paste0('W_',1:11),paste0('C_',1:11))

write.table(df,file=paste(output_path, '/fragma.txt', sep=""),sep='\t',row.names=F,quote=F)
