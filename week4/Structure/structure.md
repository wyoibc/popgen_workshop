---
title: Admixture Analysis
date: November 12, 2021
---



## Table of Contents


- [1. Preparing Input File](#preparing-input-file)

- [2. Parallelizing Structure](#parallelizing-structure)

- [3. Running Structure and Processing Output](#processing-output)

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

- Once the files are all uploaded, go ahead and execuse the script:


```bash
sbatch runstructure
```





















