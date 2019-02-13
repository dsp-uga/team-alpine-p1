from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, col, lit, asc
from pyspark.sql.types import IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, HashingTF, RegexTokenizer, NGram
from pyspark.ml.classification import NaiveBayes

"""
#===============================================#
### exec_naive_bayes.py - Execute Naive Bayes ###
#-----------------------------------------------#

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
def exec_naive_bayes(output_file, use_idf = True,
                    ngram_count = 1,
                    repitions = 30,
                    smoothing_val = 1.0,
                    num_features = 10000,
                    min_doc_freq = 5,
                    train_file = "gs://dip-p1-storage/data/train_full.json",
                    test_file = "gs://dip-p1-storage/data/test_full.json"):
    
    #Setting up Spark
    spark = SparkSession.builder.master("yarn") \
        .appName("DSP P1- DataFeaturesModel").getOrCreate()
    
    #=======================#
    ### READ TARGET FILES ###
    #-----------------------#
    
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
      
    #================================================#
    ### DYNAMICALLY DEFINE PIPELINE FOR PROCESSING ###
    #------------------------------------------------#
    
    print('Fitting pipeline with regexTokenizer, N-Gram, HashingTF, IDF, PCA...')
    regexTokenizer = RegexTokenizer(inputCol="text",
                                    outputCol="words",
                                    pattern="\\w")
    ngram = NGram(n=ngram_count, 
                  inputCol="words",
                  outputCol="nGramWords")
    if(use_idf == True):
        hashingTF = HashingTF(inputCol="nGramWords",
                              outputCol="rawFeatures",
                              numFeatures=num_features)
    else:
        hashingTF = HashingTF(inputCol="nGramWords",
                              outputCol="rawFeatures",
                              numFeatures=num_features)
    idf = IDF(inputCol="rawFeatures", 
              outputCol="idfFeatures", 
              minDocFreq= min_doc_freq)
    
    stages_list = [regexTokenizer]
    stages_list.append(ngram)
    stages_list.append(hashingTF)
    if(use_idf == True):
        stages_list.append(idf)
    pipeline = Pipeline(stages=stages_list)
    print('Completed fitting pipeline...')
    print('=============================')
    
    # Apply pipeline to the two sets
    pipeline_fit = pipeline.fit(train_df)
    train_dataset = pipeline_fit.transform(train_df)
    pipeline_fit = pipeline.fit(test_df)
    test_dataset = pipeline_fit.transform(test_df)
    
    #==============================================#
    ### BUILD THE NAIVE BAYES MODEL AND APPLY IT ###
    #----------------------------------------------#
    
    print('Fitting Naive Bayes Model with trainig data...')
    if(use_idf == True):
        nb = NaiveBayes(smoothing=smoothing_val, 
                        modelType="multinomial",
                        featuresCol="idfFeatures")
        nb_model = nb.fit(train_dataset)
        print('Completed building the Naive Bayes Model...')
        print('===========================================')
        print('Applying Model to test data...')
        predictions = nb_model.transform(test_dataset)
        test_pred = predictions.select(
                'row_id','prediction').withColumn(
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
                'row_id','prediction').withColumn(
                        'pred_label', col(
                                'prediction').cast(
                                        IntegerType())
                        ).drop('prediction').repartition(repitions)
        print('Completed prediction!')
        print('===========================================')
        
    test_pred.cache()
    print('Saving test predictions to file');
    test_pred.withColumn(
            'pred_label_corr',col('pred_label') + lit(1)).sort(
                    asc('row_id')).select(
                            'pred_label_corr').coalesce(1).write.format(
                            'csv').mode(
                                    'overwrite').save(output_file)
    print('Prediction File Complete');
    print('========================');
