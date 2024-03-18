in_bam="${1}"
in_fasta="${2}"
n_motif="${3}"
threads="${4}"
out_merged="${5}"

main(){
    forward_motif \
        $in_bam \
        $threads \
        $in_fasta \
        $n_motif > $out_merged
    reverse_motif \
        $in_bam \
        $threads \
        $in_fasta \
        $n_motif >> $out_merged
}


forward_motif(){
    #
    local in_bam="${1}"
    local threads="${2}"
    local in_fasta="${3}"
    local n_motif="${4}"
    #
    # Take first read in mapped, paired, with normal FS orientation.
    # View perfect matching reads (for BWA), first in pair.
    samtools view \
             --with-header \
             --min-MQ 30 \
             --require-flags 65 \
             --threads $threads $in_bam |
        # Fetch reference
        bedtools bamtobed -i stdin |
        bedtools getfasta -bed stdin -fi $in_fasta |
        # Sed magic to extract motifs from fasta
        sed "1d; n; d" | sed -E "s/(.{$n_motif}).*/\1/"
}


reverse_motif(){
    #
    local in_bam="${1}"
    local threads="${2}"
    local in_fasta="${3}"
    local n_motif="${4}"
    #
    # Take SECOND read in mapped, paired, with normal FS orientation.
    # View perfect matching reads (for BWA).
    samtools view \
             --with-header \
             --min-MQ 30 \
             --require-flags 129 \
             --threads $threads $in_bam |
        # Fetch reference
        bedtools bamtobed -i stdin |
        bedtools getfasta -bed stdin -fi $in_fasta |
        # Sed magic to extract motifs from fasta
        sed "1d; n; d" | sed -E "s/.*(.{$n_motif})/\1/" |
        # Generate reverse compliment
        tr ACGT TGCA | rev
}

main "$@"
