# Script for logistic regression classifier - using RegexTokenizer, HashingTF, IDF in the pipeline.
# The model undergoes cross-validation with k = 5.

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, Tokenizer, HashingTF, CountVectorizer, RegexTokenizer, StringIndexer, NGram
from pyspark.ml.classification import LogisticRegression, LinearSVC, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

#Setting up Spark
spark = SparkSession.builder.master("yarn") \
    .appName("DSP P1- Logistic Regression Model") \
    .getOrCreate()
sc = spark.sparkContext
#Reading Train set and cache'ing it
train_df = spark.read.json("gs://dip-p1-storage/data/train_full.json") \
    .withColumn('text_clean', regexp_replace("text", '\w{3,20}|[\\r\\n]', '')) \
    .withColumn('label', col('category').cast(IntegerType())) \
    .select('row_id','filename','text_clean','label') \
    .repartition(30)
train_df.cache()

#Reading Test set
test_df = spark.read.json("gs://dip-p1-storage/data/test_full.json") \
    .withColumn('text_clean', regexp_replace("fulltext", '\w{3,20}|[\\r\\n]', '')) \
    .select('row_id','filename','text_clean') \
    .repartition(30)

regexTokenizer = RegexTokenizer(inputCol="text_clean", outputCol="words", pattern="\\w")
hashingTF = HashingTF(inputCol="bigram_words", outputCol="rawFeatures")
idf = IDF(inputCol="rawFeatures", outputCol="features", minDocFreq= 5)
pipeline = Pipeline(stages=[regexTokenizer, hashingTF, idf])
pipelineFit = pipeline.fit(train_df)
train_dataset = pipelineFit.transform(train_df)
test_dataset = pipelineFit.transform(test_df)

lr = LogisticRegression(maxIter=10, regParam=0.3, family="multinomial")
paramGrid = ParamGridBuilder() \
    .addGrid(hashingTF.numFeatures, [10000]) \
    .addGrid(lr.regParam, [0.1]) \
    .build()
crossval = CrossValidator(estimator=lr, estimatorParamMaps=paramGrid,
                          evaluator=MulticlassClassificationEvaluator(), numFolds=5)
cvModel = crossval.fit(train_dataset)
predictions = cvModel.transform(test_dataset)
test_pred = predictions.select('row_id','prediction') \
    .withColumn('pred_label', col('prediction').cast(IntegerType())) \
    .drop('prediction')
test_pred.cache()
test_pred.take(1)
test_pred.sort(asc('row_id')) \
    .select('pred_label').coalesce(1) \
    .write.format('csv') \
    .mode('overwrite') \
    .save('gs://uga-dsp-output-ay/pip-regextoken_hash_idf_lr_cv_AY.txt')
