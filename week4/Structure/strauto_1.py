#!/usr/bin/env python

##### -----------------------------------------------------------------------------------                       
#####                                                                                                           
#####    strAuto Python Script (v. 1.0)                                                                    
#####    Copyright (C) 2017 by Vikram Chhatre and Kevin Emerson                                  
#####                                                                                                                   
#####    This program is free software: you can redistribute it and/or modify                                   
#####    it under the terms of the GNU General Public License as published by                                   
#####    the Free Software Foundation, either version 3 of the License, or                                      
#####    (at your option) any later version.                                                                    
#####                                                                                                           
#####    This program is distributed in the hope that it will be useful,                                        
#####    but WITHOUT ANY WARRANTY; without even the implied warranty of                                         
#####    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                          
#####    GNU General Public License for more details.                                                           
#####                                                                                                           
#####    You should have received a copy of the GNU General Public License                                      
#####    along with this program.  If not, see <http://www.gnu.org/licenses/>.                                  
#####                                                                                                           
##### -----------------------------------------------------------------------------------                       

## Import libraries we will need.
import os, subprocess, sys, stat, time, textwrap, os, re, random

## Clear screen function
def cls():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
cls()

print "-----------------------------------------------------------------------------------"
print " "
print "                                 StrAuto (version 1.0)"
print "                               "
print " "
print "                     Vikram E. Chhatre (1,2) & Kevin J. Emerson (3)"
print "       (1) Dept. of Plant Biology, University of Vermont, Burlington VT 05405"
print "       (2) INBRE Bioinformatics Core, University of Wyoming, Laramie WY 82071"
print "                             Email: crypticlineage@gmail.com "
print "    (3) Dept. of Biology, St. Mary's College of Maryland, St Marys City, MD 20686"
print "                                Email: kjemerson@smcm.edu"
print " "
print "-----------------------------------------------------------------------------------"
print " "
note1 = "Citation: Chhatre VE & Emerson KJ. StrAuto: Automation and Parallelization of STRUCTURE analysis. BMC Bioinformatics (2017) 18:192"
print " "
print textwrap.fill(note1, 80)
print " "
print "-----------------------------------------------------------------------------------"
print " "
print "                 We will now import your data information from 'input.py'."
print "                  Please make sure this file is in the current directory."
print " "
raw_input("                           Press ENTER to begin...")
print "\n"*200


                                                                                                             
## Function cmd_exists to test if an executable is available in the PATH
def cmd_exists(cmd):
    return subprocess.call(["which", cmd],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


## Check to make sure input.py is present
if os.path.isfile('input.py'):
  print "input.py found. Proceeding!"
else:
  print "input.py not found. Quitting!"
  exit(0)
        

## Function kfolders to print correct number of folders in the shell script.
def kfoldersf():
  mystr = ''.join("mkdir k{}\n".format(x) for x in xrange(1, maxpops+1))
  return mystr

## Function to print names of folders to be moved around through shell script.
def mvfolders():
  mvfold = ''.join("k{} ".format(y) for y in xrange(1, maxpops+1))
  return mvfold 

## Import all the variables from the input.py file
from input import *

## Show all the input info to confirm
print "----------------------------------------------------------------------"
print "Finished entering data for '%s'.  Verify your information.".rjust(60) %dataset
print "----------------------------------------------------------------------"
print "Maximum number of assumed populations :  ".rjust(55), maxpops
print "Number of burnin :  ".rjust(55),  burnin
print "Number of MCMC reps :  ".rjust(55),  mcmc
print "Name of dataset :  ".rjust(55),  dataset
print "Number of runs per K :  ".rjust(55),  kruns
print "Number of individuals :  ".rjust(55),  numind
print "Number of loci :  ".rjust(55),  numloci
print "Ploidy level :  ".rjust(55),  ploidy
print "Missing data is coded as :  ".rjust(55),  missing
print "Data for every individual on 1 line? :  ".rjust(55),  onerowperind
print "Data file contains individual labels? :  ".rjust(55), label
print "Does data file contain population identifiers? :  ".rjust(55),  popdata
print "Popflag is set to :  ".rjust(55),  popflag
print "Location data is set to :  ".rjust(55),  locdata
print "Does data file contain phenotypes? :  ".rjust(55),  pheno
print "Does data file have any extra columns? :  ".rjust(55),  extracols
print "Does data file contain a row with marker names? :  ".rjust(55),  markers
print "Are you using dominant markers? :  ".rjust(55),  dominant
print "Does data file contain map distances? :  ".rjust(55), mapdist
print "Is the data in correct phase? :  ".rjust(55),  phase
print "Does data file contain phase information line? :  ".rjust(55),  phaseinfo
print "Does phase follow Markov chain? :  ".rjust(55),  markov
print "Use parallelization? :  ".rjust(55), parallel
print "Define number of cores or percentage of cores:  ".rjust(55), core_def
print "How many cores (number of, or % of total) :  ".rjust(55), cores
print "Run Structure Harvester automatically? :  ".rjust(55), harvest 
print "----------------------------------------------------------------------"

print "                  (a)ccept to start writing output files."
print "                     (q)uit if you find errors above."
print "            Then correct the input file and rerun this script"
print " "

proceed = ""


while not (re.search(r'a', proceed) or re.search(r'q', proceed)):
    proceed = raw_input(">> ").lower()

## If everything correct, begin writing output files.
    if re.search(r'a', proceed):
        print "Preparing to write..."
        time.sleep(1)
    elif re.search(r'q', proceed):
        print "\nQuitting! Make corrections to input.py\n"
        print "Then please re-run the program.\n\n"
        exit(0)
    else:
        print "Not an acceptable choice. Please try again.\n"

## Clear the screen
cls()

## Message about 'mainparams'
print " "
print "Now writing 'mainparams' file for %s!" % dataset
time.sleep(1)

#################
### Write mainparams based on values in input.py
#################
## Opening the file named mainparams
target = open("mainparams", 'w')
### First the basic parameters
target.write("Basic program parameters\n")
target.write("#define MAXPOPS \t %d\n" % maxpops)
target.write("#define BURNIN  \t %d\n" % burnin)
target.write("#define NUMREPS \t %d\n\n" % mcmc)
### Input file info
target.write("Input file\n")
target.write("#define INFILE \t %s" % dataset +".str\n\n")
### Data information
target.write("Data file format\n")
target.write("#define NUMINDS \t %d\n" % numind)
target.write("#define NUMLOCI \t %d\n" % numloci)
target.write("#define PLOIDY  \t %d\n" % ploidy)
target.write("#define MISSING \t %s\n" % missing)
target.write("#define ONEROWPERIND \t %d\n\n" % onerowperind)
target.write("#define LABEL   \t %d\n" % label)
target.write("#define POPDATA \t %d\n" % popdata)
target.write("#define POPFLAG \t %d\n" % popflag)
target.write("#define LOCDATA \t %d\n" % locdata)
target.write("#define PHENOTYPE \t %d\n" % pheno)
target.write("#define EXTRACOLS \t %d\n" % extracols)
target.write("#define MARKERNAMES \t %d\n" % markers)
target.write("#define RECESSIVEALLELES \t %d\n" % dominant)
target.write("#define MAPDISTANCES \t %d\n\n" % mapdist)
### Advanced Information
target.write("Advanced data file options\n")
target.write("#define PHASED    \t %d\n" % phase) 
target.write("#define MARKOVPHASE \t %d\n" % markov)
target.write("#define NOTAMBIGUOUS \t -999 \n\n")
## Close the file 'mainparams'
target.close()


## Message about 'extraparams'
print " "
print "Now writing 'extraparams' with default values for %s!" % dataset
time.sleep(1)

#################
### Write extraparamss based on default values
#################

target = open('extraparams', 'w')
target.write("#define NOADMIX 0\n")
target.write("#define LINKAGE 0\n")
target.write("#define USEPOPINFO 0\n")
target.write("#define LOCPRIOR 0\n")
target.write("#define FREQSCORR 1\n")
target.write("#define ONEFST 0\n")
target.write("#define INFERALPHA 1\n")
target.write("#define POPALPHAS 0\n")
target.write("#define ALPHA 1.0\n")
target.write("#define INFERLAMBDA 0\n")
target.write("#define POPSPECIFICLAMBDA 0\n")
target.write("#define LAMBDA 1.0\n")
target.write("#define FPRIORMEAN 0.01\n")
target.write("#define FPRIORSD 0.05\n")
target.write("#define UNIFPRIORALPHA 1\n")
target.write("#define ALPHAMAX 10.0\n")
target.write("#define ALPHAPRIORA 1.0\n")
target.write("#define ALPHAPRIORB 2.0\n")
target.write("#define LOG10RMIN -4.0\n")
target.write("#define LOG10RMAX 1.0\n")
target.write("#define LOG10RPROPSD 0.1\n")
target.write("#define LOG10RSTART -2.0\n")
target.write("#define GENSBACK 2\n")
target.write("#define MIGRPRIOR 0.01\n")
target.write("#define PFROMPOPFLAGONLY 0\n")
target.write("#define LOCISPOP 1\n")
target.write("#define LOCPRIORINIT 1.0\n")
target.write("#define MAXLOCPRIOR 20.0\n")
target.write("#define PRINTNET 1\n")
target.write("#define PRINTLAMBDA 1\n")
target.write("#define PRINTQSUM 1\n")
target.write("#define SITEBYSITE 0\n")
target.write("#define PRINTQHAT 0\n")
target.write("#define UPDATEFREQ 100\n")
target.write("#define PRINTLIKES 0\n")
target.write("#define INTERMEDSAVE 0\n")
target.write("#define ECHODATA 1\n")
target.write("#define ANCESTDIST 0\n")
target.write("#define NUMBOXES 1000\n")
target.write("#define ANCESTPINT 0.90\n")
target.write("#define COMPUTEPROB 1\n")
target.write("#define ADMBURNIN 500\n")
target.write("#define ALPHAPROPSD 0.025\n")
target.write("#define STARTATPOPINFO 0\n")
target.write("#define RANDOMIZE 0\n")
target.write("#define SEED 2245\n")
target.write("#define METROFREQ 10\n")
target.write("#define REPORTHITRATE 0\n")
target.close()

## Determine if structure is in the path.  If it is not, add './' to the structure
## calls so that the script looks for structure in the working directory.
print ""
print "-------------------------------"
print ""
print "Checking for Structure binary"
print ""
time.sleep(1)

## Check whether structure binary is in path or in current folder
structureInPath = cmd_exists('structure')
if not structureInPath:
    if not os.path.isfile('structure'):
        print '------------------------------------------------------------------------------------------'
        print 'Structure is not in the $PATH or in the current working directory. Scripts will be created'
        print 'referencing this executable in the working directory. You will need to do have this'
        print 'executable available in order to run any script created.\n\n'
    strprefix = "./"
else:
    strprefix = ""



## Message about 'mainparams'
print "-----------------------------------------"
print ""
print "Now writing 'runstructure' shell script"
print "\n\n"
time.sleep(1)


### Now working with the 'runstructure' shell script
## Create runstructure script and call it 'runstr'
runstr = open("runstructure", 'w')

## Print info about the script
runstr.write("#!/bin/sh \n")

## Create directory structure
runstr.write("mkdir results_f log harvester\n") 
runstr.write(kfoldersf())
runstr.write("\n")
runstr.write("cd log\n")
runstr.write(kfoldersf())
runstr.write("\n")
runstr.write("cd ..\n\n")


## Parallelization routine
if parallel:
    if not cmd_exists('parallel'):
        print '-----------------------------------------------------------------------------'
        print 'In order to run the output scripts you need to have access to GNU parallel.'
        print 'Please visit: http://www.gnu.org/software/parallel/'
        print 'All scripts will be created but cannot be run until parallel is available.\n\n'

    if core_def == "percent":
        postfix = "%"
    elif core_def == "number":
        postfix = ""
    else:
        print "Error in core_def, must be either 'number' or 'percent'."
        print "Quitting now"
        sys.exit()
        
    runstr.write("cat structureCommands | parallel -j {0}{1}\n\n".format(cores, postfix))

    structureCommands = open('structureCommands', 'w')
    for myK in xrange(1, maxpops+1):
        for run in xrange(1, kruns+1):
            structureCommands.write("%sstructure -D %d -K %d -m mainparams -o k%d/%s_k%d_run%d 2>&1 > log/k%d/%s_k%d_run%d.log\n" %
                                    (strprefix, random.randint(100000,999999),myK, myK, dataset, myK, run, myK, dataset, myK, run))
    structureCommands.close()
else:
    for myK in xrange(1, maxpops+1):
        for run in xrange(1, kruns+1):
            runstr.write("%sstructure -D %d -K %d -m mainparams -o k%d/%s_k%d_run%d 2>&1 | tee log/k%d/%s_k%d_run%d.log\n" %
                         (strprefix, random.randint(100000,999999), myK, myK, dataset, myK, run, myK, dataset, myK, run))

## This code is used to move files/folders around after STRUCTURE analysis finishes
runstr.write("mv %s results_f/\n" %mvfolders())
runstr.write("mkdir harvester_input\n")
runstr.write("cp results_f/k*/*_f harvester_input\n")
runstr.write("echo 'Your structure run has finished.'\n")

## Structure Harvester routine
if harvest:
    harvesterInPath = cmd_exists('structureHarvester.py')
    if not harvesterInPath:
        if not os.path.isfile('structureHarvester.py'):
            print 'structureHarvester.py is not in the $PATH or in the current working directory. Scripts will be created'
            print 'referencing this executable in the working directory. You will need to do have this'
            print 'executable available in order to run any script created.\n\n'
        harprefix = "./"
    else:
        harprefix = ""
    runstr.write("# Run structureHarvester\n")
    runstr.write("%sstructureHarvester.py --dir harvester_input --out harvester --evanno --clumpp\n" % harprefix)
    runstr.write("echo 'structureHarvester run has finished.'\n")

runstr.write("#Clean up harvester input files.\n")
runstr.write("zip %s_Harvester_Upload.zip harvester_input/*\n" % dataset)
runstr.write("mv %s_Harvester_Upload.zip harvester/\n" % dataset)
runstr.write("rm -rf harvester_input\n") 


## Close 'runstructure' script and assign rwx permissions to it                
runstr.close()
os.chmod("runstructure", 0755)

exit(0)
