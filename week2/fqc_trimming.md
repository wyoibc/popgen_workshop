---
title: Quality assessment and trimming
author: Sean Harrington & Vikram Chhatre
date: November 5, 2021
---

## Table of Contents


- [1. Examining read quality](#examining-read-quality)

- [2. Trimming and quality filtering](#trimming-and-quality-filtering)

- [3. Post-trimming quality check](#post-trimming-quality-check)

- [4. Trimming using job arrays](#trimming-using-job-arrays)


<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>




## 1. Examining read quality


Once we have demultiplexed the data, we will want to check the quality of the reads, and check for the presence of Illumina adapters. You may also wish to do this on the combined reads before demultiplexing, however, we know that we have barcodes on each read that will need to be removed in the demultiplexing step, and so we won't do that here. If we see very poor quality in these demultiplexed FASTQ files, then we would want to go back and check on the quality of the combined FASTQ to determine if the issue started with our raw data or some weird error in demultiplexing.


To check the quality of our reads, we'll use a tool FASTQC. This runs very fast and is very simple, and we're going to be waiting on the results anyways, so we'll run it interactively here, and on only a subset of the FASTQ files so that it will be very fast. If running FASTQC on many files, you may want to write a slurm script to submit this as a job instead.


Let's start by creating a directory with only a subset of the demultiplexed FASTQ files

```
cd <PATH_TO_DIRECTORY_CONTAINING_DEMUXED_FASTQs>
mkdir demux_subset
cp SD_Field_1453.fastq.gz SD_Field_12* SD_Field_0506.fastq.gz demux_subset
cd demux_subset
```

Then we can start up an interactive session and run fastqc on all FASTQ files in this subset directory.

```
salloc --account=<YOUR_ACCOUNT>  -t 0-1:00:00 --mem=4G --nodes=1 --ntasks-per-node=6
module load swset gcc fastqc/0.11.7 # load the modules necessary
mkdir fastqc_out
fastqc -t 6 *.fastq.gz -o fastqc_out
```

The `-t` argument for fastqc tells it how many cores to use. We'll use multiple since we're running it on multiple files. The next argument, and the only requirement at all, is a fastq file or list of files. Here we provide it a list of files by using the `*` wildcard to tell it to run on all files in the current directory that end with `fastq.`. We have also used the `-o` option to tell fastqc where to put the output. Unlike some other programs, fastqc will not create this directory if it does not already exist, which is why created it on the previous line.


Fastqc will generate a report for each FASTQ file in the output directory. We can look at each individually, or we can use multiqc to aggregate the results.


```
cd fastqc_out

module load miniconda3/4.9.2 # we alread have swset gcc loaded
conda create -n multiqc
conda activate multiqc
conda install -c bioconda -c conda-forge multiqc

## The . in the next line command the present directory
##   this tells multiqc to look for output in the current directory
multiqc .
```

Download the report from multiqc to your local machine.

```
## DO THIS FROM A TERMINAL WINDOW *NOT* CONNECTED TO TETON
rsync -raz --progress <yourusername>@teton.uwyo.edu:<your_path_to_/multiqc_report.html> ~/Desktop
```

This should download the file to your desktop. If you run this on a Windows machine, you may need to edit ~/Desktop to reflect the Windows location of the desktop, we have not run this on Windows.

An alternative to using `rsync` or `scp` for uploading or downloading files from Teton is to use a program like Filezilla or Cyberduck, which let you drag and drop files and view the Teton file system in a way that looks more like the typical file navigators on Mac or Windows.

If you double click this file, it should open up in the default web browser. Let's take a look and go over some of these. From the start, in `General Statistics`, we can see that `SD_Field_0506` has very few sequences and `SD_Field_1453` doesn't have very many either. If we remember from our iPyRad assemblies last week, both of these samples ended up with few loci overlapping other samples, and this is why. This is further evidence that these are failed samples and should be removed.

When we look at the `% Dups` in the `General Statistics`, we see what are at first alarmingly high numbers. However, this is because FastQC is designed for whole genome shotgun sequence data, where the genome is randomly sheared before sequencing. In that case, if two reads are identical, it likely means that they sequenced two PCR duplicates of the same starting molecule, instead of two different starting molecules. In RAD and other reduced-representation library methods, we explicitly enrich for specific loci, with each individual locus starting at the same position. This results in lots of identical reads, even if they start from different, sequencing from the same start site each time: we will end up with lots of copies of one or two (if heterozygous) identical sequences. This is roughly what is happening here.

The sequence quality histograms look good, with most qualities falling above 30, with slightly decreasing quality as the read progresses, as is common. If we had paired end reads, we would see that those reads would generally be slightly worse quality, with a faster and sharper quality drop off in quality through the read as a result of the order in which reads are sequenced and the chemistry of the sequencer.

In the `Per Base Sequence Content` section, we see that we have identical sequences at the beginning of each read. This is because we have the same restriction overhang at the start of each read by the nature of RADseq. This is another finding that would be cause for concern for whole genome data, but is expected with RADseq.

The GC content for sample `SD_Field_1453` looks very strange, further evidence that we should not use this sample moving forward. Farther down, we also see that `SD_Field_1453` also has a lot of over-represented sequences, most likely indicating some issue with library prep for this sample.

Looking at `Adapter Content` we can see that we have very little adapter present. his isn't terribly surprising because these are 100 bp single-end reads on DNA fragments that were size selected to 415–515 bp.

Most of the rest of the checks either look good or are different ways of showing what we've discussed above.

<br><br><br>

## 2. Trimming and quality filtering

Next up, we'll use the tool [Trimmomatic](http://www.usadellab.org/cms/?page=trimmomatic) to trim out any remaining adapters, as well trim reads for quality. This will remove portions of reads with low quality scores and entire reads if the entire read is of low quality or the length of the remaining read falls below the `MINLEN` threshold.

Let's set this up as a job by creating a new slurm script to submit the job to Teton:


```
cd .. # go to your demux_subset directory
# Let's delete SD_Field_1453.fastq and SD_Field_0506.fastq since we've 
#    decided these are overall low quality samples and to speed this part up
rm  SD_Field_1453.fastq.gz SD_Field_0506.fastq.gz
nano trim.slurm # open and edit a new file
```

Then add the following to the file, then close and save it

```
#!/bin/sh

#SBATCH --job-name Trim
#SBATCH -A <YOUR_ACCOUNT>
#SBATCH -p teton
#SBATCH -t 1-00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=5G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<YOUR_EMAIL>
#SBATCH -e trim_%A_%a.err
#SBATCH -o std_trim_%A_%a.out

module load swset/2018.05  gcc/7.3.0 trimmomatic/0.36

cd <PATH_TO_YOUR/demux_subset>

# create a loop to run trimmomatic on each of the samples in the 
#    current directory that ends with .fastq
for x in *fastq.gz; do 
	trimmomatic  SE -threads 6 $x trimmed_$x \
	ILLUMINACLIP:/project/inbre-train/2021_popgen_wkshp/data/TruSeq3-PE-2.fa.txt:2:30:10 \
	LEADING:3 TRAILING:3 MINLEN:36
done

# put the trimmed reads into a new directory
mkdir trimmed_reads
mv trimmed_*fastq.gz trimmed_reads
```

Now we can submit this job using:

```
sbatch trim.slurm
```

We should rapidly start to see the trimmed file pop up and this should finish quickly.


Note that here we have trimmed adapters and low quality bases and reads, but our reads still have the restriction overhangs attached to them. If this was the main way that we were planning to handle our RAD data for analyses moving forward, we would want to further clean these up or use different trimming settings to remove these, but we won't go through that here. For RAD data it's typically simpler to use one of the existing pipelines like iPyRad, and for other types of data this won't be necessary.

If you are dealing with paired end data, you will need to feed trimmomatic both your foward and reverse reads as input and specify more output files for forward and reverse reads, and reads of each that after trimming either do or or do not retain their matched read.

<br><br><br>

## 3. Post-trimming quality check

Once the trimming has completed, we can run another round of FASTQC on these trimmed reads.

```
salloc --account=<YOUR_ACCOUNT>  -t 0-0:30:00 --mem=4G --nodes=1 --ntasks-per-node=4
module load swset gcc fastqc/0.11.7 miniconda3/4.9.2 # load the modules necessary
cd trimmed_reads
mkdir fastqc_out
fastqc -t 4 *.fastq.gz -o fastqc_out

cd fastqc_out
conda activate multiqc
multiqc .
```

Then we can download that new multiqc report and it should look better than the old one. Let's rename it so it doesn't overwrite, then download.

```
mv multiqc_report.html multiqc_report_Trimmed.html

rsync -raz --progress <yourusername>@teton.uwyo.edu:<your_path_to_/multiqc_report_Trimmed.html> ~/Desktop
```


This should all be familiar, and other than the few RAD-specific things like duplicates and some overhangs that are present, we shouldn't see anything else of concern at this point.

<br><br><br>

## 4. Trimming using job arrays

When we trimmed our files above, we used a simple loop to trim all of the fastq files. This works well enough if you have relatively few, relatively small fastq files. However, if you have many, large files, using a loop that goes over them sequentially can take quite a while. My preferred solution to this is to use job arrays. This is an automated way of submitting replicate jobs as part of a single larger job, such that each "sub-job" can run in parallel, and all jobs can be submitted with a single slurm script and sbatch command. 



The below will submit such a job array where each job will process a single fastq file when saved and run as a slurm script.

```
#!/bin/bash

#SBATCH --job-name Trim
#SBATCH -A <YOUR_ACCOUNT>
#SBATCH -p teton
#SBATCH -t 1-00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=24G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<YOUR_EMAIL>
#SBATCH -e err_trim_%A_%a.err
#SBATCH -o std_trim_%A_%a.out
#SBATCH --array=1-40


# load modules necessary to use conda on Teton
module load swset/2018.05  gcc/7.3.0 trimmomatic/0.36

# Set working directory to where the fastqs are
cd <YOUR_DIRECTORY_TO_FASTQs_toTRIM>


for x in *fastq.gz; do   # use a loop to find all the files that end in fastq.gz and assign them to a bash array
  trimfiles=(${trimfiles[@]} "${x}")
done


## For whichever SLURM_ARRAY_TASK_ID index a job is in, get the sample 
##     name to simplify the trimmomatic call below
## here, I subtract 1 from the $SLURM_ARRAY_TASK_ID because bash indexing starts at zero
##   I think it's less confusing to subtract 1 here than to remember to do it when 
##   specifying the number of jobs for the array
sample=${trimfiles[($SLURM_ARRAY_TASK_ID-1)]}

# Run trimmomatic on each file

	trimmomatic  SE -threads 6 $sample trimmed_$sample \
	ILLUMINACLIP:/project/inbre-train/2021_popgen_wkshp/data/TruSeq3-PE-2.fa.txt:2:30:10 \
	LEADING:3 TRAILING:3 MINLEN:36

# put the trimmed reads into a directory
mkdir trimmed_reads
mv trimmed_*fastq.gz trimmed_reads
```


Ensure that `#SBATCH --array=` is set to the correct number of jobs that you are running for any given job array. The script will effectively loop submit your job over the indices in that argument, replacing `$SLURM_ARRAY_TASK_ID` with the current index for each submission.


