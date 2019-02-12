from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
import requests
import re
from pyspark.sql.functions import lower, col, concat
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, Tokenizer,HashingTF,CountVectorizer,RegexTokenizer,StopWordsRemover,NGram,PCA
from pyspark.ml.classification import NaiveBayes,LogisticRegression,LinearSVC,OneVsRest,RandomForestClassifier,GBTClassifier,MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer

#Reading Train Bytes and Asm files
train_bytes = spark.read.json("gs://dip-p1-storage/data/train_full_bytes.json")
test_bytes = spark.read.json("gs://dip-p1-storage/data/test_full_bytes.json")

#Reading Test Bytes and Asm files
train_asm = spark.read.json("gs://dip-p1-storage/data/train_full_asm.json")
test_asm = spark.read.json("gs://dip-p1-storage/data/test_full_asm.json")

#Joining Train and Test files respectively
train_df = train_bytes.select("bytes_text","row_id").join(train_asm,"row_id",how = "left").select("row_id","bytes_text","asm_text","category")
test_df = test_bytes.select("bytes_text","row_id").join(test_asm,"row_id",how = "left").select("row_id","bytes_text","asm_text")

#Concatinating bytestext and asmtext columns into a single column
train_set = train_df.withColumn('text',lower(concat(col("bytes_text"),lit(" "),col("asm_text"))))
test_set = test_df.withColumn('text',lower(concat(col("bytes_text"),lit(" "),col("asm_text"))))

#Declaring Pipeline
regexTokenizer = RegexTokenizer(inputCol="text", outputCol="words", pattern="\\W")
cv = CountVectorizer(inputCol="words", outputCol="rawFeatures")
pipeline = Pipeline(stages=[regexTokenizer,cv])

#Fitting the pipeline
pipelineFit = pipeline.fit(train_set)
train_dataset = pipelineFit.transform(train_set).withColumn('label', col('category').cast(IntegerType()))
test_dataset = pipelineFit.transform(test_set)

#Training Random Forest Classifier
rf = RandomForestClassifier(labelCol="label", featuresCol="rawFeatures", numTrees=50,maxDepth = 30)
rfFit = rf.fit(train_dataset)
predictions = rfFit.transform(test_dataset).withColumn('pred_label', col('prediction').cast(IntegerType())).drop('prediction')

predictions.sort(asc('row_id')).select('pred_label').coalesce(1).write.format('csv').mode('overwrite').save('gs://dip-p1-storage/output/asmbytes_full_cv_pca20_rf_HD.txt') 

spark.stop()