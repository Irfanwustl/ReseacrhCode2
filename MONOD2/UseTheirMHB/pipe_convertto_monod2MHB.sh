bg_in=$1   #####testin real bg files' folder

outdir=${bg_in}_monod2_intersectedSortedMerged

dirList=($( ls ${bg_in}  ))

mkdir ${outdir}


i=0
while (( i < ${#dirList[@]} ))
do

	#echo now=========${bg_in}/${dirList[i]} 
	bedtools intersect -wa -wb -a ${bg_in}/${dirList[i]}  -b ../mond2_mhb_hg38_sorted_merged.bed > ${outdir}/${dirList[i]}
 	(( i++ ))
done


dirList=($( ls ${outdir}  ))

pyoutdir=${outdir}_std

mkdir ${pyoutdir}

echo now_std

i=0
while (( i < ${#dirList[@]} ))
do

	#echo now_std=========${outdir}/${dirList[i]}
	python std_cal_with_cpg_count_mean.py ${outdir}/${dirList[i]}  ${pyoutdir}
 	(( i++ ))
done



dirList=($( ls ${pyoutdir}  ))

cpg_cutoff=2 ####################################   >=
std_cutoff=0.1 #################################    <=

filteroutdir=${pyoutdir}_filtered_cpg${cpg_cutoff}_std${std_cutoff}

mkdir ${filteroutdir}

echo now_filter

i=0
while (( i < ${#dirList[@]} ))
do

	#echo now_filter=========${pyoutdir}/${dirList[i]} 
	python filter_cpg_std.py ${pyoutdir}/${dirList[i]} ${filteroutdir} ${cpg_cutoff} ${std_cutoff}
 	(( i++ ))
done








