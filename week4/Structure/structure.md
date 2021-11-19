---
title: Admixture Analysis
date: November 12, 2021
---



## Table of Contents


- [1. Preparing Input File](#preparing-input-file)

- [2. Parallelizing Structure](#parallelizing-structure)

- [3. Running Structure and Processing Output](#running-structure-and-processing-output)

- [4. Visualizing Admixture](#visualizing-admixture)



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

Converting files from one format to another is commonplace in most population genomic analysis. In this exercise, we will be converting the VCF file from ipyrad to a structure formatted input file. We will use ``PGDSpider``, which can convert between a large number of formats.


```bash
cd vcf

ls -lh

-rw-rw-r-- 1 vchhatre 2.6M Nov 17 15:37 ruber_reduced_ref.vcf

```

- Quickly generate summary of the VCF file:


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

<br><br>

## 1.1 PGDSpider Template File


PGDspider needs a template file, which can be generated from it's GUI version. This file has already been generated for you, which will simply need to be modified.


```bash

mkdir Admixture && cd Admixture

cp /project/inbre-train/2021_popgen_wkshp/data/Admixture/vcf2str.spid .

```

- Open the file

```bash
vim vcf2str.spid
```

```bash

# VCF Parser questions
PARSER_FORMAT=VCF

# Only output SNPs with a phred-scaled quality of at least:
VCF_PARSER_QUAL_QUESTION=
# Select population definition file:
VCF_PARSER_POP_FILE_QUESTION=crovir.pop
# What is the ploidy of the data?
VCF_PARSER_PLOIDY_QUESTION=DIPLOID
# Do you want to include a file with population definitions?
VCF_PARSER_POP_QUESTION=true
# Output genotypes as missing if the phred-scale genotype quality is below:
VCF_PARSER_GTQUAL_QUESTION=
# Do you want to include non-polymorphic SNPs?
VCF_PARSER_MONOMORPHIC_QUESTION=false
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

# STRUCTURE Writer questions
WRITER_FORMAT=STRUCTURE

# Specify the locus/locus combination you want to write to the STRUCTURE file:
STRUCTURE_WRITER_LOCUS_COMBINATION_QUESTION=
# Do you want to include inter-marker distances?
STRUCTURE_WRITER_LOCI_DISTANCE_QUESTION=false
# Specify which data type should be included in the STRUCTURE file  (STRUCTURE can only analyze one data type per file):
STRUCTURE_WRITER_DATA_TYPE_QUESTION=SNP
# Save more specific fastSTRUCTURE format?
STRUCTURE_WRITER_FAST_FORMAT_QUESTION=false

```


<br><br>

## 1.2 Population (``.pop``) File

This is a two column file:

	- Individual ID
	- Population ID

The authors of this data set originally did not have an apriori hypothesis about the size and locations of populations. We are just going to loosely group the individuals into ``North`` and ``South`` populations. This does not have any effect on the analysis we are going to do, but having a population column helps with visualization of results.  Get the population file below:


```bash

cp /project/inbre-train/2021_popgen_wkshp/data/Admixture/crovir.pop .

head crovir.pop

SD_Field_0201	north
SD_Field_0255	south
SD_Field_0386	south
SD_Field_0491	south
SD_Field_0492	admixed
SD_Field_0493	south
SD_Field_0557	south
SD_Field_0598	admixed
SD_Field_0599	south
SD_Field_0642	admixed
```

- As you can see, there are 3 populations in this file: north, admixed and south.



<br><br>


### 1.3 Convert VCF to .STR

- Now we have everything we need to convert the VCF file to structure format.

- Create a new script ``vcf2str.sh``

```bash

#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=100G
#SBATCH --mail-type=NONE
#SBATCH -J vcf2str
#SBATCH --account=YOUR_PROJECT

module load gcc swset pgdspider

url="/path/to/your/Admixture/Folder/"

pgdspider -inputfile $url/ruber_reduced_ref.vcf -inputformat VCF -outputfile $url/crovir.str -outputformat STRUCTURE -spid $url/vcf2str.spid

```

- Run the script to generate structure file

```bash
sbatch vcf2str.sh
```

- The script should finish within a few seconds. Once it's done, take a look at the output file:


```bash
vim ruber.str
```


<br><br>


## 2. Parallelize Structure 

- As you might know, the program STRUCTURE is not optimized for working with multiple processors. This behavior can be changed by using one of the many parallelization routines available. We will use the one from [strauto.popgen.org](https://strauto.popgen.org). Go ahead and download the archive to your local workstation.


```bash
cd ~

mkdir admixture

cd admixture

ls -lh

-rw-r--r--@ 1 vikram  staff   197K Apr  7  2019 strauto_1.tar.gz

```

- Uncompress the archive

```bash
tar -xzvf strauto_1.tar.gz

x input.py
x py3/
x py3/strauto_1.py3
x py3/sampleStructureFile.py3
x sampleStructureFile.py
x sim.str
x strauto_doc.pdf
x strauto_1.py

```

- Open the ``input.py`` file which is the settings template for this program:


```bash
vim input.py
```

```bash

## 1. How many populations are you assuming? [Integers]
maxpops = 4

## 2. How many burnin you wish to do before collecting data [Integers]
burnin = 50000

## 3. How long do you wish to collect the data after burnin [Integers]
mcmc = 100000

## 4. Name of your dataset.  Don't remove quotes. No spaces allowed. Exclude the '.str' extension.  
##    e.g. dataset = "sim" if your datafile is called 'sim.str'
dataset = "ruber"

## 5. How many runs of Structure do you wish to do for every assumed cluster K? [Integers]
kruns = 5

## 6. Number of individuals [Integers]
numind = 33

## 7. Number of loci [Integers]
numloci = 4562

## 8. What is the ploidy [Integers 1 through n]
ploidy = 2

## 9. How is the missing data coded? Write inside quotes. e.g. missing = "-9"
missing = "-9"

## 10. Does the data file contain every individual on 2 lines (0) or 1 line (1). [Boolean]
onerowperind = 0 

## 11. Do the individuals have labels in the data file?  [Boolean]
label = True

## 12. Are populations identified in the data file? [Boolean]
popdata =  True

## 13. Do you wish to set the popflag parameter? [Boolean]
popflag = False

## 14. Does the data file contain location identifiers (Not the same as population identifier) [Boolean]
locdata = False

## 15. Does the data file contain phenotypic information? [Boolean]
pheno = False

## 16. Does the data file contain any extra columns before the genotype data begins? [Boolean]
extracols = False

## 17. Does the data file contain a row of marker names at the top? [Boolean]
markers = True

## 18. Are you using dominant markers such as AFLP? [Boolean]
dominant = False

## 19. Does the data file contain information on map locations for individual markers? [Boolean]
mapdist = False

## 20. Is the data in correct phase? [Boolean]
phase = False

## 21. Is the phase information provided in the data? [Boolean]
phaseinfo = False

## 22. Does the phase follow markov chain? [Boolean]
markov = False

## 23. Do you want to make use of parallel processing [Boolean]
##     Note that you must have GNU parallel installed and available
##     www.gnu.org/s/parallel
##     You can check availability of the program by running 'which parallel' at the 
##     command prompt. If a destination of the file is returned, then it is available.
##     If not available, it must be installed locally or through your system administrator.

parallel = True

## 24. How would you like to define the number of cores for parallel processing ['number' or 'percent']
##     Use 'percent' if you would like to define the percentage of available cores to use.  For instance,
##     on a quad-core machine you might use 'percent' here and '75' for cores to use 3 of the 4 processors.
##     Use 'number' if you want to explicitely define the number of cores used.  

core_def = 'number'

## 25. How many cores would you like to use [integer]
##     This represents either a pecentage or the physical number of cores as defined in core_def (#24).

cores = 16

## 26. Would you like to automatically run structureHarvester?  [boolean]
##     Note that you must have program installed and available.
##     https://users.soe.ucsc.edu/~dearl/software/structureHarvester/

harvest = False

```

- Save and close the file, then fire up Strauto.


```bash
python strauto_1.py
```

- Hit enter on the first screen and you will be presented with the following screen:


```bash

input.py found. Proceeding!
----------------------------------------------------------------------
  Finished entering data for 'ruber'.  Verify your information.
----------------------------------------------------------------------
              Maximum number of assumed populations :   4
                                   Number of burnin :   50000
                                Number of MCMC reps :   100000
                                    Name of dataset :   ruber
                               Number of runs per K :   5
                              Number of individuals :   33
                                     Number of loci :   4562
                                       Ploidy level :   2
                           Missing data is coded as :   -9
               Data for every individual on 1 line? :   0
              Data file contains individual labels? :   True
     Does data file contain population identifiers? :   True
                                  Popflag is set to :   False
                            Location data is set to :   False
                 Does data file contain phenotypes? :   False
             Does data file have any extra columns? :   False
    Does data file contain a row with marker names? :   True
                    Are you using dominant markers? :   False
              Does data file contain map distances? :   False
                      Is the data in correct phase? :   False
     Does data file contain phase information line? :   False
                    Does phase follow Markov chain? :   False
                               Use parallelization? :   True
       Define number of cores or percentage of cores:   number
          How many cores (number of, or % of total) :   16
             Run Structure Harvester automatically? :   False
----------------------------------------------------------------------
                  (a)ccept to start writing output files.
                     (q)uit if you find errors above.
            Then correct the input file and rerun this script


```

- Check to make sure all the settings are as we want them. Then type ``a`` for accept and hit enter. 


```bash

Now writing 'mainparams' file for ruber!
 
Now writing 'extraparams' with default values for ruber!

-------------------------------

Checking for Structure binary

------------------------------------------------------------------------------------------
Structure is not in the $PATH or in the current working directory. Scripts will be created
referencing this executable in the working directory. You will need to do have this
executable available in order to run any script created.


-----------------------------------------

Now writing 'runstructure' shell script



-----------------------------------------------------------------------------
In order to run the output scripts you need to have access to GNU parallel.
Please visit: http://www.gnu.org/software/parallel/
All scripts will be created but cannot be run until parallel is available.

```

- There should be two main output files in the current directory:

	- ``runstructure`` script

	- ``structureCommands`` script

- Take a look at both:


```bash
vim runstructure
```

```bash
#!/bin/sh 
mkdir results_f log harvester
mkdir k1
mkdir k2
mkdir k3
mkdir k4

cd log
mkdir k1
mkdir k2
mkdir k3
mkdir k4

cd ..

cat structureCommands | parallel -j 16

mv k1 k2 k3 k4  results_f/
mkdir harvester_input
cp results_f/k*/*_f harvester_input
echo 'Your structure run has finished.'
#Clean up harvester input files.
zip ruber_Harvester_Upload.zip harvester_input/*
mv ruber_Harvester_Upload.zip harvester/
rm -rf harvester_input

```

- Now we need to convert this simple bash script so it will work on Teton:


```bash

#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mail-type=NONE
#SBATCH -J admix
#SBATCH --account=YOUR_PROJECT

module load gcc swset parallel structure

mkdir results_f log harvester
mkdir k1
mkdir k2
mkdir k3
mkdir k4

cd log
mkdir k1
mkdir k2
mkdir k3
mkdir k4

cd ..

cat structureCommands | parallel -j 16

mv k1 k2 k3 k4  results_f/
mkdir harvester_input
cp results_f/k*/*_f harvester_input
echo 'Your structure run has finished.'
#Clean up harvester input files.
zip ruber_Harvester_Upload.zip harvester_input/*
mv ruber_Harvester_Upload.zip harvester/
rm -rf harvester_input

```

- Save and close this file. Then open ``structureCommands``


```bash
vim structureCommands
```

- As described in the Strauto user manual section #8, we need to append some SLURM specific commands at the beginning of each line on this file.

- The command we need to prepend to each line is:

	``srun -N1 -n1 --exclusive``


- In vim:

```bash

:%s/^\.\///g

:%s/^/srun \-N1 \-n1 \-\-exclusive  /g

:wq

```

- The script should now look something like this:


```bash

srun -N1 -n1 --exclusive structure -D 583084 -K 1 -m mainparams -o k1/ruber_k1_run1 2>&1 > log/k1/ruber_k1_run1.log
srun -N1 -n1 --exclusive structure -D 314748 -K 1 -m mainparams -o k1/ruber_k1_run2 2>&1 > log/k1/ruber_k1_run2.log
srun -N1 -n1 --exclusive structure -D 657495 -K 1 -m mainparams -o k1/ruber_k1_run3 2>&1 > log/k1/ruber_k1_run3.log
srun -N1 -n1 --exclusive structure -D 307315 -K 1 -m mainparams -o k1/ruber_k1_run4 2>&1 > log/k1/ruber_k1_run4.log
srun -N1 -n1 --exclusive structure -D 683833 -K 1 -m mainparams -o k1/ruber_k1_run5 2>&1 > log/k1/ruber_k1_run5.log
srun -N1 -n1 --exclusive structure -D 518435 -K 2 -m mainparams -o k2/ruber_k2_run1 2>&1 > log/k2/ruber_k2_run1.log
srun -N1 -n1 --exclusive structure -D 333897 -K 2 -m mainparams -o k2/ruber_k2_run2 2>&1 > log/k2/ruber_k2_run2.log
srun -N1 -n1 --exclusive structure -D 493448 -K 2 -m mainparams -o k2/ruber_k2_run3 2>&1 > log/k2/ruber_k2_run3.log
srun -N1 -n1 --exclusive structure -D 967055 -K 2 -m mainparams -o k2/ruber_k2_run4 2>&1 > log/k2/ruber_k2_run4.log
srun -N1 -n1 --exclusive structure -D 836430 -K 2 -m mainparams -o k2/ruber_k2_run5 2>&1 > log/k2/ruber_k2_run5.log
srun -N1 -n1 --exclusive structure -D 703354 -K 3 -m mainparams -o k3/ruber_k3_run1 2>&1 > log/k3/ruber_k3_run1.log
srun -N1 -n1 --exclusive structure -D 429104 -K 3 -m mainparams -o k3/ruber_k3_run2 2>&1 > log/k3/ruber_k3_run2.log
srun -N1 -n1 --exclusive structure -D 784866 -K 3 -m mainparams -o k3/ruber_k3_run3 2>&1 > log/k3/ruber_k3_run3.log
srun -N1 -n1 --exclusive structure -D 956357 -K 3 -m mainparams -o k3/ruber_k3_run4 2>&1 > log/k3/ruber_k3_run4.log
srun -N1 -n1 --exclusive structure -D 377533 -K 3 -m mainparams -o k3/ruber_k3_run5 2>&1 > log/k3/ruber_k3_run5.log
srun -N1 -n1 --exclusive structure -D 799643 -K 4 -m mainparams -o k4/ruber_k4_run1 2>&1 > log/k4/ruber_k4_run1.log
srun -N1 -n1 --exclusive structure -D 129610 -K 4 -m mainparams -o k4/ruber_k4_run2 2>&1 > log/k4/ruber_k4_run2.log
srun -N1 -n1 --exclusive structure -D 705345 -K 4 -m mainparams -o k4/ruber_k4_run3 2>&1 > log/k4/ruber_k4_run3.log
srun -N1 -n1 --exclusive structure -D 305582 -K 4 -m mainparams -o k4/ruber_k4_run4 2>&1 > log/k4/ruber_k4_run4.log
srun -N1 -n1 --exclusive structure -D 804930 -K 4 -m mainparams -o k4/ruber_k4_run5 2>&1 > log/k4/ruber_k4_run5.log

```

- Go ahead and upload these two scripts to the Admixture folder on Teton where the rest of your files are:


```bash
rsync -raz structureCommands runstructure mainparams extraparams teton:/path/to/your/Admixture/Folder/
```


<br><br>

## 3. Running Structure and Processing Output



- Once the files are all uploaded, go ahead and execuse the script:


```bash
sbatch runstructure
```


<br><br>

### 3.1 Assessing Structure Output

- The script will create multiple folders in your current directory structure and start writing log and output files. The analysis may last a few hours.  But when it's done, you will have following results.

```bash

ls -lh

drwxrwsr-x 6 vchhatre 4.0K Nov 18 11:19 log
-rw-rw-r-- 1 vchhatre  140 Nov 18 12:01 seed.txt
drwxrwsr-x 6 vchhatre 4.0K Nov 18 13:34 results_f
-rw-rw-r-- 1 vchhatre 1.2K Nov 18 13:34 slurm-15640920.out
drwxrwsr-x 2 vchhatre 4.0K Nov 18 13:34 harvester

```

- Take a look inside the ``log`` and ``results_f`` folders:

```bash

ls -othr log/* results_f/*

log/k1:
total 480K
-rw-rw-r-- 1 vchhatre 84K Nov 18 12:00 ruber_k1_run5.log
-rw-rw-r-- 1 vchhatre 84K Nov 18 12:00 ruber_k1_run2.log
-rw-rw-r-- 1 vchhatre 84K Nov 18 12:01 ruber_k1_run1.log
-rw-rw-r-- 1 vchhatre 84K Nov 18 12:01 ruber_k1_run4.log
-rw-rw-r-- 1 vchhatre 84K Nov 18 12:03 ruber_k1_run3.log

log/k2:
total 800K
-rw-rw-r-- 1 vchhatre 158K Nov 18 12:17 ruber_k2_run2.log
-rw-rw-r-- 1 vchhatre 158K Nov 18 12:17 ruber_k2_run1.log
-rw-rw-r-- 1 vchhatre 158K Nov 18 12:17 ruber_k2_run5.log
-rw-rw-r-- 1 vchhatre 158K Nov 18 12:17 ruber_k2_run4.log
-rw-rw-r-- 1 vchhatre 158K Nov 18 12:17 ruber_k2_run3.log

log/k3:
total 960K
-rw-rw-r-- 1 vchhatre 187K Nov 18 12:32 ruber_k3_run2.log
-rw-rw-r-- 1 vchhatre 187K Nov 18 12:32 ruber_k3_run4.log
-rw-rw-r-- 1 vchhatre 187K Nov 18 12:32 ruber_k3_run5.log
-rw-rw-r-- 1 vchhatre 187K Nov 18 12:32 ruber_k3_run1.log
-rw-rw-r-- 1 vchhatre 187K Nov 18 12:33 ruber_k3_run3.log

log/k4:
total 1.2M
-rw-rw-r-- 1 vchhatre 231K Nov 18 12:46 ruber_k4_run1.log
-rw-rw-r-- 1 vchhatre 231K Nov 18 13:26 ruber_k4_run2.log
-rw-rw-r-- 1 vchhatre 231K Nov 18 13:33 ruber_k4_run4.log
-rw-rw-r-- 1 vchhatre 231K Nov 18 13:33 ruber_k4_run5.log
-rw-rw-r-- 1 vchhatre 231K Nov 18 13:34 ruber_k4_run3.log

results_f/k1:
total 2.3M
-rw-rw-r-- 1 vchhatre 456K Nov 18 12:00 ruber_k1_run5_f
-rw-rw-r-- 1 vchhatre 456K Nov 18 12:00 ruber_k1_run2_f
-rw-rw-r-- 1 vchhatre 456K Nov 18 12:01 ruber_k1_run1_f
-rw-rw-r-- 1 vchhatre 456K Nov 18 12:01 ruber_k1_run4_f
-rw-rw-r-- 1 vchhatre 456K Nov 18 12:03 ruber_k1_run3_f

results_f/k2:
total 2.5M
-rw-rw-r-- 1 vchhatre 510K Nov 18 12:17 ruber_k2_run2_f
-rw-rw-r-- 1 vchhatre 510K Nov 18 12:17 ruber_k2_run1_f
-rw-rw-r-- 1 vchhatre 510K Nov 18 12:17 ruber_k2_run5_f
-rw-rw-r-- 1 vchhatre 510K Nov 18 12:17 ruber_k2_run4_f
-rw-rw-r-- 1 vchhatre 510K Nov 18 12:17 ruber_k2_run3_f

results_f/k3:
total 2.9M
-rw-rw-r-- 1 vchhatre 564K Nov 18 12:32 ruber_k3_run2_f
-rw-rw-r-- 1 vchhatre 564K Nov 18 12:32 ruber_k3_run4_f
-rw-rw-r-- 1 vchhatre 564K Nov 18 12:32 ruber_k3_run5_f
-rw-rw-r-- 1 vchhatre 564K Nov 18 12:32 ruber_k3_run1_f
-rw-rw-r-- 1 vchhatre 564K Nov 18 12:33 ruber_k3_run3_f

results_f/k4:
total 3.1M
-rw-rw-r-- 1 vchhatre 618K Nov 18 12:46 ruber_k4_run1_f
-rw-rw-r-- 1 vchhatre 618K Nov 18 13:26 ruber_k4_run2_f
-rw-rw-r-- 1 vchhatre 618K Nov 18 13:33 ruber_k4_run4_f
-rw-rw-r-- 1 vchhatre 618K Nov 18 13:33 ruber_k4_run5_f
-rw-rw-r-- 1 vchhatre 618K Nov 18 13:34 ruber_k4_run3_f

```

- We will now briefly look inside a log file and a results file.



<br><br>

### 3.2 Structure Harvester

- Next, check what's inside Harvester folder:


```bash

ls -lh harvester

-rw-rw-r-- 1 vchhatre 2.1M Nov 18 13:34 ruber_Harvester_Upload.zip

```

- It's a zip file containing all the results from our run. [Structure Harvester](http://taylor0.biology.ucla.edu/structureHarvester/) is a very popular program to visualize results from Structure to understand the extent of population structure present in your data set.

- Download this zip file using rsync to your local workstation.  Then visit the Structure Harvester website, upload the zip file and click ``harvest``.

- Harvester will display all the visualizations and summary files in the browser window. You should then download an archive of all those results to your local workstation.

- One of the output files contains admixture coefficients for all the individuals at various levels that were tested (e.g. K=2, K=3, and K=4). Based on Harvester results, it looks like the optimal number of Hardy Weinberg clusters in this data set is 2. So for further analysis, we will use the admixture coefficients at K=2.

- Check the file named ``k2.indfile``.

```bash

head K2.indfile

  1   1 (19)  1 : 0.000 1.000
  2   2 (22)  1 : 0.000 1.000
  3   3 (26)  1 : 0.056 0.944
  4   4 (35)  1 : 0.000 1.000
  5   5 (29)  1 : 0.000 1.000
  6   6 (16)  1 : 0.000 1.000
  7   7 (20)  1 : 0.001 0.999
  8   8 (19)  1 : 0.000 1.000
  9   9 (29)  1 : 0.000 1.000
 10  10 (38)  1 : 0.000 1.000

```

- The last two columns in this file are admixture coefficients. These coefficients indicate the amount of ancestry each individual draws from the two HW clusters. 

- Check the number of lines in this file. It's at least ``33 * 5 = 165``. Why is this? It's because the admixture coefficients are printed for each of the 5 iterations we performed in Structure. In an ideal world, we would have time to process this output through the cluster matching program CLUMPP which takes all of these admixture matrices and outputs a single best matrix which can then be used for visualization. Since we do not have time to go through that process, we will use the coefficients from the first iteration at K=2.


```bash

sed -n 1,33p K2.indfile > ruber_k2.indfile

vim ruber_k2.indfile

```

- Now we wish to get rid of everything in this file except the last two columns. We will replace multiple spaces between columns with a single tab:


```bash
:%s/\s\+/\t/g

:wq
```

- Then we will cut out the last two columns (no. 6 & 7)


```bash

cut -f6-7 ruber_k2.indfile > ruber_k2.admix

head ruber_k2.admix

0.000	1.000
0.000	1.000
0.056	0.944
0.000	1.000
0.000	1.000
0.000	1.000
0.001	0.999
0.000	1.000
0.000	1.000
0.000	1.000

```

- Rename this file to ``ruber_k2.2.meanQ``

- Now we can use this file for visualizing admixture results:



<br><br>


## 4. Visualizing Admixture


- In addition to the ``ruber_k2.2.meanQ`` file, we are going to need a couple of files:

	- A popfile, containing one population name per individual
	- A poporder file, denoting the order in which populations should appear on the plot

- We already have the popfile (``crovir.pop``). However, we could not use that file. Remember that when you used PGDSpider to convert VCF file to Structure format, it changed the order of individuals. We must use the same order of individuals as in the structure file.

```bash

cut -f2 ruber.str > ruber.pop

cat ruber.pop

1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
3
3
3
3
3
3
3
3
3
3

```

- Keep in mind that ``1=North``, ``2=South``, and ``3=Admixed``.  Let's run a quick replacement:


```bash

vim ruber.pop

:%s/1/North/g
:%s/2/South/g
:%s/3/Admixed/g

:w ruber.pop
:q
```

- Finally make a file with population order as follows:

```bash

vim poporder

North
Admix
South

:wq
```

<br><br>


### 4.1 Distruct Plotting Script

- Next, let's get the distruct plotting script from [distruct2.popgen.org](https://distruct2.popgen.org). Once you download the archive, uncompress it:


```bash

tar -xzvf distruct2.3.tar.gz

```

- Make sure the following files are present in the folder:

	- ``ruber_k2.2.meanQ``
	- ``poporder``
	- ``popfile``

- Then execute the script as follows:


```bash
python distruct2.3.py -K 3
	--input=ruber_k2
	--output=ruber_k2.pdf
	--title="Population Structure in Crotalus ruber"
	--popfile=ruber.pop
	--poporder=poporder

```













