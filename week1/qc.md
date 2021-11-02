---
title: iPyRAD assembly of data for *Crotalus ruber*
author: Sean Harrington & Vikram Chhatre
date: October 29, 2021
---


## Table of Contents


- [1. Introduction](#introduction)

- [2. Files and Basic Setup](#files-and-basic-setup)

- [3. Installing iPyRad](#installing-ipyrad)

- [4. Running iPyRad](#running-ipyrad)

- [5. Branching An Assembly](#branching-an-assembly)

- [6. Examining the output](#examining-the-output)

	- [6.1 Do Another Round of Branching](#do-another-round-of-branching)


<br>
<center>

<img src="Crotalus_ruber_42613167.jpg" width=800 />
</center>

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

For most of the workshop, we'll be working with the same dataset. This is empirical double digest RADseq data ([Peterson et al. 2012](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0037135)) that I (Sean Harrington) generated as part of my PhD at San Diego State University. The data are for a species of rattlesnake, the red diamond rattlesnake (*Crotalus ruber*), that is distributed across the Baja California peninsula and into southern California. I was interested in identifying if there is any population structure in *C ruber* and inferring what population genetic and environmental forces have resulted in any existing structure. The data are single-end reads generated on an Illumina hiSeq. My analyses of these data are published in [Harrington et al. 2018](https://onlinelibrary.wiley.com/doi/full/10.1111/jbi.13114).

[iPyRad](https://ipyrad.readthedocs.io/en/master/) is a flexible python-based pipeline for taking various types of restriction-site associated data, processing them, and generated aligned datasets.

iPyRad is capable of generating datasets either by mapping your raw reads to a reference genome or using a de novo assembly method that does not require a reference. We will use the reference-based method today.

If you need help with iPyRad outside of this workshop for specific issues, you can always post [here](https://gitter.im/dereneaton/ipyrad). Isaac is *very* responsive to queries.

<br><br><br>

## 2. Files and Basic Setup

Before we get started, everyone will need the following files:

- ``all_ruber.fastq``
- ``barcodes_samples.txt``
- ``GCA_003400415.2_UTA_CroVir_3.0_genomic.fna``
- ``names_ruber_all.txt``



These are all contained on Teton at ``/project/inbre-train/2021_popgen_wkshp/data``

To copy these over to your directory, use 

```
cp -r /project/inbre-train/2021_popgen_wkshp/data <where_you_want_these_files>
```

Let's then also create a new directory for the output of our iPyRad assembly. This will make several directories, and it's nice to have them self-contained

```
mkdir ipyrad_out
cd ipyrad_out
```

We'll run this interactively (as long as everyone can get sessions allocated).

```
salloc --account=<YOUR_ACCOUNT> -t 0-2:00:00 --mem=10G --nodes=1 --ntasks-per-node=6
```
If you are unable to quickly get a session allocated with 6 cores, try `--ntasks-per-node=4` instead


<br><br><br>

## 3. Installing iPyRad

We will use conda to install iPyRad and all of its dependencies. To do this, we first have to load up the Teton modules necessary for miniconda

```
module load swset/2018.05 gcc/7.3.0 miniconda3/4.9.2
```

Create a new conda environemtn called ipyrad, activate the environment, and install iPyRad

```
conda create -n ipyrad  # create the environment: we only need to do this once
conda activate ipyrad  ### We will need to run this command every time we want to use ipyrad
conda install ipyrad -c conda-forge -c bioconda  ## We only need to run this once
```

<br><br><br>

## 4. Running iPyRad


First, we need to generate a params file that contains the parameters we need to specify for ipyrad:

```
ipyrad -n ruber_ref   
```

This will create a params file with the defaults that ipyrad uses, we can modify these as we need . Whatever comes after the -n is what the assembly will be named


Let's go look at and edit that
```
nano params-ruber_ref.txt  #if you prefer a different text editor to nano, use that instead
```


We'll change a few of these:

- ``[2]``: this needs to reflect the path to the ``all_ruber.fastq`` file wherever it lives for you 

- ``[3]``: this needs to be the path to ``barcodes_samples.txt`` 

- ``[5]``: change to ``reference`` 

- ``[6]``: change to the path to ``GCA_003400415.2_UTA_CroVir_3.0_genomic.fna`` 

- ``[7]``: dataype should be ``ddrad`` 

- ``[8]``: restriction overhang is: ``TGCAGG, GATC``   these are the overhangs created by the restriction enzymes for ddRAD that was used for these data 

- ``[27]``: change to ``*``, this will generate all output formats that ipyrad is currently capable of  


The rest of these are at generally reasonable values, although depending on your data, you may want to modify some of these. The parameters are all well [**documented here**](https://ipyrad.readthedocs.io/en/master/6-params.html)

Save the file (``ctrl + x``)


Run this for ``steps 1-5``

```
ipyrad -p params-ruber_ref.txt -s 12345 -c 6 # If you had to use 4 cores instead of 6 for salloc, then change this to -c 4
```

We're running this interactively, and it should take around 20 minutes. If you had trouble with getting an interactive ``salloc`` session running, you could also set this up as a job instead.


Instructions for how one would do this:


create and open a new  file to run a slurm job (e.g., ``ruber_ref.slurm``). It should contain the following, with the starred sections for your email and your account replaced with your information:

```bash
#!/bin/bash

#SBATCH --job-name ruber_denovo
#SBATCH -A *****YOUR_ACCOUNT*******
#SBATCH -p teton
#SBATCH -t 2-00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=10G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=*****YOUR_EMAIL*********
#SBATCH -e ruber_%A_%a.err
#SBATCH -o ruber_%A_%a.out

module load swset/2018.05 gcc/7.3.0 miniconda3/4.9.2

## run ipyrad
conda activate ipyrad
ipyrad -p params-ruber_ref.txt -s 12345 -c 8
```

Save that file, then submit the job:

```
sbatch ruber_ref.slurm
```

While our job is running, we can take a look at what's happening in each of the iPyRad steps. These are [**documented here**](https://ipyrad.readthedocs.io/en/master/7-outline.html).

<br><br><br>

## 5. Branching an assembly

The FASTQ that we started with includes most individuals of the red diamond rattlesnake, *Crotalus ruber* but also a few outgroup samples. For the types of analyses we'll be doing downstream, we want to include only *C. ruber* samples.

iPyRad includes functionality to make new "branches" of the assembly using different parameters and/or including/excluding different individuals, and we'll take advantage of that functionality here.

Make a branch of the reference assembly
```
ipyrad -p params-ruber_ref.txt -b ruber_only_ref names_ruber_all.txt
```

This will use our old assembly and params file to generate a new branch, with params file "params-ruber_only_ref.txt" that includes only samples in the "names_ruber_all.txt" file.

We need to further edit this file so that "min_sample per locus" is set to 26 - this is about 75% of individuals. This is param [21] - should be at 4 by default.

```
nano params-ruber_only_ref.txt
```

Once that change has been made, run the final 2 steps in ipyrad:
```
ipyrad -p params-ruber_only_ref.txt -s 67 -c 4 
```

<br><br><br>

## 6. Examining the output

```
cd ruber_only_ref_outfiles
less -S ruber_only_ref_stats.txt
```

There should be 2825 loci recovered in the assembly (or something very similar). If we scroll down a bit, we can see that ``SD_Field_0506`` has almost no loci shared with other samples, and ``SD_Field_1453`` has only about half as many loci as most samples.
We'll want to remove these samples before moving on. Note that ``SD_Field_0506`` is an obviously failed sample, but for ``SD_Field_1453``, you would likely want to try out some preliminary downstream analyses with and without this sample--I've already played with these data and decided it's best to remove it.


### 6.1 Do Another Round of Branching

Start by making a new names file to exclude ``SD_Field_0506`` and ``SD_Field_1453``

```
cd ..
cp names_ruber_all.txt names_ruber_reduced.txt
nano names_ruber_reduced.txt  # delete the lines with the poorly assembled individuals
```


Do the branching:
```
ipyrad -p params-ruber_only_ref.txt -b ruber_reduced_ref names_ruber_reduced.txt
```

Run step 7 on this new branch:
```
ipyrad -p params-ruber_reduced_ref.txt -s 7 -c 4
```



Let's go look at the stats files for each new assembly

```
less -S ruber_reduced_ref_outfiles/ruber_reduced_ref_stats.txt
```


The assembly is down to 2783 loci, a slight decrease, but we now pretty good coverage across individuals.

<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>

