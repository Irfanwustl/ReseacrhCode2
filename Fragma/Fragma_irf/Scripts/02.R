library(data.table)
options(stringsAsFactors=F)
options(scipen=100)

args <- commandArgs(trailingOnly = TRUE)
input_path <- args[1]
output_path <- args[2]
interest <- args[3]

cgs <- as.data.frame(fread(paste(input_path, '/cg_2bp.bed', sep=""),header=F,sep='\t'))
colnames(cgs) <- c('chr','p1','p2','Sequence','MetDens','Label')
cov <- as.data.frame(fread(paste(input_path, '/profile_cov.bed', sep=""),header=F,sep='\t'))
edgeW <- as.data.frame(fread(paste(input_path, '/profile_edgeW.bed', sep=""),header=F,sep='\t'))
edgeC <- as.data.frame(fread(paste(input_path, '/profile_edgeC.bed', sep=""),header=F,sep='\t'))

cgs$p1 <- cgs$p1 - 5
cgs$p2 <- cgs$p2 + 5
clvR_W <- edgeW[,4:14]
clvR_C <- edgeC[,15:5]

df <- cbind(cgs,clvR_W+clvR_C, cov[,15:5]+cov[,4:14])
colnames(df) <- c('chr','p1','p2','Sequence','MetDens','Label',paste0('end_',1:11),paste0('cov_',1:11))

df_interest <- matrix(0, nrow = 1, ncol = 22)
df_interest[1,] <- apply(subset(df, df$Label == interest)[,-(1:6)], 2, sum)
df_interest <- as.data.frame(df_interest)
df_interest[1,1:11] <- df_interest[1,1:11]*100/df_interest[1,12:22]
df_interest <- df_interest[,1:11]
colnames(df_interest) <- paste0('Cleavage_proportion_',1:11)
df_interest$Label <- interest

write.table(df_interest[,c(12, 1:11)],file=paste(output_path, '/fragma_interest.txt', sep=""),sep='\t',row.names=F,quote=F)
