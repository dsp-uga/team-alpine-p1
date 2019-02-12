#==================================================================#
### logistic_regression.py - Executes Logistics Regression Model ###
#------------------------------------------------------------------#
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, col, asc
from pyspark.sql.types import StructType, StringType, LongType
from pyspark.sql.types import StructField, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, HashingTF, RegexTokenizer, NGram, PCA
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder


base_output_directory = "gs://dip-p1-storage/output/"
base_data_direcotry = "gs://dip-p1-storage/data/"
min_doc_freq = 5
file_repartition_count = 30
n_gram_val = 1
pca_val = False
cv_val = False
oversampline_val = False


def get_filename(n_gram_val, pca_val, cv_val, oversampling_val):
    """
    Returns the filename based on the parameters entered during main function call.
    :param n_gram_val: 1-Gram, 2-Gram or 3-Gram
    :param pca_val: Enabling or disabling feature dimensionality reduction using PCA
    :param cv_val: Enabling or disabling cross validation
    :param oversampling_val: Enabling or disabling oversampling of training data
    :return: filename with which output should be saved
    """
    n_gram_string = str(n_gram_val)+'gram' if n_gram_val != 1 else ''
    pca_string = 'pca' if pca_val else ''
    cv_string = 'cv' if cv_val else ''
    oversampling_string = 'oversampled' if oversampling_val else ''
    filename = 'pip-regextoken_' + n_gram_string + '_hash_tf_idf_' \
               + pca_string + '_' + cv_string + '_' \
               + oversampling_string + '.txt'
    filesave = base_output_directory + filename
    return filesave


def log_reg(n_gram_val, pca_val, cv_val, oversampling_val):
    """
    Fits the logistic regression model on the training data and makes predictions on the test set based on the
    given input parameters.
    :param n_gram_val: 1-Gram, 2-Gram or 3-Gram
    :param pca_val: Enabling or disabling feature dimensionality reduction using PCA
    :param cv_val: Enabling or disabling cross validation
    :param oversampling_val: Enabling or disabling oversampling of training data
    :return: writes file into Google storage bucket
    """
    #Setting up Spark
    spark = SparkSession.builder.master("yarn") \
        .appName("DSP P1- Logistic Regression Model") \
        .getOrCreate()
    #Reading Train set and cache'ing it
    train_df = spark.read.json(base_data_direcotry + "train_full.json") \
        .withColumn('text_clean', 
                    regexp_replace("text", '\w{3,20}|[\\r\\n]', '')) \
        .withColumn('label', col('category').cast(IntegerType())) \
        .select('row_id','filename','text_clean','label') \
        .repartition(file_repartition_count)
    #Reading Test set
    test_df = spark.read.json(base_data_direcotry + "/test_full.json") \
        .withColumn('text_clean', regexp_replace("fulltext", '\w{3,20}|[\\r\\n]', '')) \
        .select('row_id','filename','text_clean') \
        .repartition(file_repartition_count)
    if oversampling_val:
        # Getting individual counts of documents for each label
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
                             StructField("text_clean", StringType(), True),
                             StructField("label", LongType(), True)])
        new_train_df = spark.createDataFrame([], schema)
        # Merging duplicated label sets into new_train_df
        for i in range(len(duplication_factor)):
            if duplication_factor[i] != 1:
                original_df = train_df.filter(
                    train_df.label == count_dict_keys[i])
                partial_df = original_df
                for j in range(duplication_factor[i] - 1):
                    partial_df = partial_df.union(original_df)
                new_train_df = new_train_df.union(partial_df).repartition(10)
            else:
                original_df = train_df.filter(
                    train_df.label == count_dict_keys[i])
                new_train_df = new_train_df.union(original_df).repartition(10)
    else:
        new_train_df = train_df
    # Pipeline and creation of train_dataset and test_dataset
    regexTokenizer = RegexTokenizer(inputCol="text_clean", 
                                    outputCol="words", 
                                    pattern="\\w")
    ngram = NGram(n=n_gram_val, inputCol="words", outputCol="ngram_words")
    hashingTF = HashingTF(inputCol="ngram_words", 
                          outputCol="rawFeatures", 
                          numFeatures=256)
    if not pca_val:
        idf = IDF(inputCol="rawFeatures", 
                  outputCol="features", 
                  minDocFreq=min_doc_freq)
        pipeline = Pipeline(stages=[regexTokenizer, ngram, hashingTF, idf])
    else:
        idf = IDF(inputCol="rawFeatures", 
                  outputCol="idf_features", 
                  minDocFreq=min_doc_freq)
        pca = PCA(k=20, inputCol="idf_features", outputCol="features")
        pipeline = Pipeline(
                stages=[regexTokenizer, ngram, hashingTF, idf, pca])
    pipelineFit = pipeline.fit(new_train_df)
    train_dataset = pipelineFit.transform(new_train_df)
    test_dataset = pipelineFit.transform(test_df)
    lr = LogisticRegression(maxIter=10, regParam=0.3, family="multinomial")
    if cv_val:
        # Is executed if cross validation is enabled
        paramGrid = ParamGridBuilder() \
            .addGrid(hashingTF.numFeatures, [256]) \
            .addGrid(lr.regParam, [0.3]) \
            .build()
        crossval = CrossValidator(estimator=lr,
                                  estimatorParamMaps=paramGrid,
                                  evaluator=MulticlassClassificationEvaluator(),
                                  numFolds=5)
        cvModel = crossval.fit(train_dataset)
        predictions = cvModel.transform(test_dataset)
    else:
        # Is executed when cross validation is disabled
        lrModel = lr.fit(train_dataset)
        predictions = lrModel.transform(test_dataset)
    # Making predictions for test data
    test_pred = predictions.select('row_id', 'prediction') \
        .withColumn('pred_label', col('prediction').cast(IntegerType())) \
        .drop('prediction')
    test_pred.cache()
    # Sorting test data on row_id to neutralize effects of shuffling
    test_pred.sort(asc('row_id')) \
        .select('pred_label').coalesce(1) \
        .write.format('csv') \
        .mode('overwrite') \
        .save(get_filename(n_gram_val, pca_val, cv_val, oversampling_val))


log_reg(n_gram_val, cv_val, pca_val, oversampline_val)