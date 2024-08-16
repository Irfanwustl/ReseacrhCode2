library(data.table)
options(stringsAsFactors=F)
options(scipen=100)

args <- commandArgs(trailingOnly = TRUE)
input_path <- args[1]
output_path <- args[2]

cgs <- as.data.frame(fread(paste(input_path, '/cg_2bp.bed', sep=""),header=F,sep='\t'))
colnames(cgs) <- c('chr','p1','p2','Sequence','MetDens','Label')
cov <- as.data.frame(fread(paste(input_path, '/profile_cov.bed', sep=""),header=F,sep='\t'))
edgeW <- as.data.frame(fread(paste(input_path, '/profile_edgeW.bed', sep=""),header=F,sep='\t'))
edgeC <- as.data.frame(fread(paste(input_path, '/profile_edgeC.bed', sep=""),header=F,sep='\t'))

qcW <- edgeW$V8 + edgeW$V9
qcC <- edgeC$V10 + edgeC$V11
qc <- (qcW > 1 & qcC > 1 & qcW+qcC > 10)

cgs$p1 <- cgs$p1 - 5
cgs$p2 <- cgs$p2 + 5
clvR_W <- edgeW[,4:14]
clvR_W <- format(round(clvR_W*100/cov[,4:14],9),nsmall=9)
clvR_C <- edgeC[,15:5]
clvR_C <- format(round(clvR_C*100/cov[,15:5],9),nsmall=9)
df <- cbind(cgs,clvR_W,clvR_C)
colnames(df) <- c('chr','p1','p2','Sequence','MetDens','Label',paste0('W_',1:11),paste0('C_',1:11))
df_qc <- df[qc,]

write.table(df,file=paste(output_path, '/fragma_all.txt', sep=""),sep='\t',row.names=F,quote=F)
write.table(df_qc,file=paste(output_path, '/fragma.txt', sep=""),sep='\t',row.names=F,quote=F)
