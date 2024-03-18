infolder=$1
outdir=${infolder}_head

dirList=($( ls ${infolder}  ))



mkdir ${outdir}


i=0
while (( i < ${#dirList[@]} ))
do

	echo now=========${dirList[i]} 
	head ${infolder}/${dirList[i]}  > ${outdir}/${dirList[i]}
 	(( i++ ))
done