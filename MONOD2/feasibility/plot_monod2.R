


library(grid)
library(gridExtra)
library(ggplot2)


args <- commandArgs(TRUE)
file<-args[1] 

out_folder <- args[2]


fname<-paste(out_folder,basename(file),sep="/")
fname<-paste(fname,"pdf",sep=".")

print(fname)




df <- read.table(file,header=F,sep="\t")
head(df)

df[,1] <- as.factor(df[,1])

df <- df[which(df[,3] > 1),]

df<-df[order(-df[,2]),]

head(df)

pdf(file =fname,width = 10, height = 10)
top<-ggplot(data=df, aes(x=df[,1], y=df[,2])) +geom_bar(stat="identity",fill="darkslategray2")+theme(axis.text.x = element_text(angle=90))+  ylab("Standard Deviation")+ scale_x_discrete(limits = df[,1],labels = abbreviate)+ggtitle(basename(file))+ theme(axis.title.x=element_blank(),axis.text.x=element_blank(),axis.ticks.x=element_blank())
                                                                                                                                                                                                        
                                                                                                                                                                                                        





bottom<-ggplot(data=df,aes(x=df[,1], y=df[,3]))+geom_point(col="red")+theme(axis.text.x = element_text(angle=90))+ labs(x ="MHB") + ylab("Number of CpG")+ scale_x_discrete(limits = df[,1],labels = abbreviate)+ theme(axis.title.x=element_blank(),axis.text.x=element_blank(),axis.ticks.x=element_blank())
                                                                                                                                                                                                                                 
grid.arrange(top,bottom,bottom=textGrob("MHB"))
dev.off()

#ggplot(data=df, aes(x=df[1], y=df[2])) +geom_bar(stat="identity")



