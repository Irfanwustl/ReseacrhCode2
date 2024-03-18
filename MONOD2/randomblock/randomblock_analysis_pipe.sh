####### param ####

bg_in=$1 #all_bg_rooled


mhbstdfolder=$2  #all_bg_rooled_intersected_std


maxtryforablock=10  #how many try should we try for generating a corresponding random block


maximumblocklength=1479  # what shoulb the maximum length of a random block

##### param ###



randblockfolder=${bg_in}_corresRandBlock
mkdir ${randblockfolder}



outdir=${bg_in}_randblock_intersected

dirList=($( ls ${bg_in}  ))

mkdir ${outdir}


i=0
while (( i < ${#dirList[@]} ))
do

	

	corresmhbstdfile=${dirList[i]}_with_monod2_std


	echo nowbg=========${dirList[i]} 

	echo corres=========${corresmhbstdfile}

	python3 randomperfileMHB.py ${bg_in}/${dirList[i]} ${mhbstdfolder}/${corresmhbstdfile} ${randblockfolder}/${dirList[i]}_randblock ${maxtryforablock} ${maximumblocklength}

	sort -k 1,1 -k2,2n ${randblockfolder}/${dirList[i]}_randblock > ${randblockfolder}/${dirList[i]}_randblock_sorted

	bedtools intersect -wa -wb -a ${bg_in}/${dirList[i]}  -b ${randblockfolder}/${dirList[i]}_randblock_sorted > ${outdir}/${dirList[i]}_with_monod2
 	(( i++ ))
done







#########################intack######

dirList=($( ls ${outdir}  ))

pyoutdir=${outdir}_std

mkdir ${pyoutdir}

i=0
while (( i < ${#dirList[@]} ))
do

	echo now_std=========${dirList[i]} 
	python std_cal_with_cpg_count.py ${outdir}/${dirList[i]}  ${pyoutdir}
 	(( i++ ))
done



dirList=($( ls ${pyoutdir}  ))

routdir=${pyoutdir}_fig

mkdir ${routdir}

i=0
while (( i < ${#dirList[@]} ))
do

	echo now_fig=========${dirList[i]} 
	Rscript plot_monod2.R ${pyoutdir}/${dirList[i]}  ${routdir}
 	(( i++ ))
done