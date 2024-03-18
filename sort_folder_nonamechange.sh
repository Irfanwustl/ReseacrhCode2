infolder=$1
outdir=${infolder}_sorted

dirList=($( ls ${infolder}  ))



mkdir ${outdir}


i=0
while (( i < ${#dirList[@]} ))
do

	#echo now=========${dirList[i]} 
	sort -k 1,1 -k2,2n ${infolder}/${dirList[i]}  > ${outdir}/${dirList[i]}
 	(( i++ ))
done