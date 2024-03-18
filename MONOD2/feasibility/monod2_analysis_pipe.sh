bg_in=$1

outdir=${bg_in}_monod2_intersected

dirList=($( ls ${bg_in}  ))

mkdir ${outdir}


i=0
while (( i < ${#dirList[@]} ))
do

	#echo now=========${dirList[i]} 
	bedtools intersect -wa -wb -a ${bg_in}/${dirList[i]}  -b ../mond2_mhb_hg38_sorted_merged.bed > ${outdir}/${dirList[i]}_with_monod2
 	(( i++ ))
done


dirList=($( ls ${outdir}  ))

pyoutdir=${outdir}_std

mkdir ${pyoutdir}

echo now_std

i=0
while (( i < ${#dirList[@]} ))
do

	#echo now_std=========${dirList[i]} 
	python std_cal_with_cpg_count.py ${outdir}/${dirList[i]}  ${pyoutdir}
 	(( i++ ))
done



dirList=($( ls ${pyoutdir}  ))

routdir=${pyoutdir}_fig

mkdir ${routdir}

echo now_fig

i=0
while (( i < ${#dirList[@]} ))
do

	#echo now_fig=========${dirList[i]} 
	Rscript plot_monod2.R ${pyoutdir}/${dirList[i]}  ${routdir}
 	(( i++ ))
done
