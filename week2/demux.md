---
title: Demultiplexing Samples
date: November 5, 2021
author: Wyoming INBRE Data Science Core
---


## Table of Contents

- [1. Housekeeping: Where Are All Files?](#housekeeping-where-are-all-files)

- [2. Demultiplex using Barcodes](#demultiplex-using-barcodes)

- [3. Truncate Quality Scores](#truncate-quality-scores)










<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>
<br><br><br><br><br><br>



## 1. Housekeeping: Where Are All Files

Let's take inventory of our files, which should be:

- A fastq file containing sequence data on all individuals

- Barcodes that link sequence reads with the individuals they came from


```bash

ls -lh

-rwxrwxr-x 1 vchhatre 6.0G Nov  4 13:06 all_ruber.fastq
-rw-rw-r-- 1 vchhatre  863 Nov  4 13:09 barcodes.txt

```

If you are coming to the workshop for the first time today, please copy these files as follows:


```bash

cd /gscratch/YOUR_USER_NAME/

mkdir rattlesnake

cd rattlesnake/

cp /project/inbre-train/2021_popgen_wkshp/data/all_ruber.fastq .

cp /project/inbre-train/2021_popgen_wkshp/data/barcodes_samples.txt .

```

- Take a quick look inside the barcodes file to know what information we have:

```bash

head barcodes_samples.txt

SD_Field_1453	CTCTCCAG	8
SD_Field_0983	TAATTG	6
SD_Field_1880	ATCTCGT	7
SD_Field_0201	GACAACT	7
SD_Field_2127	CTCGCAA	7
SD_Field_1878	TGGACACT	8
SD_Field_2287	TGTCAAT	7
SD_Field_0598	TCCTGCT	7
SD_Field_1899	GAACTT	6
SD_Field_1205	ATGCT	5

```

- Note that the third field is the length of barcodes. We will need that information in a bit.

<br><br><br>



## 2. Demultiplex using Barcodes

We need to write a simple bash script which will do the following:

- Read barcodes and their respective sample names

- Parse fastq sequence data file and identify reads for a given barcode

- Isolate identified reads into their own files and name these files after the sample name

- Simultaneously delete the barcodes from each read.


In order to accomplish this, we will make use of two unix utilities:

	- ``grep``

	- ``sed``


<br>

### 2.1 The ``demux.sh`` Script


- Please type everything out instead of copy pasting. Yes, you will make mistakes and the script won't work on first try. But you will learn something.

```bash

#!/bin/bash

#SBATCH --time=1:00:00
#SBATCH --mem=20G
#SBATCH --nodes=1
#SBATCH --mail-type=NONE
#SBATCH -J demux
#SBATCH --account=YOUR_PROJECT


## Navigate to the data folder
cd /gscratch/YOUR_ACCOUNT/rattlesnake/


## Create shortcut for the fastq file
ruber="all_ruber.fastq"


## Create output directory
mkdir -p demux_out


## Demultiplexing begins

while read name bar leng
do
  grep -A 2 -B 1 "^$bar" $ruber | sed "s/^$bar//" >> demux_out/${name}.fastq
done < barcodes_samples.txt

```


- At the end of this run, you should have 40 fastq files named after each of the 40 individuals and their barcodes removed.  

- If you recall from introduction to fastq format, the fourth line of each read record contains quality scores per nucleotide. We removed barcodes, but we haven't yet removed quality scores for those barcodes. We need to do that before moving on.


<br><br><br>


## 3. Truncate Quality Scores

We will be using a strategy similar to section 2.1 above to achieve this. This is a two step process:

- Figure out how to capture the fourth line of each read record (i.e. quality score line)

- Use unix ``sed`` tool to keep all quality scores except for those belonging to the removed barcodes


<br>

### 3.1 The ``truncate.sh`` Script


**The ``truncate.sh`` Script**

```bash
#!/bin/bash


cd /gscratch/YOUR_ACCOUNT/rattlesnake

mkdir -p finalfq

while read name barcode leng
do
  sed -E '0~4 s/^.{'"$leng"'}//' demux_out/${name}.fastq >> finalfq/${name}.fastq
done < barcodes_samples.txt

```

This script will produce 40 fastq files in the ``finalfq`` folder and each of these files will have the same length for lines 2 and 4 per read entry.
