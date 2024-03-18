

# ~cmiller/usr/bin/isub -i mgibio/biscuit

#bsub -M 48000000 -R 'select[mem>48000] span[hosts=1] rusage[mem=48000]' -oo bam.err -q research-hpc -a "docker(mgibio/biscuit)" -J irftest1389 "bash bam_sort_flexi_job.sh"
start=$SECONDS

file_directory=$1  #"test_bam"  #"medgenome_bam_pp"


coretouse=$2

outdir="${file_directory}_sorted"

mkdir  ${outdir}


fList=($( ls ${file_directory} ))



i=0
while (( i < ${#fList[@]} ))
#while (( i < 1 ))
do
	infile=${fList[i]} 
	outfile="$(echo ${infile%%.*})_sorted"
	echo "${infile} sorting....."
	samtools sort -@ ${coretouse} -o  ${outdir}/${outfile}  -O bam  ${file_directory}/${infile}
	echo "${outfile} indexing....."
	samtools index  -@ ${coretouse}  -b ${outdir}/${outfile}
	echo "done..........."
	(( i++ ))
done


end=$SECONDS
duration=$(( end - start ))
echo "stuff took $duration seconds to complete"

