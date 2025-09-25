# ΔFCS sequencing analysis

SARS-CoV-2 ΔFCS sequencing analysis for "SARS-CoV-2-related bat viruses evade human intrinsic immunity but lack efficient transmission capacity" by Peña-Hernández et al. (2024)

## Index amplicon sequencing using Bowtie2 (v2.5.1, GCC-12.2.0)
```
bowtie2-build amplicon.fna amplicon_index
```
amplicon.fna contains the nucleotide sequence of the amplicon spanning the FCS (corresponding to ARTIC primers SARS-CoV-2_400_77_RIGHT_0 and SARS-CoV-2_400_77_LEFT_0)

## Align reads to amplicon using Bowtie2 (v2.5.1, GCC-12.2.0)
```
bowtie2 -q --local -t --very-sensitive-local --no-mixed --no-discordant -x amplicon_index \
        -1 /path/to/sample_R1.fastq.gz \
        -2 /path/to/sample_R2.fastq.gz \
	-S /path/to/sample_align.sam
```

## Convert alignments from SAM to BAM format using Samtools (v1.18, GCC-12.2.0)
```
samtools view -bS /path/to/sample_align.sam > /path/to/sample_align.bam
```

## Filter out non-mapping reads using Samtools (v1.18, GCC-12.2.0)
```
samtools view -b -F 4 /path/to/sample_align.bam > /path/to/sample_mapped.bam
```

## Extract nucleotide sequences from mapping reads BAM file using Samtools (v1.18, GCC-12.2.0)
```
samtools view /path/to/sample_mapped.bam | cut -f 10 > /path/to/sample_mapped_extracted.txt
```
each line in sample_mapped_extracted.txt corresponds to a single read

## Filter out mapping reads lacking conserved FCS flanking sites
```
grep 'GACTCA' /path/to/sample_mapped_extracted.txt | grep 'CAATCC' /path/to/sample_mapped_extracted.txt > /path/to/sample_mapped_extracted_flank.txt
```
both sites must be present for reads to pass this filter step

## Count number of remaining reads containing FCS sequence  
```
grep -c "TCTCCTCGGCGGGCACGT" /path/to/sample_mapped_extracted_flank.txt
wc -l /path/to/sample_mapped_extracted_flank.txt
```