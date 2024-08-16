#!/bin/bash

######## Data processing #################

mkdir tmp_clvR
sort -k1,1 -k2,2n $1 -o tmp_clvR/cg_2bp.bed
cat tmp_clvR/cg_2bp.bed | awk -v OFS="\t" '{print $1,$2-5,$3+5}' > tmp_clvR/cg_12bp.bed

sort -k1,1 -k2,2n $2 -o tmp_clvR/cov.bed
cat tmp_clvR/cov.bed | awk -v OFS="\t" '{print $1,$2,$2+1}' > tmp_clvR/edgeW.bed
cat tmp_clvR/cov.bed | awk -v OFS="\t" '{print $1,$3-1,$3}' > tmp_clvR/edgeC.bed
sort -k1,1 -k2,2n tmp_clvR/edgeC.bed -o tmp_clvR/edgeC.bed

bedtools coverage -a tmp_clvR/cg_12bp.bed -b tmp_clvR/cov.bed -d -sorted > tmp_clvR/profile_cov_long.bed
bedtools coverage -a tmp_clvR/cg_12bp.bed -b tmp_clvR/edgeW.bed -d -sorted > tmp_clvR/profile_edgeW_long.bed
bedtools coverage -a tmp_clvR/cg_12bp.bed -b tmp_clvR/edgeC.bed -d -sorted > tmp_clvR/profile_edgeC_long.bed

./Scripts/01.pl tmp_clvR/profile_cov_long.bed > tmp_clvR/profile_cov.bed && rm tmp_clvR/profile_cov_long.bed
./Scripts/01.pl tmp_clvR/profile_edgeW_long.bed > tmp_clvR/profile_edgeW.bed && rm tmp_clvR/profile_edgeW_long.bed
./Scripts/01.pl tmp_clvR/profile_edgeC_long.bed > tmp_clvR/profile_edgeC.bed && rm tmp_clvR/profile_edgeC_long.bed

mkdir Output

######## Cleavage profile of selected sites #################

Rscript ./Scripts/02.R tmp_clvR Output $3

######## Prepare data for CNN train and test#################

Rscript ./Scripts/03.R tmp_clvR Output

rm -r tmp_clvR
