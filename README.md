# CSCI 8360 - Project 1 - Malware Classification

## Synopsis

This project implements a large-scale malware classifier for the [Kaggle Microsoft Maleware Classification Problem](https://www.kaggle.com/c/malware-classification), we developed a Python Spark ([pyspark](https://spark.apache.org/docs/2.2.1/api/python/pyspark.html)) package that implements machine learning techniques to classify malware files. As part of the University of Georgia, Computer Science course CSCI 8360, the software's design centers on execution in the [Google Cloud Platform](https://cloud.google.com/) along with accessing pertenant data through a 
[Google Data Storage Bucket](https://console.cloud.google.com/storage/browser/uga-dsp/project1) managed by Dr.Quinn. This document discusses the classification techniques supported by our software, the parameters necessary for instantiating them, and instructions on how to execute this package.

## Table of Contents 
1)	[Prerequisites](https://github.com/dsp-uga/team-alpine-p1/tree/develop#prerequisites)
2)	[Usage](https://github.com/dsp-uga/team-alpine-p1/tree/develop#usage)
3)	[Contributors](https://github.com/dsp-uga/team-alpine-p1/tree/develop#contributors)
4)	[License](https://github.com/dsp-uga/team-alpine-p1/tree/develop#license)

## Prerequisites 
1. Java 8 JDK: <br />
Make sure you have version 1.8.x <br /> 
To check, open the terminal and type: <br /> 
`java -version` <br />
If you don't have it installed, [download Java here](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) <br />

2. Scala: <br />
Make sure you have version 2.12.7 <br /> 
To check, open the terminal and type: <br /> 
`scala -version` <br /> 
If you don't have it installed, [download Scala here](https://www.scala-lang.org/download/) <br /> 

3. Spark: <br />
Make sure you have version 2.3.3 <br />
To check, open the terminal and type:<br />
`spark-submit --version` <br /> 
If you don't have it installed, [download Spark here](https://spark.apache.org/downloads.html)

4. Python: <br />
Make sure you have version 3.7.2 <br />
To check, open the terminal and type: <br />
`python --version` <br />
If you don't have it installed, [download Python here](https://www.python.org/downloads/)

5. [Google Data Storage](https://cloud.google.com/storage/)

6. [Google Cloud Platform](https://console.cloud.google.com/)

## Usage

### Team Alpine - Malware Classification Software

This program was built as a team project for the University of Georgia Data
Science Pragma course CSCI 8360 to address the Kaggel Microsoft Maleware 
Classification Problem. The problem involves building a classification model
using the training and testing data sets provided followed by evaluating their
performance on a final testing data set, for which we do not know the data.

In general, this process takes two steps:
    
    1) Read all infomration necessary for building and testing followed by
       storing the data in json files for future use
    2) Select one of the methodologies we support, specify what parameters
       values the methodology should use, and finally allow the process to 
       generate a text file containing category predictions for the test set
       supplied.

This software was built on many of the assumptions and data organization
rules incumbent to the assignment. It is important to first define json files 
containing all the data of interest. Once defined, you may apply different 
methodologies with different settings to evalue their performance.

In general, you execute this program using spark-submit command (look up more
information regarding Pyspark on the internet for installation and 
initalization):
    
    $ spark-submit team_alpine.py --operation <Operation Name> 
                                  <Operation Parameters ...>

The following sections discuss how to generate the json files followed by how
to execute the methodologies and which options we support.

### JSON Files

The project assignment came with two data sets:
    
    1) A small set of training and tests
    2) A large set of training and tests

The small data set is composed of the files

    X_small_train.txt, y_small_train.txt, X_small_test.txt, 
    and y_small_test.txt

The X-files list filename prefixes (to which you could add .bytes or .asm to
derive the true filename) along with Y-files that contain category index 
numbers. NOTE: The lines in each file correlate, signifying the nth row in 
an X-file signifyes a file that represents the category stored on the nth row
of the Y-file.

The large data set is composed of the files

    X_train.txt, y_train.txt, X_test.txt

Notice here that the Y-file was not defined for X_test.txt -- defining such 
values is the goal for this project.

When this project was built, these files were stored in the directory:
    
    gs://uga-dsp/project1/files

The other files referenced were stored in two different directories, depending
on which suffix you added to their names:
    
    1) .asm files in gs://uga-dsp/project1/data/asm
    2) .bytes files in gs://uga-dsp/project1/data/bytes

You could also find these files through URL links:
    
    1) .asm files at https://storage.googleapis.com/uga-dsp/project1/data/asm/
    2) .bytes files https://storage.googleapis.com/uga-dsp/project1/data/bytes/

* These data sources were initialized and managed by the course instructor. 

We start an introduction to this process under the assumption you will use the
same data sources we did, but we will show you later how you may define your
own source. You will need to define your own output directories and file names,
but, for simplicity, we will start by using some of the names we might have
used. Here's a basic call to read all the source files and build json files
containing their data (all in one line):
    
    $ spark-submit team_alpine.py
                   --operation build_malware_json 
                   --size_set all
                   --data_type all
                   --output_dir gs://dip-p1-storage/data/                   

Execution of this code would generate the following files in the directory
gs://dip-p1-storage/data/ :
    
    train_small_bytes.json
    test_small_bytes.json
    train_full_bytes.json
    test_full_bytes.json

These files in the directory gs://dip-p1-storage/data/ will be used when 
building and evaluating models in later steps. In general, the operation
"build_malware_json" takes the following parameters:
    
    --size_set {small, full, all}
    
    --data_type {bytes, asm, all}
    
    --output_dir {<path to your output directory>}
    
    --bytes_base_url {<path or url of directory containing bytes files>}
      (OPT - def.'https://storage.googleapis.com/uga-dsp/project1/data/bytes/')
      
    --asm_base_url {<path or url of directory containing asm files>}
      (OPT - def. 'https://storage.googleapis.com/uga-dsp/project1/data/asm/')
      
    --proj_file_dir {<path or url of directory containig set files>}
      (OPT - def. 'gs://uga-dsp/project1/files/')
      
    --small_x_train {<Name of small training file with file names>}
      (OPT - def. 'X_small_train.txt')
      
    --small_y_train {<Name of small training file with category ids>}
      (OPT - def. 'y_small_train.txt')
      
    --small_x_test {<Name of small test file with file names>}
      (OPT - def. 'X_small_test.txt')
      
    --small_y_test {<Name of small test file with category ids>}
      (OPT - def. 'y_small_test.txt')
      
    --full_x_train {<Name of large training file with file names>}
      (OPT - def. 'X_train.txt')
      
    --full_y_train {<Name of large training file with category ids>}
      (OPT - def. 'y_train.txt')
      
    --full_x_test {<Name of large test file with file names>}
      (OPT - def. 'X_test.txt')
      
    --repartition_count {<The number of repitions to split process into>}
      (OPT - def. 30)

Once you have created the small train/test json files and/or the full train/
test json files, you are ready to start passing that data to different 
classification methodologies to evaluate how well they work, see the following
sections.

### Merge ASM and Byte Files

### Classification Execution

In the time we had for this project, the Alpine Team put together different
approaches for predicting malware file catagories based on previous knoledge. 
The following sections discuss how to execute our software to generate 
predition files for later evaluation. As opposed to the data management 
discussed in the previous section, starting off a call to our pogram with 
(NOTICE!! - you will be expected to supply more command line parameters)

    $ spark-submit team_alpine.py
                   --operation build_classifier

will open up the options below. Again, this is just a start, read on...

### Naive Bayes

This approach has been around for quite some time, but despite its simplicity,
cases have shown it provides fairly reasonable predictions swiftly. Like many
other methodologies, people continue to find applying certain extentions and
modifications improve its general performance. Here, we mainly focused on 
evaluating IDE, word occurrence limitation, and N-Gram. Pyspark contains 
documents on these methods, and further details could be found on websites like
Wolfram Mathworld (http://mathworld.wolfram.com/BayesTheorem.html) and many 
others on these topics.

To start off, here is a basic example for how to execute the Naïve Bayes 
methodology on the data generated previously:

    $ spark-submit team_alpine.py
               --operation build_classifier
               --model nb
               --n_gram 1
               --use_idf True
               --smoothing_val 1
               --min_doc_freq 5
               --train_file gs://dip-p1-storage/data/train_small_bytes.json
               --test_file gs://dip-p1-storage/data/test_small_bytes.json
               --output_file gs://dip-p1-storage/data/small_bytes_predition.csv
                   
The command above would read in the data stored in the target 
train_small_bytes.json file to build a Naïve Bayes model using IDF, 
grams of size 1 (single byte in this case), smoothing value 1, and filter out 
all grams that occur less than 5 times. The program takes the resulting model 
and then sequentially applies it to the samples contained in the  test file. 
The results are then stored in the output file specified for later evaluation. 
In general, to apply the Naïve Bayes classification methodology to a target 
class set, you may consider the following parameters:

    --operation build_classifier
      (Required)

    --model nb
      (Required)

    --output_file <Target file to store output>
      (Required) 

    --train_file <Target json file with training data>
      (Opt. -def. gs://dip-p1-storage/data/train_full.json)

    --test_file <Target json file with testing data>
      (Opt. -def. gs://dip-p1-storage/data/test_full.json)

    --n_gram {1, 2, 3, 4}
      (Opt. -def. 1. Larger n_gram values incites slower performance) 

    --use_idf {True, False}
      (Opt. -def. True) 

    --smoothing_val {positive integer}
      (Opt. -def. 1)

    --min_doc_freq {positive integer}
      (Opt. -def. 3)

    --repartition {positive integer}
      (Opt. -def. 30, number of branches to brake a process into)
      
The resulting file will list category number predicted by the Naïve Bayes
classifier for the data defined in the test file. Further analysis of the 
results could be done through external programs.

### Logistic Regression
Here is a basic example for how to execute the logistic regression methodology on the data generated previously:

    $ spark-submit team_alpine.py
               --operation build_classifier     
               --model lr
               --n_gram 1 
               --use_idf True 
               --train_file gs://dip-p1-storage/data/train_small_bytes.json 
               --test_file gs://dip-p1-storage/data/test_small_bytes.json 
               --output_file gs://dip-p1-storage/data/small_bytes_predition.csv
               
### Random Forest
Here is a basic example for how to execute the randomForest methodology on the data generated previously:

      $ spark-submit team_alpine.py
               --operation build_classifier
               --model rf
               --n_gram 1
               --use_idf False
               --train_file gs://dip-p1-storage/data/train_small_bytes.json
               --test_file gs://dip-p1-storage/data/test_small_bytes.json
               --output_file gs://dip-p1-storage/data/small_bytes_predition.csv
            
## Contributors

See the contributors file for details. 

[Contributors](https://github.com/dsp-uga/team-alpine-p1/blob/master/Contributors.md)

## License
This project is licensed under the MIT License- see the [LICENSE.md](https://github.com/dsp-uga/team-alpine-p1/blob/master/LICENSE) file for details



