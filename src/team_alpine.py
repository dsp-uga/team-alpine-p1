#===================================================#
### Team Alpine - Malware Classification Software ###
#---------------------------------------------------#
#
# This program was built as a team project for the University of Georgia Data
# Science Pragma course CSCI 8360 to address the Kaggel Microsoft Maleware
# Classification Problem. The problem involves building a classification model
# using the training and testing data sets provided followed by evaluating their
# performance on a final testing data set, for which we do not know the data.
#
# In general, this process takes two steps:
#
#   1) Read all infomration necessary for building and testing followed by
#       storing the data in json files for future use
#    2) Select one of the methodologies we support, specify what parameters
#       values the methodology should use, and finally allow the process to
#       generate a text file containing category predictions for the test set
#       supplied.
#
# This software was built on many of the assumptions and data organization
# rules incumbent to the assignment. It is important to first define json files
# containing all the data of interest. Once defined, you may apply different
# methodologies with different settings to evalue their performance.
#
# In general, you execute this program using spark-submit command (look up more
# information regarding Pyspark on the internet for installation and
# initalization):
#
#    $ spark-submit team_alpine.py --operation <Operation Name>
#                                  <Operation Parameters ...>
#
#The following sections discuss how to generate the json files followed by how
#to execute the methodologies and which options we support.
#
#==============#
## JSON Files ##
#--------------#
#
# The project assignment came with two data sets:
#
#    1) A small set of training and tests
#    2) A large set of training and tests
#
# The small data set is composed of the files
#
#    X_small_train.txt, y_small_train.txt, X_small_test.txt,
#    and y_small_test.txt
#
# The X-files list filename prefixes (to which you could add .bytes or .asm to
# derive the true filename) along with Y-files that contain category index
# numbers. NOTE: The lines in each file correlate, signifying the nth row in
# an X-file signifyes a file that represents the category stored on the nth row
# of the Y-file.
#
# The large data set is composed of the files
#
#    X_train.txt, y_train.txt, X_test.txt
#
# Notice here that the Y-file was not defined for X_test.txt -- defining such
# values is the goal for this project.
#
# When this project was built, these files were stored in the directory:
#
#   gs://uga-dsp/project1/files
#
# The other files referenced were stored in two different directories, depending
# on which suffix you added to their names:
#
#    1) .asm files in gs://uga-dsp/project1/data/asm
#    2) .bytes files in gs://uga-dsp/project1/data/bytes
#
# You could also find these files through URL links:
#
#    1) .asm files at https://storage.googleapis.com/uga-dsp/project1/data/asm/
#    2) .bytes files at https://storage.googleapis.com/uga-dsp/project1/data/bytes/
#
# * These data sources were initialized and managed by the course instructor.
#
# We start an introduction to this process under the assumption you will use the
# same data sources we did, but we will show you later how you may define your
# own source. You will need to define your own output directories and file names,
# but, for simplicity, we will start by using some of the names we might have
# used. Here's a basic call to read all the source files and build json files
# containing their data (all in one line):
#
#    $ spark-submit team_alpine.py
#                   --operation build_malware_json
#                   --size_set all
#                   --data_type all
#                   --output_dir gs://dip-p1-storage/data/
#
# Execution of this code would generate the following files in the directory
# gs://dip-p1-storage/data/ :
#
#    train_small_bytes.json
#    test_small_bytes.json
#    train_full_bytes.json
#    test_full_bytes.json
#
# These files in the directory gs://dip-p1-storage/data/ will be used when
# building and evaluating models in later steps. In general, the operation
# "build_malware_json" takes the following parameters:
#
#    --size_set {small, full, all}
#
#    --data_type {bytes, asm, all}
#
#    --output_dir {<path to your output directory>}
#
#    --bytes_base_url {<path or url of directory containing bytes files>}
#      (OPT - def. 'https://storage.googleapis.com/uga-dsp/project1/data/bytes/')
#
#    --asm_base_url {<path or url of directory containing asm files>}
#      (OPT - def. 'https://storage.googleapis.com/uga-dsp/project1/data/asm/')
#
#    --proj_file_dir {<path or url of directory containig set files>}
#      (OPT - def. 'gs://uga-dsp/project1/files/')
#
#    --small_x_train {<Name of small training file with file names>}
#      (OPT - def. 'X_small_train.txt')
#
#    --small_y_train {<Name of small training file with category ids>}
#      (OPT - def. 'y_small_train.txt')
#
#    --small_x_test {<Name of small test file with file names>}
#      (OPT - def. 'X_small_test.txt')
#
#    --small_y_test {<Name of small test file with category ids>}
#      (OPT - def. 'y_small_test.txt')
#
#    --full_x_train {<Name of large training file with file names>}
#      (OPT - def. 'X_train.txt')
#
#    --full_y_train {<Name of large training file with category ids>}
#      (OPT - def. 'y_train.txt')
#
#    --full_x_test {<Name of large test file with file names>}
#      (OPT - def. 'X_test.txt')
#
#    --repartition_count {<The number of repitions to split process into>}
#      (OPT - def. 30)
#
# Once you have created the small train/test json files and/or the full train/
# test json files, you are ready to start passing that data to different
# classification methodologies to evaluate how well they work, see the following
# sections.
#
#==============================#
### Merge ASM and Byte Files ###
#------------------------------#
#
#
#==============================#
### Classification Execution ###
#------------------------------#
#
# In the time we had for this project, the Alpine Team put together different
# approaches for predicting malware file catagories based on previous knoledge.
# The following sections discuss how to execute our software to generate
# predition files for later evaluation. As opposed to the data management
# discussed in the previous section, starting off a call to our pogram with
# (NOTICE!! - you will be expected to supply more command line parameters)
#
#    $ spark-submit team_alpine.py
#                   --operation build_classifier
#
# will open up the options below. Again, this is just a start, read on...
#
#===============#
## Naive Bayes ##
#---------------#
#
# This approach has been around for quite some time, but despite its simplicity,
# cases have shown it provides fairly reasonable predictions swiftly. Like many
# other methodologies, people continue to find applying certain extentions and
# modifications improve its general performance. Here, we mainly focused on
# evaluating IDE, word occurrence limitation, and N-Gram. Pyspark contains
# documents on these methods, and further details could be found on websites like
# Wolfram Mathworld (http://mathworld.wolfram.com/BayesTheorem.html) and many
# others on these topics.
#
# To start off, here is a basic example for how to execute the Naïve Bayes
# methodology on the data generated previously:
#
#    $ spark-submit team_alpine.py
#                   --operation build_classifier
#                   --model nb
#                   --n_gram 1
#                   --use_idf True
#                   --smoothing_val 1
#                   --min_doc_freq 5
#                   --train_file gs://dip-p1-storage/data/train_small_bytes.json
#                   --test_file gs://dip-p1-storage/data/test_small_bytes.json
#                  --output_file gs://dip-p1-storage/data/small_bytes_predition.csv
#
# The command above would read in the data stored in the target
# train_small_bytes.json file to build a Naïve Bayes model using IDF,
# grams of size 1 (single byte in this case), smoothing value 1, and filter out
# all grams that occur less than 5 times. The program takes the resulting model
# and then sequentially applies it to the samples contained in the  test file.
# The results are then stored in the output file specified for later evaluation.
# In general, to apply the Naïve Bayes classification methodology to a target
# class set, you may consider the following parameters:
#
#    --operation build_classifier
#      (Required)
#
#    --model nb
#      (Required)
#
#    --output_file <Target file to store output>
#      (Required)
#
#    --train_file <Target json file with training data>
#      (Opt. -def. gs://dip-p1-storage/data/train_full.json)
#
#    --test_file <Target json file with testing data>
#      (Opt. -def. gs://dip-p1-storage/data/test_full.json)
#
#    --n_gram {1, 2, 3, 4}
#      (Opt. -def. 1. Larger n_gram values incites slower performance)
#
#    --use_idf {True, False}
#      (Opt. -def. True)
#
#    --smoothing_val {positive integer}
#      (Opt. -def. 1)
#
#    --min_doc_freq {positive integer}
#      (Opt. -def. 3)
#
#    --repartition {positive integer}
#      (Opt. -def. 30, number of branches to brake a process into)
#
# The resulting file will list category number predicted by the Naïve Bayes
# classifier for the data defined in the test file. Further analysis of the
# results could be done through external programs.
#============================================================================


import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, col, lit, asc
from pyspark.sql.types import IntegerType
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, LongType
from pyspark.sql.types import StructField, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, HashingTF, NGram, CountVectorizer, RegexTokenizer, PCA
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.classification import NaiveBayes, LogisticRegression, RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import monotonically_increasing_id, udf, lower
from pyspark.sql.functions import concat, col, lit
import requests


allowed_file_types = ('bytes','asm')
allowed_target_groups = ('small_train','small_test','full_train','full_test')
spark_active = None
full_mode = False


# Function to add text to a string
def add_bytes_text(s):
    return (s + '.bytes')


# Function to read byte file for each hash input and return the entire file
# as a single string
def text_bytes_get(fileName):
    resp = requests.get('https://storage.googleapis.com/uga-dsp/project1/data/bytes/' + fileName).text
    resp_filtered = ' '.join([w for w in resp.split() if len(w) < 3])
    return (resp_filtered)


# Function to add text to a string
def add_asm_text(s):
    return (s + '.asm')


# Function to read byte file for each hash input and return the entire file as
# a single string
def text_asm_get(fileName):
    resp = requests.get('https://storage.googleapis.com/uga-dsp/project1/data/asm/' + fileName).text
    lines = resp.splitlines()
    firsts = [line.split("\\s+")[0] for line in lines]
    first = [word if ":" not in word else word.split(':')[0] for word in firsts]
    varList = " ".join(first)
    return (varList)


# Decarling the functions as udf
add_bytes_text_udf = udf(add_bytes_text)
text_bytes_get_udf = udf(text_bytes_get)
add_asm_text_udf = udf(add_asm_text)
text_asm_get_udf = udf(text_asm_get)


def build_json(output_directory, target_group, file_type="bytes",
               bytes_base_url='https://storage.googleapis.com/uga-dsp/project1/data/bytes/',
               asm_base_url='https://storage.googleapis.com/uga-dsp/project1/data/asm/',
               proj_file_dir='gs://uga-dsp/project1/files/',
               small_x_train='X_small_train.txt',
               small_y_train='X_small_train.txt',
               small_x_test='X_small_test.txt',
               small_y_test='y_small_test.txt',
               full_x_train='X_train.txt',
               full_y_train='y_train.txt',
               full_x_test='X_test.txt',
               repartition_count=40):
    if (file_type not in allowed_file_types):
        raise ValueError("Only file_types 'bytes' and 'asm' are recognized")
    if (target_group not in allowed_target_groups):
        raise ValueError("Only target groups allowed are small_train, " + \
                         "small_test, full_train, and full_test - you passed" + \
                         " '" + target_group + "'")
    if (not full_mode):
        spark_active = SparkSession.builder.master("yarn").appName(
            "DSP P1- Train & Test set creation").getOrCreate()

    target_x_file = None
    target_y_file = None
    if (target_group == "small_train"):
        target_x_file = proj_file_dir + small_x_train
        target_y_file = proj_file_dir + small_y_train
    if (target_group == "small_test"):
        target_x_file = proj_file_dir + small_x_test
        target_y_file = proj_file_dir + small_y_test
    if (target_group == "full_train"):
        target_x_file = proj_file_dir + full_x_train
        target_y_file = proj_file_dir + full_y_train
    if (target_group == "full_test"):
        target_x_file = proj_file_dir + full_x_test

    if (target_x_file == None):
        print(
                    "Output: '" + output_directory + "', target_group: '" + target_group + "', file_type: '" + file_type + "'")
        raise ValueError("target_x_file was not initialized")

    # Read filenames
    files_list = spark_active.read.option("header", "false") \
        .csv(target_x_file) \
        .withColumn("row_id", monotonically_increasing_id())
    if (file_type == "bytes"):
        files_list = files_list.withColumn('filename',
                                           add_bytes_text_udf('_c0')).drop('_c0')
    if (file_type == "asm"):
        files_list = files_list.withColumn('filename',
                                           add_asm_text_udf('_c0')).drop('_c0')

    # Compensate for categories if category file is defined
    df_1 = files_list
    if (target_y_file != None):
        # Read categories
        cat_list = spark_active.read.option("header", "false") \
            .csv(target_y_file) \
            .withColumn("row_id", monotonically_increasing_id()) \
            .withColumnRenamed('_c0', 'category')

        df_1 = files_list.join(cat_list, 'row_id', how='left') \
            .repartition(repartition_count)

    # Read the text for target bytes or asm files
    final_df = df_1
    if (file_type == "bytes"):
        final_df = df_1.withColumn('text', text_bytes_get_udf("filename")) \
            .repartition(repartition_count)
    if (file_type == "asm"):
        final_df = df_1.withColumn('text', text_asm_get_udf("filename")) \
            .repartition(repartition_count)

    if (not output_directory.endswith("/")):
        output_directory = output_directory + "/"

    final_df.write.json(output_directory + target_group + "_" + file_type, mode='overwrite')

    if (not full_mode):
        spark_active.stop()


def build_all_json(output_directory, file_type,
                   bytes_base_url='https://storage.googleapis.com/uga-dsp/project1/data/bytes/',
                   asm_base_url='https://storage.googleapis.com/uga-dsp/project1/data/asm/',
                   proj_file_dir='gs://uga-dsp/project1/files/',
                   small_x_train='X_small_train.txt',
                   small_y_train='X_small_train.txt',
                   small_x_test='X_small_test.txt',
                   small_y_test='y_small_test.txt',
                   full_x_train='X_train.txt',
                   full_y_train='y_train.txt',
                   full_x_test='X_test.txt',
                   repartition_count=40):
    if (file_type not in allowed_file_types):
        raise ValueError("Only file_types 'bytes' and 'asm' are recognized")

    spark_active = SparkSession.builder.master("yarn").appName(
        "DSP P1- Train & Test set creation").getOrCreate()
    full_mode = True

    if (not output_directory.endswith("/")):
        output_directory = output_directory + "/"

    for group in allowed_target_groups:
        build_json(output_directory + group + file_type, group, file_type,
                   bytes_base_url,
                   asm_base_url,
                   proj_file_dir,
                   small_x_train,
                   small_y_train,
                   small_x_test,
                   small_y_test,
                   full_x_train,
                   full_y_train,
                   full_x_test,
                   repartition_count)

    full_mode = False
    spark_active.stop()


def merge_asm_bytes_json(train_bytes_file, test_bytes_file, train_asm_file, \
                         test_asm_file, output_directory, output_train_filename, \
                         output_test_filename, \
                         bytes_base_url='https://storage.googleapis.com/uga-dsp/project1/data/bytes/',
                         asm_base_url='https://storage.googleapis.com/uga-dsp/project1/data/asm/',
                         proj_file_dir='gs://uga-dsp/project1/files/',
                         small_x_train='X_small_train.txt',
                         small_y_train='X_small_train.txt',
                         small_x_test='X_small_test.txt',
                         small_y_test='y_small_test.txt',
                         full_x_train='X_train.txt',
                         full_y_train='y_train.txt',
                         full_x_test='X_test.txt',
                         repartition_count=40):
    spark_active = SparkSession.builder.master("yarn").appName(
        "DSP P1- Train & Test set creation").getOrCreate()

    # Reading Train Bytes and Asm files
    train_bytes = spark_active.read.json(train_bytes_file)
    test_bytes = spark_active.read.json(test_bytes_file)
    train_bytes = train_bytes.withColumnRenamed("bytes_text", train_bytes.text)
    test_bytes = train_bytes.withColumnRenamed("bytes_text", test_bytes.text)

    # Reading Test Bytes and Asm files
    train_asm = spark_active.read.json(train_asm_file)
    test_asm = spark_active.read.json(test_asm_file)
    train_bytes = train_bytes.withColumnRenamed("asm_text", train_bytes.text)
    test_bytes = train_bytes.withColumnRenamed("asm_text", test_bytes.text)

    # Joining Train and Test files respectively
    train_df = train_bytes.select("bytes_text", "row_id").join(train_asm, "row_id", how="left").select("row_id",
                                                                                                       "bytes_text",
                                                                                                       "asm_text",
                                                                                                       "category")
    test_df = test_bytes.select("bytes_text", "row_id").join(test_asm, "row_id", how="left").select("row_id",
                                                                                                    "bytes_text",
                                                                                                    "asm_text")

    # Concatinating bytestext and asmtext columns into a single column
    train_set = train_df.withColumn('text', lower(concat(col("bytes_text"), lit(" "), col("asm_text"))))
    test_set = test_df.withColumn('text', lower(concat(col("bytes_text"), lit(" "), col("asm_text"))))

    train_set.write.json(output_directory + output_train_filename, mode='overwrite')
    test_set.write.json(output_directory + output_test_filename, mode='overwrite')

    spark_active.stop()


def exec_naive_bayes(output_file, use_idf=True,
                     ngram_count=1,
                     repitions=30,
                     smoothing_val=1.0,
                     num_features=10000,
                     min_doc_freq=5,
                     train_file="gs://dip-p1-storage/data/train_full.json",
                     test_file="gs://dip-p1-storage/data/test_full.json"):
    # Setting up Spark
    spark = SparkSession.builder.master("yarn") \
        .appName("DSP P1- DataFeaturesModel").getOrCreate()

    # =======================#
    ### READ TARGET FILES ###
    # -----------------------#

    # Reading Train and Test sets along with cache'ing them
    print('Reading training data...')
    train_df = spark.read.json(train_file).withColumn(
        'text',
        regexp_replace(
            "text",
            '\w{3,20}\s|\\r\\n\w{3,20}',
            '')).withColumn(
        'label',
        col('category').cast(IntegerType())
    ).select(
        'row_id',
        'filename',
        'text',
        'label').repartition(repitions).cache()
    print('Completed reading training data...')
    print('==================================')
    print('Reading testing data...')
    test_df = spark.read.json(
        test_file).withColumn(
        'text',
        regexp_replace(
            "text",
            '\w{3,20}\s|\\r\\n\w{3,20}', '')
    ).select(
        'row_id',
        'filename',
        'text').repartition(repitions).cache()
    print('Completed reading testing data...')
    print('=================================')

    # ================================================#
    ### DYNAMICALLY DEFINE PIPELINE FOR PROCESSING ###
    # ------------------------------------------------#

    print('Fitting pipeline with regexTokenizer, N-Gram, HashingTF, IDF, PCA...')
    regexTokenizer = RegexTokenizer(inputCol="text",
                                    outputCol="words",
                                    pattern="\\w")
    ngram = NGram(n=ngram_count,
                  inputCol="words",
                  outputCol="nGramWords")
    if (use_idf == True):
        hashingTF = HashingTF(inputCol="nGramWords",
                              outputCol="rawFeatures",
                              numFeatures=num_features)
    else:
        hashingTF = HashingTF(inputCol="nGramWords",
                              outputCol="rawFeatures",
                              numFeatures=num_features)
    idf = IDF(inputCol="rawFeatures",
              outputCol="idfFeatures",
              minDocFreq=min_doc_freq)

    stages_list = [regexTokenizer]
    stages_list.append(ngram)
    stages_list.append(hashingTF)
    if (use_idf == True):
        stages_list.append(idf)
    pipeline = Pipeline(stages=stages_list)
    print('Completed fitting pipeline...')
    print('=============================')

    # Apply pipeline to the two sets
    pipeline_fit = pipeline.fit(train_df)
    train_dataset = pipeline_fit.transform(train_df)
    pipeline_fit = pipeline.fit(test_df)
    test_dataset = pipeline_fit.transform(test_df)

    # ==============================================#
    ### BUILD THE NAIVE BAYES MODEL AND APPLY IT ###
    # ----------------------------------------------#

    print('Fitting Naive Bayes Model with trainig data...')
    if (use_idf == True):
        nb = NaiveBayes(smoothing=smoothing_val,
                        modelType="multinomial",
                        featuresCol="idfFeatures")
        nb_model = nb.fit(train_dataset)
        print('Completed building the Naive Bayes Model...')
        print('===========================================')
        print('Applying Model to test data...')
        predictions = nb_model.transform(test_dataset)
        test_pred = predictions.select(
            'row_id', 'prediction').withColumn(
            'pred_label', col(
                'prediction').cast(
                IntegerType())
        ).drop('prediction').repartition(repitions)
        print('Completed prediction!')
        print('===========================================')

    else:
        nb = NaiveBayes(smoothing=smoothing_val,
                        modelType="multinomial",
                        featuresCol="rawFeatures")
        nb_model = nb.fit(train_dataset)
        print('Completed building the Naive Bayes Model...')
        print('===========================================')
        print('Applying Model to test data...')
        predictions = nb_model.transform(test_dataset)
        test_pred = predictions.select(
            'row_id', 'prediction').withColumn(
            'pred_label', col(
                'prediction').cast(
                IntegerType())
        ).drop('prediction').repartition(repitions)
        print('Completed prediction!')
        print('===========================================')

    test_pred.cache()
    print('Saving test predictions to file');
    test_pred.withColumn(
        'pred_label_corr', col('pred_label') + lit(1)).sort(
        asc('row_id')).select(
        'pred_label_corr').coalesce(1).write.format(
        'csv').mode(
        'overwrite').save(output_file)
    print('Prediction File Complete');
    print('========================');


def get_filename(n_gram_val, pca_val, cv_val, oversampling_val, base_output_directory):
    """
    Finds and returns the filename for the output file to be saved as, based on input parameters given by user
    :param n_gram_val: 1-gram, 2-gram, 3-gram
    :param pca_val: enabling or disabling dimensionality reduction using PCA
    :param cv_val: enabling or disabling cross-validation
    :param oversampling_val: enabling or disabling oversampling
    :return: filename of output file
    """
    n_gram_string = str(n_gram_val) + 'gram' if n_gram_val != 1 else ''
    pca_string = 'pca' if pca_val else ''
    cv_string = 'cv' if cv_val else ''
    oversampling_string = 'oversampled' if oversampling_val else ''
    filename = 'pip-regextoken_' + n_gram_string + '_hash_tf_idf_' \
               + pca_string + '_' + cv_string + '_' \
               + oversampling_string + '.txt'
    filesave = base_output_directory + filename
    return filesave


def log_reg(n_gram_val, pca_val, cv_val, oversampling_val, base_output_directory,
            min_doc_freq, file_repartition_count):
    """
    Executes logistic regression model for the training set, based on the input parameters given by the user
    and makes predictions for the test set
    :param n_gram_val: 1-gram, 2-gram, 3-gram
    :param pca_val: enabling or disabling dimensionality reduction using PCA
    :param cv_val: enabling or disabling cross-validation
    :param oversampling_val: enabling or disabling oversampling
    :return: writes predictions into file in a Google storage bucket
    """
    # Setting up Spark
    spark = SparkSession.builder.master("yarn") \
        .appName("DSP P1- Logistic Regression Model") \
        .getOrCreate()
    # Reading Train set and cache'ing it
    print('Reading training data...')
    train_df = spark.read.json(base_data_direcotry + "train_full.json") \
        .withColumn('label', col('category').cast(IntegerType())) \
        .select('row_id', 'filename', 'text', 'label') \
        .repartition(file_repartition_count)
    print('Completed reading training data...')
    print('==================================')
    # Reading Test set
    print('Reading testing data...')
    test_df = spark.read.json(base_data_direcotry + "/test_full.json") \
        .select('row_id', 'filename', 'text') \
        .repartition(file_repartition_count)
    print('Completed reading testing data...')
    print('=================================')
    if oversampling_val:
        # Enables oversampling of training set
        # Getting individual counts of documents for each label
        print('Oversampling training data to handle class imbalance...')
        category_count = train_df.groupBy(train_df.label).count()
        # Collecting label and it's count as key-value pairs in a dictionary in descending order
        count_dict = category_count.sort(category_count['count'].desc()) \
            .rdd.collectAsMap()
        # List of keys from count dictionary
        count_dict_keys = list(count_dict.keys())
        # Factor to check how many times to duplicate the data instances in a label
        duplication_factor = [int(2206 / count_dict[label]) for label in count_dict]
        # Creating an empty dataframe
        schema = StructType([StructField("row_id", StringType(), True),
                             StructField("filename", StringType(), True),
                             StructField("text", StringType(), True),
                             StructField("label", LongType(), True)])
        new_train_df = spark.createDataFrame([], schema)
        # Merging duplicated label sets into new_train_df
        for i in range(len(duplication_factor)):
            if duplication_factor[i] != 1:
                original_df = train_df.filter(train_df.label == count_dict_keys[i])
                partial_df = original_df
                for j in range(duplication_factor[i] - 1):
                    partial_df = partial_df.union(original_df)
                new_train_df = new_train_df.union(partial_df).repartition(10)
            else:
                original_df = train_df.filter(train_df.label == count_dict_keys[i])
                new_train_df = new_train_df.union(original_df).repartition(10)
        print('Completed oversampling training data...')
        print('=======================================')
    else:
        # Disables oversampling of training set
        new_train_df = train_df
    # Pipeline and creation of train_dataset and test_dataset
    regexTokenizer = RegexTokenizer(inputCol="text",
                                    outputCol="words",
                                    pattern="\\w")
    ngram = NGram(n=n_gram_val, inputCol="words", outputCol="ngram_words")
    hashingTF = HashingTF(inputCol="ngram_words",
                          outputCol="rawFeatures",
                          numFeatures=256)
    if pca_val:
        # Enabling Principal Component Analysis
        idf = IDF(inputCol="rawFeatures",
                  outputCol="idf_features",
                  minDocFreq=min_doc_freq)
        pca = PCA(k=20, inputCol="idf_features", outputCol="features")
        print('Fitting pipeline with regexTokenizer, N-Gram, HashingTF, IDF, PCA...')
        pipeline = Pipeline(stages=[regexTokenizer, ngram, hashingTF, idf, pca])
        print('Completed fitting pipeline...')
        print('=============================')
    else:
        # Disabling Principal Component Analysis
        idf = IDF(inputCol="rawFeatures",
                  outputCol="features",
                  minDocFreq=min_doc_freq)
        print('Fitting pipeline with regexTokenizer, N-Gram, HashingTF, IDF...')
        pipeline = Pipeline(stages=[regexTokenizer, ngram, hashingTF, idf])
        print('Completed fitting pipeline...')
        print('=============================')
    pipelineFit = pipeline.fit(new_train_df)
    train_dataset = pipelineFit.transform(new_train_df)
    test_dataset = pipelineFit.transform(test_df)
    lr = LogisticRegression(maxIter=10, regParam=0.3, family="multinomial")
    if cv_val:
        # Enabling cross-validation
        paramGrid = ParamGridBuilder() \
            .addGrid(hashingTF.numFeatures, [256]) \
            .addGrid(lr.regParam, [0.3]) \
            .build()
        crossval = CrossValidator(estimator=lr,
                                  estimatorParamMaps=paramGrid,
                                  evaluator=MulticlassClassificationEvaluator(),
                                  numFolds=5)
        print('Fitting cross-validation model using Logistic Regression estimator...')
        cvModel = crossval.fit(train_dataset)
        print('Completed cross-validation using Logistic Regression estimator...')
        print('=================================================================')
        predictions = cvModel.transform(test_dataset)
    else:
        # Disabling cross-validation
        print('Fitting Logistic Regression model on the training data...')
        lrModel = lr.fit(train_dataset)
        print('Completed fitting Logistic Regression model...')
        print('==============================================')
        predictions = lrModel.transform(test_dataset)
    # Making predictions for test set
    print('Getting predictions for test set...')
    test_pred = predictions.select('row_id', 'prediction') \
        .withColumn('pred_label', col('prediction').cast(IntegerType())) \
        .drop('prediction')
    test_pred.cache()
    print('Completed predictions for test set...')
    print('=====================================')
    # Writing predictions into output file
    print('Writing predictions into output file...')
    test_pred.sort(asc('row_id')) \
        .select('pred_label').coalesce(1) \
        .write.format('csv') \
        .mode('overwrite') \
        .save(get_filename(n_gram_val, pca_val, cv_val, oversampling_val, base_output_directory))
    print('Completed writing predictions into output file...')
    print('=================================================')
    print('Logistic Regression Model completed.')


def get_filename_rf(pca_val, base_output_directory):
    """
    Finds and returns the filename for the output file to be saved as, based on input parameters given by user
    :param pca_val: enabling or disabling dimensionality reduction using PCA
    :param base_output_directory: Directory or URL path to store the generated output files
    :return: filename of output file
    """
    n_gram_string = str(n_gram_val) + 'gram' if n_gram_val != 1 else ''
    pca_string = 'pca' if pca_val else ''
    cv_string = 'cv' if cv_val else ''
    oversampling_string = 'oversampled' if oversampling_val else ''
    filename = 'pip-regextoken_' + n_gram_string + '_hash_tf_idf_' \
               + pca_string + '_' + cv_string + '_' \
               + oversampling_string + '.txt'
    filesave = base_output_directory + filename
    return filesave


def rand_forest(pca_val, base_output_directory, file_repartition_count):
    """
    Executes logistic regression model for the training set, based on the input parameters given by the user
    and makes predictions for the test set
    :param pca_val: enabling or disabling dimensionality reduction using PCA
    :param base_output_directory: Directory or URL path to store the generated output files
    :param file_repartition_count: Repartition count
    :return: writes predictions into file in a Google storage bucket
    """
    # Setting up Spark
    spark = SparkSession.builder.master("yarn") \
        .appName("DSP P1- Logistic Regression Model") \
        .getOrCreate()
    # Reading Train set and cache'ing it
    train_df = spark.read.json(base_data_direcotry + "train_full.json") \
        .withColumn('label', col('category').cast(IntegerType())) \
        .select('row_id', 'filename', 'text', 'label') \
        .repartition(file_repartition_count)
    # Reading Test set
    test_df = spark.read.json(base_data_direcotry + "/test_full.json") \
        .select('row_id', 'filename', 'text') \
        .repartition(file_repartition_count)
    # Pipeline and creation of train_dataset and test_dataset
    regexTokenizer = RegexTokenizer(inputCol="text",
                                    outputCol="words",
                                    pattern="\\w")
    countVectorizer = CountVectorizer(inputCol="words",
									  outputCol="rawFeatures")
    if pca_val:
        # Enabling Principal Component Analysis
        pca = PCA(k=20, inputCol="idf_features", outputCol="features")
        pipeline = Pipeline(stages=[regexTokenizer,countVectorizer, pca])
    else:
        # Disabling Principal Component Analysis
        pipeline = Pipeline(stages=[regexTokenizer,countVectorizer])
    pipelineFit = pipeline.fit(train_df)
    train_dataset = pipelineFit.transform(train_df)
    test_dataset = pipelineFit.transform(test_df)
    #Random Forest Classifier
    rf = RandomForestClassifier(labelCol="label", seed=42, maxDepth=30, numTrees=50)
    rfModel = rf.fit(train_dataset)
    predictions = rfModel.transform(test_dataset)
    # Making predictions for test set
    test_pred = predictions.select('row_id', 'prediction') \
        .withColumn('pred_label', col('prediction').cast(IntegerType())) \
        .drop('prediction')
    test_pred.cache()
    # Writing predictions into output file
    test_pred.sort(asc('row_id')) \
        .select('pred_label').coalesce(1) \
        .write.format('csv') \
        .mode('overwrite') \
        .save(get_filename_rf(pca_val, base_output_directory))



# Start by determining the general mode: build_malware_data or build_classifier
def main():
    base_parser = argparse.ArgumentParser(description="Operation Parameters:")
    base_parser.add_argument('--operation', 
                             dest='operation',
                             choices=['build_malware_json','build_classifier'], 
                             help='Chose to either "build_malware_json" or ' 
                                 + '"build_classifier". '
                                 + 'Start by building json data'
                                 + ' files before applying classifier models', 
                             required=True);
    
    ## The following are place holders for values that might be used later
    base_parser.add_argument(
            '--size_set',dest='size_set',required=False);
    base_parser.add_argument(
            '--data_type',dest='data_type',required=False);
    base_parser.add_argument(
            '--output_dir',dest='output_dir',required=False);
    base_parser.add_argument(
            '--byte_train_file',dest='byte_train_file',required=False);
    base_parser.add_argument(
            '--byte_test_file',dest='byte_test_file',required=False);
    base_parser.add_argument(
            '--asm_train_file',dest='asm_train_file',required=False);
    base_parser.add_argument(
            '--asm_test_file',dest='asm_test_file',required=False);
    base_parser.add_argument(
            '--merge_train_outfile',dest='asm_test_file',required=False);
    base_parser.add_argument(
            '--merge_test_outfile',dest='asm_test_file',required=False);
    base_parser.add_argument(
            '--bytes_base_url',dest='bytes_base_url',required=False);
    base_parser.add_argument(
            '--asm_base_url',dest='asm_base_url',required=False);
    base_parser.add_argument(
            '--proj_file_dir',dest='proj_file_dir',required=False);
    base_parser.add_argument(
            '--small_x_train',dest='small_x_train',required=False);
    base_parser.add_argument(
            '--small_y_train',dest='small_y_train',required=False);
    base_parser.add_argument(
            '--small_x_test',dest='small_x_test',required=False);
    base_parser.add_argument(
            '--small_y_test',dest='small_y_test',required=False);
    base_parser.add_argument(
            '--full_x_train',dest='full_x_train',required=False);
    base_parser.add_argument(
            '--full_y_train',dest='full_y_train',required=False);
    base_parser.add_argument(
            '--full_x_test',dest='full_x_test',required=False);
    base_parser.add_argument(
            '--train_file',dest='train_file',required=False);
    base_parser.add_argument(
            '--test_file',dest='test_file',required=False);
    base_parser.add_argument(
            '--repartition_count',dest='repartition_count',required=False);
    base_parser.add_argument(
            '--model',dest='model',required=False);
    base_parser.add_argument(
            '--n_gram',dest='n_gram',required=False);
    base_parser.add_argument(
            '--pca',dest='pca',required=False);
    base_parser.add_argument(
            '--min_doc_freq',dest='min_doc_freq',required=False);
    base_parser.add_argument(
            '--cv',dest='cv',required=False);
    base_parser.add_argument(
            '--oversampling',dest='oversampling',required=False);
    base_parser.add_argument(
            '--use_asm',dest='use_asm',required=False);
    base_parser.add_argument(
            '--output_file',dest='output_file',required=False);
    
    base_args = base_parser.parse_args()
    
    
    if(base_args.operation == "build_malware_json"):
        json_parser = argparse.ArgumentParser(description="Malware Json " \
                                              + "Parameters:")
        json_parser.add_argument('--operation', 
                                 dest='operation',
                                 choices=['build_malware_json',
                                          'build_classifier'], 
                                 help='Chose to either "build_malware_json" or' 
                                 + ' "build_classifier". Start by '
                                 + ' building json data'
                                 + ' files before applying classifier models', 
                                 required=True);
        json_parser.add_argument('--size_set',
                                 dest='size_set', 
                                 choices=['small_train','small_test',
                                          'full_train','full_test','all'],
                                 required=True,
                                 help='Select "small-train", "small-test", ' + 
                                 '"full-train", "full-test", ' +
                                 'or "all" for both');
        json_parser.add_argument('--data_type',
                                 dest='data_type', 
                                 choices=['bytes','asm','all'],
                                 required=True,
                                 help='Select "byes" for only bytes data, ' +
                                 '"asm" for only asm data, or "all" for both');
        json_parser.add_argument('--output_dir',
                                 dest='output_dir', 
                                 required=True,
                                 help='Directory or URL path to '
                                 + 'store json files '+
                                 'generated');
        json_parser.add_argument('--bytes_base_url',
                                 dest='bytes_base_url', 
                                 required=False,
                                 default='https://storage.googleapis.com/' +
                                 'uga-dsp/project1/data/bytes/',
                                 help='path or url of directory '
                                 +'containing bytes '+
                                 'files');
        json_parser.add_argument('--asm_base_url',
                                 dest='asm_base_url', 
                                 required=False,
                                 default='https://storage.googleapis.com/' +
                                 'uga-dsp/project1/data/asm/',
                                 help='path or url of directory ' +
                                 'containing asm files');
        json_parser.add_argument('--proj_file_dir',
                                 dest='proj_file_dir', 
                                 required=False,
                                 default='gs://uga-dsp/project1/files/',
                                 help='path or url of directory containig set'
                                 + ' files');
        json_parser.add_argument('--small_x_train',
                                 dest='small_x_train', 
                                 required=False,
                                 default='X_small_train.txt',
                                 help='Name of small training file containing'
                                 + ' target file' +
                                 ' names');
        json_parser.add_argument('--small_y_train',
                                 dest='small_y_train', 
                                 required=False,
                                 default='y_small_train.txt',
                                 help='Name of small training file containing' 
                                 + ' target labels');
        json_parser.add_argument('--small_x_test',
                                 dest='small_x_test', 
                                 required=False,
                                 default='X_small_test.txt',
                                 help='Name of small testing file containing' 
                                 + ' target file' +
                                 ' names');
        json_parser.add_argument('--small_y_test',
                                 dest='small_y_test', 
                                 required=False,
                                 default='y_small_test.txt',
                                 help='Name of small testing file containing' 
                                 + ' target labels');
        json_parser.add_argument('--full_x_train',
                                 dest='full_x_train', 
                                 required=False,
                                 default='X_train.txt',
                                 help='Name of large training file ' + 
                                 'with target file names');
        json_parser.add_argument('--full_y_train',
                                 dest='full_y_train', 
                                 required=False,
                                 default='y_train.txt',
                                 help='Name of large training file ' + 
                                 'with lables');
        json_parser.add_argument('--full_x_test',
                                 dest='full_x_test', 
                                 required=False,
                                 default='X_test.txt',
                                 help='Name of large test file ' + 
                                 'with target file names');
        json_parser.add_argument('--repartition_count',
                                 dest='repartition_count', 
                                 type=int,
                                 required=False,
                                 default='30',
                                 help='The number of repitions to ' + 
                                 'split processes into');
        args = json_parser.parse_args()
        
        if( args.size_set == "all" ):
            if( args.data_type == "all" or args.data_type == "bytes" ):
                build_all_json(
                        args.output_dir,"bytes",
                        bytes_base_url = args.bytes_base_url,
                        asm_base_url = args.asm_base_url,
                        proj_file_dir = args.proj_file_dir,
                        small_x_train = args.small_x_train,
                        small_y_train = args.small_y_train,
                        small_x_test = args.small_x_test,
                        small_y_test = args.small_y_test,
                        full_x_train = args.full_x_train,
                        full_y_train = args.full_y_train,
                        full_x_test = args.full_x_test,
                        repartition_count = args.repartition_count)
            if( args.data_type == "all" or args.data_type == "asm" ):
                build_all_json(
                        args.output_dir,"asm",
                        bytes_base_url = args.bytes_base_url,
                        asm_base_url = args.asm_base_url,
                        proj_file_dir = args.proj_file_dir,
                        small_x_train = args.small_x_train,
                        small_y_train = args.small_y_train,
                        small_x_test = args.small_x_test,
                        small_y_test = args.small_y_test,
                        full_x_train = args.full_x_train,
                        full_y_train = args.full_y_train,
                        full_x_test = args.full_x_test,
                        repartition_count = args.repartition_count)
        else:
            if( args.data_type == "all" or args.data_type == "bytes" ):
                build_json(
                        args.output_dir,args.size_set,"bytes",
                        bytes_base_url = args.bytes_base_url,
                        asm_base_url = args.asm_base_url,
                        proj_file_dir = args.proj_file_dir,
                        small_x_train = args.small_x_train,
                        small_y_train = args.small_y_train,
                        small_x_test = args.small_x_test,
                        small_y_test = args.small_y_test,
                        full_x_train = args.full_x_train,
                        full_y_train = args.full_y_train,
                        full_x_test = args.full_x_test,
                        repartition_count = args.repartition_count)
            if( args.data_type == "all" or args.data_type == "asm" ):
                build_json(
                        args.output_dir,args.size_set,"asm",
                        bytes_base_url = args.bytes_base_url,
                        asm_base_url = args.asm_base_url,
                        proj_file_dir = args.proj_file_dir,
                        small_x_train = args.small_x_train,
                        small_y_train = args.small_y_train,
                        small_x_test = args.small_x_test,
                        small_y_test = args.small_y_test,
                        full_x_train = args.full_x_train,
                         full_y_train = args.full_y_train,
                        full_x_test = args.full_x_test,
                        repartition_count = args.repartition_count)
    
    elif(base_args.operation == "merge_malware_json"):
        merge_parser = argparse.ArgumentParser(description="Merge "
                                               + "Malware Json:")
        merge_parser.add_argument('--operation', 
                             dest='operation',
                             choices=['build_malware_json','build_classifier'], 
                             help='Chose to either "build_malware_json" or ' 
                             + '"build_classifier". Start by '
                             + 'building json data'
                             + ' files before applying classifier models', 
                             required=True);
        merge_parser.add_argument('--output_dir',
                                 dest='output_dir',
                                 help='Direcotry that will store merged files',
                                 required=True);
        merge_parser.add_argument('--byte_train_file',
                                 dest='byte_train_file',
                                 required=True);
        merge_parser.add_argument('--byte_test_file',
                                 dest='byte_test_file',
                                 required=True);
        merge_parser.add_argument('--asm_train_file',
                                 dest='asm_train_file',
                                 required=True);
        merge_parser.add_argument('--asm_test_file',
                                 dest='asm_test_file',
                                 required=True);
        merge_parser.add_argument('--merge_train_outfile',
                                 dest='asm_test_file',
                                 required=True);
        merge_parser.add_argument('--merge_test_outfile',
                                 dest='asm_test_file',
                                 required=True);
        merge_args = merge_parser.parse_args()
        merge_asm_bytes_json(merge_args.byte_train_file,
                                             merge_args.byte_test_file,
                                             merge_args.asm_train_file, 
                                             merge_args.asm_test_file, 
                                             merge_args.output_dir, 
                                             merge_args.merge_train_outfile,
                                             merge_args.merge_test_outfile)
    
    if(base_args.operation == "build_classifier"):
        # Determine which class was selected for use
        class_parser = argparse.ArgumentParser(
                description='Model Parameters:')
        class_parser.add_argument('--operation', 
                         dest='operation',
                         choices=['build_malware_json','build_classifier'], 
                         help='Chose to either "build_malware_json" or ' 
                             + '"build_classifier". Start '
                             + 'by building json data'
                             + ' files before applying classifier models', 
                         required=True);
        class_parser.add_argument('--model', dest='model', default='rf', 
                            choices=['nb', 'lr', 'rf'],
                            help='machine learning model to be used')
        class_parser.add_argument(
                '--size_set',dest='size_set',required=False);
        class_parser.add_argument(
                '--data_type',dest='data_type',required=False);
        class_parser.add_argument(
                '--output_dir',dest='output_dir',required=False);
        class_parser.add_argument(
                '--byte_train_file',dest='byte_train_file',required=False);
        class_parser.add_argument(
                '--byte_test_file',dest='byte_test_file',required=False);
        class_parser.add_argument(
                '--asm_train_file',dest='asm_train_file',required=False);
        class_parser.add_argument(
                '--asm_test_file',dest='asm_test_file',required=False);
        class_parser.add_argument(
                '--merge_train_outfile',dest='asm_test_file',required=False);
        class_parser.add_argument(
                '--merge_test_outfile',dest='asm_test_file',required=False);
        class_parser.add_argument(
                '--bytes_base_url',dest='bytes_base_url',required=False);
        class_parser.add_argument(
                '--asm_base_url',dest='asm_base_url',required=False);
        class_parser.add_argument(
                '--proj_file_dir',dest='proj_file_dir',required=False);
        class_parser.add_argument(
                '--small_x_train',dest='small_x_train',required=False);
        class_parser.add_argument(
                '--small_y_train',dest='small_y_train',required=False);
        class_parser.add_argument(
                '--small_x_test',dest='small_x_test',required=False);
        class_parser.add_argument(
                '--small_y_test',dest='small_y_test',required=False);
        class_parser.add_argument(
                '--full_x_train',dest='full_x_train',required=False);
        class_parser.add_argument(
                '--full_y_train',dest='full_y_train',required=False);
        class_parser.add_argument(
                '--full_x_test',dest='full_x_test',required=False);
        class_parser.add_argument(
                '--train_file',dest='train_file',required=False);
        class_parser.add_argument(
                '--test_file',dest='test_file',required=False);
        class_parser.add_argument(
                '--repartition_count',dest='repartition_count',required=False);
        class_parser.add_argument(
                '--n_gram',dest='n_gram',required=False);
        class_parser.add_argument(
                '--pca',dest='pca',required=False);
        class_parser.add_argument(
                '--min_doc_freq',dest='min_doc_freq',required=False);
        class_parser.add_argument(
                '--cv',dest='cv',required=False);
        class_parser.add_argument(
                '--oversampling',dest='oversampling',required=False);
        class_parser.add_argument(
                '--use_asm',dest='use_asm',required=False);
        class_parser.add_argument(
                '--output_file',dest='output_file',required=False);
            
        class_args = class_parser.parse_args()
        if(class_args.model == "nb"):
            # User selected Naive Bayes. Look for all arguments 
            # recognized by Naive Bayes
            nb_parser = argparse.ArgumentParser(description='NB Parameters:')
            nb_parser.add_argument('--operation', 
                                   dest='operation',
                                   choices=['build_malware_json',
                                            'build_classifier'], 
                                   help='Chose to either ' + 
                                   '"build_malware_json" or ' 
                                       + '"build_classifier". ' 
                                       + 'Start by building json data'
                                       + ' files before applying ' + 
                                       'classifier models', 
                                   required=True);
            nb_parser.add_argument('--model', dest='model', default='rf', 
                                   choices=['nb', 'lr', 'rf'],
                                   help='machine learning model to be used')
            nb_parser.add_argument('--n_gram', dest='n_gram_value', type=int, 
                                   default=1, choices=[1, 2, 3, 4],
                                   help='value of n-gram to be ' + 
                                   'applied to features')
            nb_parser.add_argument('--min_doc_freq', dest='min_doc_freq'
                                   , type=int, 
                                   default=5, 
                                   help='Minimum number of ' + 
                                   'times a word should " \
                                   + "appear to be accounted for')
            nb_parser.add_argument('--repartition_count',
                                   dest='repartition_count', 
                                   type=int,
                                   required=False,
                                   default='30',
                                   help='The number of repitions to ' + 
                                   'split processes into')
            nb_parser.add_argument('--use_idf', dest='use_idf', 
                                   default=True, type=bool, 
                                   choices=[True, False],
                                   help='use assembly files with '
                                   + 'byte files as features')
            nb_parser.add_argument('--train_file', dest='use_idm', 
                                   required=True,
                                   help='Target json file used for training')
            nb_parser.add_argument('--test_file', dest='test_file',
                                   required=True,
                                   help='Target json file used for testing')
            
            nb_parser.add_argument('--output_file',dest='output_file',
                                   required=False)
    
            nb_args = nb_parser.parse_args()
            exec_naive_bayes(nb_args.output_file,
                                              nb_args.use_idf,
                                              nb_args.n_gram_value,
                                              nb_args.repartition_count,
                                              1.0,
                                              10000,
                                              nb_args.min_doc_freq,
                                              nb_args.train_file,
                                              nb_args.test_file
                                              )
            
        if(class_args.model == 'lr'):
        
            parser = argparse.ArgumentParser(description='Model Parameters:')
            parser.add_argument('--operation', 
                             dest='operation',
                             choices=['build_malware_json','build_classifier'], 
                             help='Chose to either "build_malware_json" or ' 
                                 + '"build_classifier". '
                                 + 'Start by building json data'
                                 + ' files before applying classifier models', 
                             required=True);
            parser.add_argument('--model', dest='model', default='rf', 
                                choices=['nb', 'lr', 'rf'],
                                help='machine learning model to be used')
            parser.add_argument('--n_gram', dest='n_gram_value', type=int, 
                                default=1, choices=[1, 2, 3, 4],
                                help='value of n-gram to be '
                                + 'applied to features')
            parser.add_argument('--pca', dest='pca_value', 
                                type=bool, default=False, 
                                choices=[True, False],
                                help='enable/disable ' +
                                'dimensionality reduction using ' + 
                                'Principal Component Analysis')
            parser.add_argument('--cv', dest='cv_value', 
                                type=bool, default=False, 
                                choices=[True, False],
                                help='enable/disable 5-fold cross-validation')
            parser.add_argument('--oversampling', dest='oversampling_val', 
                                default=False, 
                                choices=[True, False], type=bool,
                                help='enable/disable oversampling')
            parser.add_argument('--output_dir',
                                dest='output_dir', 
                                required=True,
                                help='Directory or URL path to '
                                + 'store output files '+
                                'generated')
            parser.add_argument('--min_doc_freq', dest='min_doc_freq'
                                , type=int, 
                                default=5, 
                                help='Minimum number of ' + 
                                'times a word should " \
                                + "appear to be accounted for')
            parser.add_argument('--repartition_count',
                                dest='repartition_count', 
                                type=int,
                                required=False,
                                default='30',
                                help='The number of repitions to ' + 
                                'split processes into')
            
            
    
            args = parser.parse_args()
   
            log_reg(args.n_gram_value, args.pca_value, args.cv_value, 
                    args.oversampling_val, args.base_output_directory, 
                    args.min_doc_freq, args.repartition_count)
            
        if(class_args.model == 'rf'):
        
            parser = argparse.ArgumentParser(description='Model Parameters:')
            parser.add_argument('--operation', 
                             dest='operation',
                             choices=['build_malware_json','build_classifier'], 
                             help='Chose to either "build_malware_json" or ' 
                                 + '"build_classifier". Start '
                                 + 'by building json data'
                                 + ' files before applying '
                                 + 'classifier models', 
                             required=True);
            parser.add_argument('--model', dest='model', default='rf', 
                                choices=['nb', 'lr', 'rf'],
                                help='machine learning model to be used')
            parser.add_argument('--pca', dest='pca_value', 
                                type=bool, default=False, 
                                choices=[True, False],
                                help='enable/disable '
                                + 'dimensionality reduction using ' + 
                                'Principal Component Analysis')
            parser.add_argument('--output_dir',
                                dest='output_dir', 
                                required=True,
                                help='Directory or URL path to '
                                + 'store output files '+
                                'generated')
            parser.add_argument('--repartition_count',
                                dest='repartition_count', 
                                type=int,
                                required=False,
                                default='30',
                                help='The number of repitions to ' + 
                                'split processes into')
            
    
            args = parser.parse_args()
   
            rand_forest(args.pca_value,
                    args.base_output_directory, 
                    args.repartition_count)
            
            
if __name__ == "__main__":
    main()
