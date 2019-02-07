from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
import requests

#Function to add text to a string
def add_text(s):
    return (s+'.bytes')

#Function to read byte file for each hash input and return the entire file as a single string
def text_get(fileName):   
	resp = requests.get('https://storage.googleapis.com/uga-dsp/project1/data/bytes/' + fileName).text
	return(resp)

#Setting up Spark
spark = SparkSession.builder.master("yarn").appName("DSP P1- DataTrainTest").getOrCreate()
sc = spark.sparkContext

#Decarling the functions as udf
add_text_udf = udf(add_text)
text_get_udf = udf(text_get)

#Reading the train and test hashes
files_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_train.txt").withColumn("row_id", monotonically_increasing_id()).withColumn('filename',add_text_udf('_c0')).drop('_c0')
files_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_test.txt").withColumn("row_id", monotonically_increasing_id()).withColumn('filename',add_text_udf('_c0')).drop('_c0')

#Reading Train categories
cat_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/y_train.txt").withColumn("row_id", monotonically_increasing_id()).withColumnRenamed('_c0','category')
#cat_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/y_small_test.txt").withColumnRenamed('_c0','category').withColumn("row_id", monotonically_increasing_id())

#Joining train and test hashes with their corresponding categories based on row_id
train_df_1 = files_train.join(cat_train,'row_id',how = 'left').repartition(30)

#Getting text for train and test from hashes using text_get_udf
train_df = train_df_1.withColumn('text',text_get_udf("filename")).repartition(30)
test_df = files_test.repartition(30).withColumn('fulltext',text_get_udf("filename")).select("filename","fulltext","row_id").repartition(30)

#Cache and take 1 to execute upto train_df and test_df
#train_df.cache()
#train_df.take(1)
#test_df.cache()
#test_df.take(1)

#Writing train and test into json format
train_df.write.json("gs://dip-p1-storage/data/train_full.json",mode = 'overwrite')
test_df.write.json("gs://dip-p1-storage/data/test_full.json",mode = 'overwrite')

#train_df_1 = spark.read.json("gs://dip-p1-storage/data/train_full.json")
#test_df_1 = spark.read.json("gs://dip-p1-storage/data/test_full.json")

#Stopping spark
spark.stop()