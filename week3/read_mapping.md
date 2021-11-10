---
title: Read mapping
author: Sean Harrington & Vikram Chhatre
date: November 12, 2021
---

## Table of Contents


- [1. Orienting and finding our files](#orienting-and-finding-our-files)

- [2. Read mapping with BWA](#read-mapping-with-bwa)


<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>




## 1. Orienting and finding our files

Today, we will continue working with the data we've been working with for the past few weeks. We will start with the trimmed fastq.gz files that were output by the job array to run Trimmomatic over all of our files at the end of last last week. If you completed this, your files are likely somewhere like `/gscratch/YOUR_USERNAME/rattlesnake/finalfq/trimmed_reads`. As noted previously, we do not want to move forward with analyzing all of these files. Some are samples of other rattlesnake species, and others we showed previously to be comprised of low quality sequences.

If you have all 40 trimmed files, we'll first move the ones we are not concerned with to a new directory and ignore these for all subsequent analyses.

```
cd /LOCATION/OF_YOUR/TRIMMED_FILES
mkdir not_use_fastq
mv trimmed_MCB_284.fastq.gz trimmed_DGM_258.fastq.gz trimmed_TWR_747.fastq.gz \
	trimmed_JQR_172.fastq.gz trimmed_SD_Field_1545.fastq.gz \
	trimmed_SD_Field_0506.fastq.gz trimmed_SD_Field_1453.fastq.gz \
	not_use_fastq
```

Remember here that the `\` at the ends of these lines are escaping the end of line, so that we can have code over multiple lines for better appearance while still running it as a single line that does not contain line breaks.

If you did not complete the trimming on all samples from the end of last week, then copy over the files we have prepared:

```
cp -r /project/inbre-train/2021_popgen_wkshp/week_2_trimmed_files/trimmed_reads \
	/YOUR/DIRECTORY/TO_COPY_TO
```

This contains the fastq.gz files that we will move forward with, a subdirectory of the files that we will not move forward with, and a subdirectory containing post-trimming FastQC results on these data. If you go into the `fastqc_out` subdirectory, you can check the `multiqc_report.html` and see that trimming worked well and all samples, except for a few that we are not moving forward with, are now of high quality.

<br><br><br>

## 2. Read mapping with BWA

Now that we have demultiplexed and cleaned our data, we are reading for read mapping. Read mapping is the process of taking each read from our FASTQ files and identifying which segment of the genome they correspond to. This is done by finding the sequence of a reference genome that matches up to the read in question. This approach can be used to map reads from reduced representation library approaches like we're using here, as well as for mapping reads from whole genome sequencing runs.

When using a read mapping approach, it is key that you have a relatively closely related genome to map your reads to. If your reference genome if too diverged from your species of interest, then your reads may not map well due to accumulation of too many mutations between species, making it difficult for the read mapping program to match up the reads to the genome. As divergence between species increases, you also increase the probability of gene gains, losses, and rearrangements that further interfere with accurate mapping. If you do not have a closely related genome, de novo methods that do not rely on a reference genome will often be preferable. These include programs like iPyRAD and Stacks for RAD data, or SOAPdenovo2, ABySS, or several other alternatives for whole genomes.

Here we will use [BWA (Burrows-Wheeler Aligner)](http://bio-bwa.sourceforge.net/), one of the most common read mapping programs. We will need the reference genome in addition to our trimmed FASTQ files, let's copy that over to where we'll want to work.

```
cp /project/inbre-train/2021_popgen_wkshp/data/GCA_003400415.2_UTA_CroVir_3.0_genomic.fna .
```

Note that our file organization isn't great here, and I would not work in increasingly nested directories like we are now on my own data. This is just to try to avoid losing track of everyone's file paths. I would structure this as a single directory for the entire project, with a subdirectory inside of that for each major step. E.g., an overall `cruber` directory that contains directories like `demux`, `trim`, `mapping`, etc. Since we all have different file paths, it's trickier to keep everyone on the same page if we have to continuously point to other file paths, though.

The first step in running BWA is to index the genome. This effectively preprocesses the reference genome and makes it much faster to search, analogous to adding an index to a book. This took me > 20 minutes to run, so I've included the code to run this below (commented out), but for the sake of time, and because this is a simple command to run, we'll copy the indexed genome files that I prepared.

Commands to index:

```
# salloc --account=YOUR_ACCOUNT -t 0-0:40:00 --mem=3G --nodes=1 --ntasks-per-node=1
# module load swset gcc bwa/0.7.17 # this should look familiar by now
# bwa index -p CroVir_idx GCA_003400415.2_UTA_CroVir_3.0_genomic.fna
```

The `-p` flag gives a prefix for out indexed database.


Commands to copy over the index files to the current directory:


```
cp /project/inbre-train/2021_popgen_wkshp/data/CroVir_idx* .
```

Once we have the index files, we can go ahead and run BWA on each of our fastq files. We'll set this up as a job array, as we did for running trimmomatic on all samples.


```
#!/bin/bash

#SBATCH --job-name BWA
#SBATCH -A <YOUR_ACCOUNT>
#SBATCH -p teton
#SBATCH -t 0-0:10:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<YOUR_EMAIL>
#SBATCH -e err_BWA_%A_%a.err
#SBATCH -o std_BWA_%A_%a.out
#SBATCH --array=1-33


# load modules necessary
module load swset gcc bwa/0.7.17

# Set working directory to where the index files and trimmed_reads directory are
cd <YOUR_FILE_PATH>

# use a loop to find all the files in trimmed_reads that end
#     in fastq.gz and assign them to a bash array
for x in trimmed_reads/*fastq.gz; do   
  to_map=(${to_map[@]} "${x}")
done



## For whichever SLURM_ARRAY_TASK_ID index a job is in, get the sample 
##     name to simplify the trimmomatic call below
## here, I subtract 1 from the $SLURM_ARRAY_TASK_ID because bash indexing starts at zero
##   I think it's less confusing to subtract 1 here than to remember to do it when 
##   specifying the number of jobs for the array
sample=${to_map[($SLURM_ARRAY_TASK_ID-1)]}

# To get the output filename, we'll do a bit of extra manipulation:
# First, strip off the stuff at the beginnig we don't want
base=$(echo $sample | sed 's/trimmed_reads\/trimmed_//')
# strip off the .fastq.gz and add on a .sam as the output
outname=${base%.fastq.gz}.sam

# Run bwa on each file using the mem algorithm
bwa mem -t 6 CroVir_idx $to_map > $outname
```

This should run VERY quickly as long as we don't run into issues with job allocations. As we have noted before, the data here are fairly small, so don't necessarily expect such short run times with larger datasets, particularly as you get into whole genomes.

That will generate a lot of err and std_out files, let's clean those up a bit and  move our sam files to a new subdirectory.


```
mkdir errs_outs_bwa
mv err_BWA* std_BWA_* errs_outs_bwa

mkdir mapped_reads
mv *.sam mapped_reads
```


This will generate a SAM file for each Fastq, which contains information about where each read is mapped to, some information about how well each read mapped, and some other associated information.


We can take a quick look at one of these files using samtools.

```
cd mapped_reads
module load swset/2018.05  gcc/7.3.0 samtools/1.12
samtools view SD_Field_1220.sam | less -S
q # to quit less when you're done looking around
```
















