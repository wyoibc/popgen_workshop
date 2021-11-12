---
title: VCF Specification
date: November 12, 2021
---

The current version of VCF is 4.3. However, your files are likely formatted to version 4.1 because that's the version available on Teton. The VCF format specification has an extensive manual [available here](https://samtools.github.io/hts-specs/VCFv4.3.pdf).


## 1. VCF Header

The header is usually quite large and contains definitions of each field. The most important header line is the one that starts with ``#CHROM``. Let's look at it.

```bash

zgrep "#CHROM" vcf/CroVir.vcf.gz > vcf.header

vim vcf.header

:%s/\t//g

```

We first sent the header to a text file and then replaced all tabs with line breaks so the file is easier to read.


<br><br>

## 2. The FORMAT Field

This is one of the most important fields in the VCF file. It consists of one or more of the following:

- ``DP``: Total depth. Number of sequence reads that confirm a given variant in an individual. 

- ``AD``: Allelic Depth. Number of sequence reads that confirm a given allele. Two values provided, one per allele

- ``GT``: This is the called genotype based on allelic depth, quality scores and error rate

- ``GQ``: Genotype Quality - based on PHRED scaled quality scores



<br><br>

## 3. Using VCFTools

VCFTools is a very fast and wonderful program to parse and filter VCF files. Let's run a few examples of what this program can do:


### 3.1 Summarize VCF Files


```bash

vcftools --gzvcf CroVir.vcf.gz

```

### 3.2 Filter Loci

- Keep only biallelic sites

```bash

vcftools --gzvcf CroVir.vcf.gz --min-alleles 2 --max-alleles 2

```

- Get allele frequency table


```bash
vcftools --gzvcf CroVir.vcf.gz --freq

```

- Keep sites for only Chromosome #2

```bash
vcftools --gzvcf CroVir.vcf.gz --chr 2
```

- Thin your dataset to reduce linkage disequilibrium (20Kbp)

```bash
vcftools --gzvcf CroVir.vcf.gz --thin 20000
```























