---
title: Selection Scan with BAYESCAN
date: December 3, 2021
---



## Table of Contents


- [1. Preparing Input File](#preparing-input-file)

- [2. Run Bayescan](#run-bayescan)

- [3. Understanding Bayescan Output](#understanding-bayescan-output)

<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>






## 1. Preparing Input File

The file conversion will be similar to how we did it for Structure using ``PGDSpider``. We need the following files:

- Population file (``ruber.pop``)

- PGDSpider template file (``vcf2bscan.spid``)

- Input VCF file (``ruber_reduced_ref.vcf``)



You can copy these files from: ``/project/inbre-train/2021_popgen_wkshp/data/Bayescan``.  Copy all files from this folder.


```bash

cd /path/to/your/gscratch/folder

cp -r /project/inbre-train/2021_popgen_wkshp/data/Bayescan .


ls -lh

-rw-rw-r-- 1 vchhatre  670 Dec  2 10:56 crovir.pop
-rw-r--r-- 1 vchhatre  336 Dec  2 10:57 vcf2bscan.sh
-rw-r--r-- 1 vchhatre 1.5K Dec  2 10:57 vcf2bscan.spid
-rw-rw-r-- 1 vchhatre 2.6M Dec  2 10:58 ruber_reduced_ref.vcf

```


<br><br>


### 1.1 Exclude Loci with More than 2 Alleles

You might recall that the VCF file contains some loci with more than 2 alleles. We need to exclude those loci from further analysis because they violate the assumptions of the method (Bayescan) we are about to use.

- First, run a check on the vcf file:


```bash
module load gcc swset perl vcftools

vcftools --vcf ruber_reduced_ref.vcf

VCFtools - 0.1.14
(C) Adam Auton and Anthony Marcketta 2009

Parameters as interpreted:
	--vcf ruber_reduced_ref.vcf

After filtering, kept 33 out of 33 Individuals
After filtering, kept 4562 out of a possible 4562 Sites
Run Time = 0.00 seconds

```


- Then check for loci that have exactly two alleles

```bash

vcftools --vcf ruber_reduced_ref.vcf --min-alleles 2 --max-alleles 2

VCFtools - 0.1.14
(C) Adam Auton and Anthony Marcketta 2009

Parameters as interpreted:
	--vcf ruber_reduced_ref.vcf
	--max-alleles 2
	--min-alleles 2

After filtering, kept 33 out of 33 Individuals
After filtering, kept 4502 out of a possible 4562 Sites
Run Time = 0.00 seconds

```

- So it appears that there are about 60 sites with more than 2 alleles. Let's exclude those.


```bash

vcftools --vcf ruber_reduced_ref.vcf --min-alleles 2 --max-alleles 2 --recode --out ruber_4502snp

VCFtools - 0.1.14
(C) Adam Auton and Anthony Marcketta 2009

Parameters as interpreted:
	--vcf ruber_reduced_ref.vcf
	--max-alleles 2
	--min-alleles 2
	--out ruber_4502snp
	--recode

After filtering, kept 33 out of 33 Individuals
Outputting VCF file...
After filtering, kept 4502 out of a possible 4562 Sites
Run Time = 0.00 seconds


```

- Check to make sure it worked:


```bash

vcftools --vcf ruber_4502snp.recode.vcf 

VCFtools - 0.1.14
(C) Adam Auton and Anthony Marcketta 2009

Parameters as interpreted:
	--vcf ruber_4502snp.recode.vcf

After filtering, kept 33 out of 33 Individuals
After filtering, kept 4502 out of a possible 4502 Sites
Run Time = 0.00 seconds


```

- Good!  Let's quickly rename this file to shorten its name:


```bash
mv ruber_4502snp.recode.vcf ruber_4502snp.vcf
```




<br><br>

### 1.2 Check Popfile


```bash
vim crovir.pop

SD_Field_0201   north
SD_Field_0255   south
SD_Field_0386   south
SD_Field_0491   south
SD_Field_0492   admixed
SD_Field_0493   south
SD_Field_0557   south
SD_Field_0598   admixed
SD_Field_0599   south
SD_Field_0642   admixed
SD_Field_0666   admixed
SD_Field_0983   north
SD_Field_1079   south
SD_Field_1205   north
SD_Field_1220   south
SD_Field_1225   south
SD_Field_1226   south
SD_Field_1381   north
SD_Field_1878   north
SD_Field_1880   north
SD_Field_1899   north
SD_Field_1961   south
SD_Field_1988   south
SD_Field_1991   south
SD_Field_2127   north
SD_Field_2287   admixed
SD_Field_2383   south
SD_Field_2427   south
SD_Field_2789   north
SD_Field_2914   south
SD_Field_2968   north
SD_Field_3027   north
SD_Field_3124   north
```

- Note that after conversion to Bayescan format, the order of individuals may change as they will be grouped by populations.


<br><br>


### 1.3 Modify the SPID File


```bash
vim vcf2bscan.spid
```


```bash
# VCF Parser questions
PARSER_FORMAT=VCF

# Only output SNPs with a phred-scaled quality of at least:
VCF_PARSER_QUAL_QUESTION=
# Select population definition file:
VCF_PARSER_POP_FILE_QUESTION=
# What is the ploidy of the data?
VCF_PARSER_PLOIDY_QUESTION=DIPLOID
# Do you want to include a file with population definitions?
VCF_PARSER_POP_QUESTION=true
# Output genotypes as missing if the phred-scale genotype quality is below:
VCF_PARSER_GTQUAL_QUESTION=
# Do you want to include non-polymorphic SNPs?
VCF_PARSER_MONOMORPHIC_QUESTION=FALSE
# Only output following individuals (ind1, ind2, ind4, ...):
VCF_PARSER_IND_QUESTION=
# Only input following regions (refSeqName:start:end, multiple regions: whitespace separated):
VCF_PARSER_REGION_QUESTION=
# Output genotypes as missing if the read depth of a position for the sample is below:
VCF_PARSER_READ_QUESTION=
# Take most likely genotype if "PL" or "GL" is given in the genotype field?
VCF_PARSER_PL_QUESTION=false
# Do you want to exclude loci with only missing data?
VCF_PARSER_EXC_MISSING_LOCI_QUESTION=true

# GESTE / BayeScan Writer questions
WRITER_FORMAT=GESTE_BAYE_SCAN

# Specify which data type should be included in the GESTE / BayeScan file  (GESTE / BayeScan can only analyze one data type per file):
GESTE_BAYE_SCAN_WRITER_DATA_TYPE_QUESTION=SNP
```

<br><br>

### 1.4 Modify the ``vcf2bscan.sh`` Script


```bash
vim vcf2bscan.sh
```


```bash
#!/bin/bash

pgdspider 	-inputfile 		\
		-inputformat VCF 	\
		-outputfile 		\
		-outputformat GESTE_BAYE_SCAN 	\
		-spid vcf2bscan.spid

```


<br>

Then run the script:


```bash
sbatch vcf2bscan.sh
```


<br><br>


### 1.5 Bayescan Input File

Let's take a look at the ``ruber.bayescan`` file


```bash
vim ruber.bayescan
```


```bash
[loci]=4502     
 
[populations]=3 
 
[pop]=1 
 1      24      2       16 8
 2      24      2       0 24
 3      24      2       23 1
 4      24      2       24 0
 5      18      2       0 18
 6      8       2       0 8 
 7      4       2       1 3 
 8      24      2       0 24
 9      24      2       24 0
 10     24      2       4 20
 11     24      2       13 11
 12     24      2       1 23
 13     2       2       0 2 
 14     22      2       0 22
 15     24      2       0 24
 16     10      2       10 0
 17     20      2       7 13
 18     22      2       19 3
```

- This is a partial view of the file. The fields are as follows:

	1. Locus number
	2. Number of genes (2x the number of diploid individuals in that population)
	3. Number of alleles found in that population at that locus
	4. Number of copies of each of the two alleles in the given population

- The number in the third column must always be 2. Our filtering of the vcf above was done precisely for this purpose. Still, you can once again verify that this number is 2 throughout:


```bash
sed -n 6,4507p ruber.bayescan | cut -f3 | sort | uniq -c

   4502  2
```

- Good! Now we can proceed with Bayescan analysis.


<br><br><br>


## 2. Run Bayescan


- Let's check the commandline parameters that Bayescan provides:


```bash
module load gcc swset bayescan

bayescan -h

 --------------------------- 
 | BayeScan 2.0 usage:     | 
 --------------------------- 
 -help        Prints this help 
 --------------------------- 
 | Input                   | 
 --------------------------- 
 alleles.txt  Name of the genotypes data input file 
 -d discarded Optional input file containing list of loci to discard
 -snp         Use SNP genotypes matrix
 --------------------------- 
 | Output                  | 
 --------------------------- 
 -od .        Output file directory, default is the same as program file
 -o alleles   Output file prefix, default is input file without the extension
 -fstat       Only estimate F-stats (no selection)
 -all_trace   Write out MCMC trace also for alpha paremeters (can be a very large file)
 --------------------------- 
 | Parameters of the chain | 
 --------------------------- 
 -threads n   Number of threads used, default is number of cpu available 
 -n 5000      Number of outputted iterations, default is 5000 
 -thin 10     Thinning interval size, default is 10 
 -nbp 20      Number of pilot runs, default is 20 
 -pilot 5000  Length of pilot runs, default is 5000 
 -burn 50000  Burn-in length, default is 50000 
 --------------------------- 
 | Parameters of the model | 
 --------------------------- 
 -pr_odds 10  Prior odds for the neutral model, default is 10 
 -lb_fis 0    Lower bound for uniform prior on Fis (dominant data), default is 0
 -hb_fis 1    Higher bound for uniform prior on Fis (dominant data), default is 1
 -beta_fis    Optional beta prior for Fis (dominant data, m_fis and sd_fis need to be set)
 -m_fis 0.05  Optional mean for beta prior on Fis (dominant data with -beta_fis)
 -sd_fis 0.01 Optional std. deviation for beta prior on Fis (dominant data with -beta_fis)
 -aflp_pc 0.1 Threshold for the recessive genotype as a fraction of maximum band intensity, default is 0.1
 --------------------------- 
 | Output files            | 
 --------------------------- 
 -out_pilot   Optional output file for pilot runs
 -out_freq    Optional output file for allele frequencies

```


- Here are the parameters we will be using:

	- ``-snp`` indicates that we are using SNP data
	- ``-od`` specifies output directory. 
	- ``-threads n`` We will use 16 threads
	- ``-n 5000`` Similar to structure MCMC. We will set this to 20000
	- ``-thin 10`` Keep this as is
	- ``-nbp 20`` Keep as is
	- ``-pilot 5000`` This is fine as well
	- ``-burn 50000`` Keep as is
	- ``-pr_odds 10`` Change this to 1000. 10 is too high a number
	- ``-out_freq`` Obtain output allele frequencies in addition to selection scan


- Let's make a script:


```bash
vim run_bayescan.sh
```


```bash

module load gcc swset bayescan/2.1


bayescan ruber.bayescan -snp \
	-od ruber_output	\
	-threads 16	\
	-n 5000	\
	-thin 10	\
	-nbp 20	\
	-pilot 5000	\
	-burn 50000	\
	-pr_odds 1000	\
	-out_freq	

```


- Make the output folder and run the script:


```bash

mkdir ruber_output

sbatch run_bayescan.sh

```




