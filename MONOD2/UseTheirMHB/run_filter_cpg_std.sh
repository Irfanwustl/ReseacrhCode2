


std_dir=$1

dirList=($( ls ${std_dir}  ))

cpg_cutoff=$2 #2 ####################################   >=
std_cutoff=$3 #0.1 #################################    <=

filteroutdir=${std_dir}_filtered_cpg${cpg_cutoff}_std${std_cutoff}

mkdir ${filteroutdir}

echo now_filter

i=0
while (( i < ${#dirList[@]} ))
do

	#echo now_filter=========${std_dir}/${dirList[i]} 
	python3 filter_cpg_std.py ${std_dir}/${dirList[i]} ${filteroutdir} ${cpg_cutoff} ${std_cutoff}
 	(( i++ ))
done
