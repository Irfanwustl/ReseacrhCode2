outdir=$1

mkdir ${outdir}

dirList=("Bronchus and lung")

parallel -j 8 python3 illumina_retrieve_all_download.py ::: "${dirList[@]}" ::: ${outdir}
