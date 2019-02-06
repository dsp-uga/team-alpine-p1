from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id

def add_text(s):
    return (s+'.bytes')

add_text_udf = udf(add_text)


#spark = SparkSession.builder.master("local").appName("DSP P1- Data Organization").getOrCreate()
spark = SparkSession.builder.master(
        "yarn").appName(
                "DSP P1- Train & Test set creation").getOrCreate()
sc = spark.sparkContext

#Reading masterDF
masterDF = spark.read.option(
        "header", "true").csv(
                "gs://dip-p1-storage/data/data_small.csv")

#Reading train and test hashes
files_train = spark.read.option(
        "header", "false").csv(
                "gs://uga-dsp/project1/files/X_small_train.txt").withColumnRenamed(
                        '_c0','hash').withColumn(
                                "row_id", monotonically_increasing_id())
files_train_df = files_train.withColumn(
        'filename',add_text_udf(files_train.hash)).select(
                'filename','row_id')

files_test = spark.read.option(
        "header", "false").csv(
                "gs://uga-dsp/project1/files/X_small_test.txt").withColumnRenamed(
                        '_c0','hash').withColumn(
                                "row_id", monotonically_increasing_id())
files_test_df = files_test.withColumn(
        'filename',add_text_udf(files_test.hash)).select('filename','row_id')

#Reading Train and Test categories
cat_train = spark.read.option(
        "header", "false").csv(
                "gs://uga-dsp/project1/files/y_small_train.txt").withColumnRenamed(
                        '_c0','category').withColumn(
                                "row_id", monotonically_increasing_id())
cat_test = spark.read.option(
        "header", "false").csv(
                "gs://uga-dsp/project1/files/y_small_test.txt").withColumnRenamed(
                        '_c0','category').withColumn(
                                "row_id", monotonically_increasing_id())

#Joining files_train_df with categories
train_df_1 = files_train_df.join(cat_train,'row_id',how = 'left')
#Joining with masterDF
train_df = train_df_1.join(
        masterDF,'filename',how = 'left').select(
                'filename','text','category')

#Joining files_test_df with categories
test_df_1 = files_test_df.join(cat_test,'row_id',how = 'left')
#Joining test with masterDF
test_df = test_df_1.join(
        masterDF,'filename',how = 'left').select('filename','text','category')

#Writing the masterDF to csv
train_df.repartition(1).write.mode(
        "overwrite").format(
                'com.databricks.spark.csv').save(
                        "gs://dip-p1-storage/data/train_small.csv",
                        header = 'true')
test_df.repartition(1).write.mode(
        "overwrite").format(
                'com.databricks.spark.csv').save(
                        "gs://dip-p1-storage/data/test_small.csv"
                        ,header = 'true')

#train_df = spark.read.option("header", "true").csv("gs://dip-p1-storage/data/train_small.csv")
#test_df = spark.read.option("header", "true").csv("gs://dip-p1-storage/data/test_small.csv")

#Stopping spark
spark.stop()