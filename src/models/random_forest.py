#===================================================================#
### random_forest.py - Executes Random Forest Model ###
#-------------------------------------------------------------------#
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, col, asc
from pyspark.sql.types import StructType, StringType, LongType
from pyspark.sql.types import StructField, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import CountVectorizer, RegexTokenizer, PCA
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder


#base_output_directory = "gs://dip-p1-storage/output/"
#base_data_direcotry = "gs://dip-p1-storage/data/"
#min_doc_freq = 5
#file_repartition_count = 30
#n_gram_val=1
#pca_val = False
#cv_val = False
#oversampling_val = False


def get_filename(pca_val, base_output_directory):
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
        .save(get_filename(pca_val, base_output_directory))


rand_forest(pca_val, base_output_directory, file_repartition_count)
