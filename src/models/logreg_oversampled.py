from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, Tokenizer, HashingTF, CountVectorizer, RegexTokenizer, StringIndexer, NGram
from pyspark.ml.classification import LogisticRegression, LinearSVC, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

# Setting up Spark
spark = SparkSession.builder.master("yarn") \
    .appName("DSP P1- DataFeaturesModel") \
    .getOrCreate()
sc = spark.sparkContext
# Reading Train set and cache'ing it
train_df = spark.read.json("gs://dip-p1-storage/data/train_full.json") \
    .withColumn('text_clean', regexp_replace("text", '\w{3,20}|[\\r\\n]', '')) \
    .withColumn('label', col('category').cast(IntegerType())) \
    .select('row_id','filename','text_clean','label') \
    .repartition(30)
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
schema = StructType([StructField("row_id",StringType(), True), StructField("filename", StringType(), True),StructField("text_clean", StringType(), True), StructField("label", LongType(), True)])
new_train_df = spark.createDataFrame([], schema)

# Merging duplicated label sets into new_train_df
for i in range(len(duplication_factor)):
    if duplication_factor[i] != 1:
        original_df = train_df.filter(train_df.label == count_dict_keys[i])
        partial_df = original_df
        for j in range(duplication_factor[i]-1):
            partial_df = partial_df.union(original_df)
        new_train_df = new_train_df.union(partial_df).repartition(10)
    else:
        original_df = train_df.filter(train_df.label == count_dict_keys[i])
        new_train_df = new_train_df.union(original_df).repartition(10)

new_train_df.cache()
test_df = spark.read.json("gs://dip-p1-storage/data/test_full.json").withColumn('text_clean', regexp_replace("fulltext", '\w{3,20}|[\\r\\n]', '')).select('row_id','filename','text_clean').repartition(30)
# Performing feature extraction on new training set with duplicated instances
regexTokenizer = RegexTokenizer(inputCol="text_clean", outputCol="words", pattern="\\w")
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures")
idf = IDF(inputCol="rawFeatures", outputCol="features", minDocFreq= 5)
pipeline = Pipeline(stages=[regexTokenizer, hashingTF, idf])
pipelineFit = pipeline.fit(new_train_df)
train_dataset = pipelineFit.transform(new_train_df)
test_dataset = pipelineFit.transform(test_df)

lr = LogisticRegression(maxIter=10, regParam=0.3, family="multinomial")
lrModel = lr.fit(train_dataset)
predictions = lrModel.transform(test_dataset)
test_pred = predictions.select('row_id','prediction') \
    .withColumn('pred_label', col('prediction').cast(IntegerType())) \
    .drop('prediction')
test_pred.cache()
test_pred.sort(asc('row_id')).select('pred_label').coalesce(1) \
    .write.format('csv') \
    .mode('overwrite') \
    .save('gs://uga-dsp-output-ay/pip-mod-regextoken_hash_idf_lr_AY.txt')
