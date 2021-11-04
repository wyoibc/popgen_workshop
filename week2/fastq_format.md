---
title: FASTQ format
author: Sean Harrington & Vikram Chhatre
date: November 5, 2021
---


## Table of Contents


- [1. Introduction](#introduction)

- [2. FASTQ format](#fastq-format)



<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>


## 1. Introduction

Last week we ran through some basics of Teton usage and worked through using iPyRad to process our RADseq data. The iPyRad pipeline includes steps to automate the demultiplexing, quality control, trimming, and alignment of our data. This week, we'll handle these steps manually. Whereas the iPyRad pipeline is specific to RADseq and related types of sequence data, the approaches we'll use today are generalizable to any type of genomic or subgenomic DNA sequence data that you may work with, so long as you have a reference genome to map your reads to, although certain datatypes may require tweaking of these steps or additional processing.

### Data from last week
For anyone who did not finish running iPyRad, we have posted all ouput files, as well as the slurm script and params files used to run through last week's session to 

```
/project/inbre-train/2021_popgen_wkshp/week_1_ipyrad_output
```

<br><br><br>

## 2. FASTQ format

We've been working with a fastq file, but so far haven't explored the structure of these files yet. Let's do that. Navigate to where your `all_ruber.fastq` file is located, and we'll look at the fist 8 lines of the file:

```
cd <path_to_your/all_ruber.fastq>
head -n 8 all_ruber.fastq
```

this should return something like this (we've truncated the reads so they fit on a single line here):


```
@SRR6143937.sra.1 1 length=96
TGATCGCTAANAGCAAATTGAGTCCCCTGCCCATCAGTTGATGATGTCATTGGTACTTTCTATTGTGTCA
+SRR6143937.sra.1 1 length=96
IIIIIIIIFD#24AFHJJJJJJIIJJJJJJJJJJJJJIJJJJJJJJJJJJJJJGHIJJJJJJJJJHIJJJ
@SRR6143937.sra.2 2 length=96
TGATCGCTTGNAGGGGGCGCATGAAGAGCGCAGGCACAGAGCAAGGCCCCGCCCTCCCCAGGGACTCATT
+SRR6143937.sra.2 2 length=96
IIIIIIIIFF#22<DHIHJJJJJIJIJJJIJJJJHHHHFFFFFEECDDDDDDDDDDDDDDDDB<@BDDDE
```

Each read from the sequencer is represented by 4 lines: the first 4 lines are the first read, the second set of 4 lines are the seond read, etc. For each read, the first line is the header, and always starts with `@`. This contains a sequence identifier and any various information about the read, often including information about the sequencing run. The second line, after the header, is the actual sequence read. The next line always starts with `+` and may contain either no additional text, or the sequence identifier and extra information, as in the header. Line 4 for each read, following the `+` line, indicates the quality score for each DNA base in the read. You can find the meaning of each of these symbols [here](https://support.illumina.com/help/BaseSpace_OLH_009008/Content/Source/Informatics/BS/QualityScoreEncoding_swBS.htm).

In most cases, fastq files will be stored in a compressed format, with the extension fastq.gz. These can be read and taken as input by many programs, but the command `head` and other simple linux text reading programs will not read thes files. Instead we can use methods that read compressed files directly (e.g., `zless <filename>`) or pipe output from these to something else (e.g., `zcat <filename> | head`).
