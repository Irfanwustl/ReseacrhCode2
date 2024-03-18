outdir=$1

mkdir ${outdir}

dirList=("Adrenal gland" "Base of tongue" "Bladder" "Brain" "Breast" "Bronchus and lung" "Colon" "Corpus uteri" "Esophagus" "Floor of mouth" "Kidney" "Larynx" "Liver and intrahepatic bile ducts" "Pancreas" "Prostate gland" "Rectum" "Skin" "Stomach" "Thymus" "Thyroid gland" "Uterus, NOS")

parallel -j 8 python3 illumina_retrieve_all_download.py ::: "${dirList[@]}" ::: ${outdir}
