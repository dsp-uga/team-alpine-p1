from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, col, lit, asc
from pyspark.sql.types import IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, HashingTF, RegexTokenizer, NGram
from pyspark.ml.classification import NaiveBayes

"""
=========================================
exec_naive_bayes.py - Execute Naive Bayes
-----------------------------------------

This python file supports the exec_naive_bayes function which trains a naive
bayes model based on the train and test files and generates an output file
specified by the user in the call to this function.

NOTE: This function uses a number of variables to determine which actions are
performed by the process, and these are values the user may overwrite before
executing the exec_naive_bayes function -- set these with the command:
    exec_naive_bayes.<setting_name> = <value_of_interest>

1) Training and Testing Files:
    train_file = "gs://dip-p1-storage/data/train_full.json"
    test_file = "gs://dip-p1-storage/data/test_full.json"
2) Integrate IDF into the word counts is an option that is on by default
    use_idf = True
3) Specify the number of words that constitute an n-gram
    ngram_count = 1
4) Minimum number of times a word must occur to be accounted for
    min_doc_freq = 3

ENSURE the <output_file> parameter carries the fill path. For example, we used 
values like 'gs://dip-p1-storage/output/pip-regextoken_hash_idf_nb_jbm.txt'

"""

use_idf = True
ngram_count = 1
min_doc_freq = 3
repitions = 30
smoothing_val = 1.0
num_features = 10000
min_doc_freq = 5
train_file = "gs://dip-p1-storage/data/train_full.json"
test_file = "gs://dip-p1-storage/data/test_full.json"

## ex. output file 'gs://dip-p1-storage/output/pip-regextoken_hash_idf_nb.txt'
def exec_naive_bayes(output_file):
    
    #Setting up Spark
    spark = SparkSession.builder.master(
            "yarn").appName("DSP P1- DataFeaturesModel").getOrCreate()
    
    #=======================#
    ### READ TARGET FILES ###
    #-----------------------#
    
    #Reading Train and Test sets along with cache'ing them
    train_df = spark.read.json(
            train_file).withColumn(
                    'text_clean', regexp_replace(
                            "text",
                            '\w{3,20}\s|\\r\\n\w{3,20}', 
                            '')).withColumn(
                            'label', col('category').cast(IntegerType())
                            ).select(
                                    'row_id',
                                    'filename',
                                    'text_clean',
                                    'label').repartition(repitions).cache()
    test_df = spark.read.json(
            test_file).withColumn(
                    'text_clean', regexp_replace(
                            "fulltext",
                            '\w{3,20}\s|\\r\\n\w{3,20}', '')).select(
                            'row_id',
                            'filename',
                            'text_clean').repartition(repitions).cache()
      
    #================================================#
    ### DYNAMICALLY DEFINE PIPELINE FOR PROCESSING ###
    #------------------------------------------------#
    
    regexTokenizer = RegexTokenizer(inputCol="text_clean", 
                                    outputCol="words", 
                                    pattern="\\w")
    ngram = NGram(n=ngram_count, inputCol="words", 
                  outputCol="words")
    hashingTF = HashingTF(inputCol="words", 
                          outputCol="rawFeatures", 
                          numFeatures=num_features)
    idf = IDF(inputCol="rawFeatures", outputCol="features", 
              minDocFreq= min_doc_freq) 
    
    pipeline = Pipeline(stages=[regexTokenizer])
    if(ngram_count > 1):
        pipeline.stages.add(ngram)
    pipeline.stages.add(hashingTF)
    if(idf == True):
        pipeline.stages.add(idf)
    
    # Apply pipeline to the two sets
    pipelineFit = pipeline.fit(train_df)
    train_dataset = pipelineFit.transform(train_df)
    test_dataset = pipelineFit.transform(test_df)
    
    #==============================================#
    ### BUILD THE NAIVE BAYES MODEL AND APPLY IT ###
    #----------------------------------------------#
    
    nb = NaiveBayes(smoothing=smoothing_val, 
                    modelType="multinomial",
                    featuresCol="features")
    nbModel = nb.fit(train_dataset)
    predictions = nbModel.transform(test_dataset)
    test_pred = predictions.select(
            'row_id','prediction').withColumn(
                    'pred_label', col(
                            'prediction').cast(
                                    IntegerType())).drop('prediction')
    test_pred.cache()
    test_pred.withColumn(
            'pred_label_corr',col('pred_label') + lit(1)).sort(
                    asc('row_id')).select(
                            'pred_label_corr').coalesce(1).write.format(
                            'csv').mode(
                                    'overwrite').save(output_file)
