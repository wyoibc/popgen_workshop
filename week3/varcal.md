---
title: Variant Calling
date: November 12, 2021
---


We now have all the information we need in order to identify genetic variants in our population sample:


- Sequence Alignment Files (``.sam``), one per study sample



## Table of Contents


- [1. Prepping SAM Files](#prepping-sam-files)

- [2. Calling SNPs](#calling-snps)



<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>









## 1. Prepping SAM Files

SAM files can get very large, hundreds of gigabytes large. It's always helpful to compress them. Furthermore, many downstream programs require that the sam files be sorted by chromosome and scaffolds/contigs and then indexed. Indexing allows for quick retrieval of alignments from the same genomic region. Finally, it would be useful to get summary alignment stats on each sample so we can find out what percentage of reads in each sample aligned with the reference genome. We will combine all these steps into a single script.


### 1.1 ``bamsortidx.sh`` Script

This script will compress, sort and index the BAM files & print alignment stats


- Navigate to the folder where you have all your mapped sam files.


```bash

cd mapped_reads

```


- Open a new file and write this script

```bash

vim bamsortidx.sh

```


```bash

#!/bin/bash
#SBATCH -t 1:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH -J bamsort
#SBATCH --mail-type=NONE
#SBATCH --account=YOUR_PROJECT


## Load base modules
module load gcc swset


## Load additional modules we need
module load samtools bamtools


## Create file path shortcuts
mapped="/path/to/your/mapped_reads_folder"

## Shortcut to a file containing all sample names
samps="$mapped/sampnames"  


## Navigate to the target directory
cd $mapped


## Begin script loop

while read samp
do
  mkdir -p $samp 
  echo "Working on $samp"
  echo "Converting ${samp}.sam to ${samp}.bam"
  samtools view -@ 16 -bS ${samp}.sam > $samp/${samp}.bam
  echo "Getting alignment stats"
  bamtools stats -in $samp/${samp}.bam > $samp/${samp}.alnStats
  echo "Sorting and indexing the bam file"
  samtools sort -@ 16 $samp/${samp}.bam -o $samp/${samp}_sorted.bam
  samtools index -@ 16 $samp/${samp}_sorted.bam
  echo "Finished processing at $(date)"
  echo "Created following files:"
  echo "$(ls -othr $samp/)"
  echo "---------------------------------------------------------"
done < $samps


```

<br>

### 1.2 Create sampnames file


```bash

ls *.sam > sampnames

vim sampnames

:%s/\.sam//g

:wq

```

Now run the script

```bash

sbatch bamsortidx.sh

```




<br>



### 1.3 Check Alignment Stats

- In the ``mapped_reads`` folder, there should be 33 sub-folders, one per sample. Each of these sub-folders should contain a file named ``SAMPLE.alnStats``. Let's look at one of them.

```bash

cat SD_Field_1880/SD_Field_1880.alnStats

```

- The most informative line in this output is the one that says: ``Mapped reads:``.  Let's get that line for each sample.


```bash

find . -name '*.alnStats' -exec cat {} \; | grep "Mapped reads:"

```

<br><br><br>


## 2. Calling SNPs

Our next step is identifying variants and recording them in variant call format. Assuming you are still in the ``mapped_reads`` folder, let's create the following script:



```bash
vim callsnp.sh
```


```bash

#!/bin/bash
#SBATCH -t 2:00:00
#SBATCH --nodes=1-1
#SBATCH --ntasks-per-node=16
#SBATCH -J SNPcall
#SBATCH --mail-type=NONE
#SBATCH --account=YOUR_PROJECT_NAME


## Load base modules
module load gcc swset


## Load additional modules we need
module load samtools bamtools bcftools


## Create file path shortcuts
mapped="/path/to/your/mapped_reads_folder"

## Create some output folders
mkdir -p $mapped/vcf $mapped/bcf


## Shortcut to a file containing all sample names
samps="$mapped/sampnames"  

## Shortcut to the reference genome
crovir="/project/inbre-train/2021_popgen_wkshp/data/refindex/CroVir.fa"


## Navigate to the target directory
cd $mapped


## Shortcut to a list of bam files. More on this soon..
bamlist="$mapped/bamlist.txt"


## Begin script

echo "Current time is: $(date)"

echo "Starting bcftools mpileup"

bcftools mpileup --threads 16 -A -a DP,AD -f $crovir --bam-list $bamlist > bcf/CroVir.bcf

echo "Calling SNPs for All samples"

bcftools call --multiallelic-caller --variants-only --threads 16 -O z bcf/CroVir.bcf -o vcf/CroVir.vcf.gz

echo "Finished calling SNPs at $(date)"


```

<br>

### 2.1 Create a List of BAM Files

Before running this script, we need to create a list of all BAM files. The list contains one BAM file per line with its complete path on the system, not just the relative path. We will use the find command again to first get partial paths.


```bash

find . -name "*_sorted.bam"

```

This should list all BAM files with their path relative to where you are on the system. Send this list to a new file.


```bash

find . -name "*_sorted.bam" > bamlist.txt

```

We still need to complete the path.  What is your current directory?

```bash
pwd

/gscratch/vchhatre/rattlesnake/mapped_reads

```

We need to prepend the pwd output in the bamlist file.  First, open the bamlist file in vim:


```bash
vim bamlist.txt
```

```bash

:%s/^./\/gscratch\/vchhatre\/rattlesnake\/mapped_reads\//g

:wq

```

That should do it. If everything looks okay, go ahead and submit your job:


```bash
sbatch callsnp.sh
```


If your script runs successfully, you should get ``CroVir.vcf.gz`` file in the ``vcf`` directory. We will briefly visit the Variant Call Format Specification in the next section.
