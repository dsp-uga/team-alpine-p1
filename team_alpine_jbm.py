import argparse
from src.models.logistic_regression import log_reg

"""
#===================================================#
### Team Alpine - Malware Classification Software ###
#---------------------------------------------------#

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

#==============#
## JSON Files ##
#--------------#

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
    2) .bytes files at https://storage.googleapis.com/uga-dsp/project1/data/bytes/

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
      (OPT - def. 'https://storage.googleapis.com/uga-dsp/project1/data/bytes/')
      
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


#==============================#
### Classification Execution ###
#------------------------------#

In the time we had for this project, the Alpine Team put together different
approaches for predicting malware file catagories based on previous knoledge. 
The following sections discuss how to execute our software to generate 
predition files for later evaluation. As opposed to the data management 
discussed in the previous section, starting off a call to our pogram with 
(NOTICE!! - you will be expected to supply more command line parameters)

    $ spark-submit team_alpine.py
                   --operation build_classifier

will open up the options below. Again, this is just a start, read on...

#===============#
## Naive Bayes ##
#---------------#

This approach has been around for quite some time, but despite its simplicity,
cases have shown it provides fairly reasonable predictions swiftly. Like many
other methodologies, people continue to find applying certain extentions and
modifications improve its general performance. Here, we mainly focused on 
evaluating IDE, word occurrence limitation, and N-Gram. Pyspark contains 
documents on these methods, and further details could be found on websites like
Wolfram Mathworld (http://mathworld.wolfram.com/BayesTheorem.html) and many 
others on these topics.

Once you have 






    
"""

# Start by determining the general mode: build_malware_data or build_classifier

base_parser = argparse.ArgumentParser(description="Operation Parameters:")
base_parser.add_argument('--operation', 
                         dest='operation',
                         choices=['build_malware_json','build_classifier'], 
                         help='Chose to either "build_malware_json" or ' 
                             + '"build_classifier". Start by building json data'
                             + ' files before applying classifier models', 
                         required=True);
base_parser.add_argument('--size_set',
                         dest='size_set',
                         required=False);
base_parser.add_argument('--data_type',
                         dest='data_type',
                         required=False);
base_parser.add_argument('--output_dir',
                         dest='output_dir', 
                         required=False);

base_args = base_parser.parse_args()

if(base_args.operation == "build_malware_json"):
    json_parser = argparse.ArgumentParser(description="Malware Json Parameters:")
    json_parser.add_argument('--operation', 
                             dest='operation',
                             choices=['build_malware_json','build_classifier'], 
                             help='Chose to either "build_malware_json" or ' 
                             + '"build_classifier". Start by building json data'
                             + ' files before applying classifier models', 
                             required=True);
    json_parser.add_argument('--size_set',
                             dest='size_set', 
                             choices=['small','full','all'],
                             required=True,
                             help='Select "small" for only small set, ' +
                             '"large" for only large set, or "all" for both');
    json_parser.add_argument('--data_type',
                             dest='data_type', 
                             choices=['bytes','asm','all'],
                             required=True,
                             help='Select "byes" for only bytes data, ' +
                             '"asm" for only asm data, or "all" for both');
    json_parser.add_argument('--output_dir',
                             dest='output_dir', 
                             required=True,
                             help='Directory or URL path to store json files '+
                             'generated');
    json_parser.add_argument('--bytes_base_url',
                             dest='bytes_base_url', 
                             required=False,
                             default='https://storage.googleapis.com/uga-dsp/project1/data/bytes/',
                             help='path or url of directory containing bytes '+
                             'files');
    json_parser.add_argument('--asm_base_url',
                             dest='asm_base_url', 
                             required=False,
                             default='gs://uga-dsp/project1/files/',
                             help='path or url of directory containing asm files');
    json_parser.add_argument('--proj_file_dir',
                             dest='proj_file_dir', 
                             required=False,
                             default='https://storage.googleapis.com/uga-dsp/project1/data/asm/',
                             help='path or url of directory containig set files');
    json_parser.add_argument('--small_x_train',
                             dest='small_x_train', 
                             required=False,
                             default='X_small_train.txt',
                             help='Name of small training file with file names');
    json_parser.add_argument('--small_y_train',
                             dest='small_y_train', 
                             required=False,
                             default='y_small_train.txt',
                             help='Name of small training file with category id');
    json_parser.add_argument('--small_x_test',
                             dest='small_x_test', 
                             required=False,
                             default='X_small_test.txt',
                             help='Name of small test file with file names');
    json_parser.add_argument('--small_y_test',
                             dest='small_y_test', 
                             required=False,
                             default='ysmall_test.txt',
                             help='Name of small test file with category ids');
    json_parser.add_argument('--full_x_train',
                             dest='full_x_train', 
                             required=False,
                             default='X_train.txt',
                             help='Name of large training file with file names');
    json_parser.add_argument('--full_y_train',
                             dest='full_y_train', 
                             required=False,
                             default='y_train.txt',
                             help='Name of large training file with category ids');
    json_parser.add_argument('--full_x_test',
                             dest='full_x_test', 
                             required=False,
                             default='X_test.txt',
                             help='Name of large test file with file names');
    json_parser.add_argument('--repartition_count',
                             dest='repartition_count', 
                             type=int,
                             required=False,
                             default='30',
                             help='The number of repitions to split processes into');
    args = json_parser.parse_args()
    print(args.operation)
    

elif(base_args.operation == "build_classifier"):                      
    parser = argparse.ArgumentParser(description='Model Parameters:')
    parser.add_argument('--operation', 
                     dest='operation',
                     choices=['build_malware_json','build_classifier'], 
                     help='Chose to either "build_malware_json" or ' 
                         + '"build_classifier". Start by building json data'
                         + ' files before applying classifier models', 
                     required=True);
    parser.add_argument('--model', dest='model', default='rf', 
                        choices=['nb', 'lr', 'rf'],
                        help='machine learning model to be used')
    parser.add_argument('--n_gram', dest='n_gram_value', type=int, 
                        default=1, choices=[1, 2, 3, 4],
                        help='value of n-gram to be applied to features')
    parser.add_argument('--pca', dest='pca_value', type=bool, default=False, 
                        choices=[True, False],
                        help='enable/disable dimensionality reduction using ' + 
                        'Principal Component Analysis')
    parser.add_argument('--cv', dest='cv_value', type=bool, default=False, 
                        choices=[True, False],
                        help='enable/disable 5-fold cross-validation')
    parser.add_argument('--oversampling', dest='oversampling_val', 
                        default=False, choices=[True, False], type=bool,
                        help='enable/disable oversampling')
    parser.add_argument('--use-asm', dest='asm', default=True, type=bool, 
                        choices=[True, False],
                        help='use assembly files with byte files as features')

    
    args = parser.parse_args()
    print(args.operation)


