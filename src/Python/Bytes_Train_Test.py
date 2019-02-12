from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
import requests
import re

#Function to add text to a string
def add_bytes_text(s):
    return (s+'.bytes')

#Function to read byte file for each hash input and return the entire file as a single string
def text_bytes_get(fileName): 
	resp = requests.get('https://storage.googleapis.com/uga-dsp/project1/data/bytes/' + fileName).text
	resp_filtered = ' '.join([w for w in resp.split() if len(w)<3])
	return(resp_filtered)

#Setting up Spark
spark = SparkSession.builder.master("yarn").appName("DSP P1- DataTrainTest").getOrCreate()
sc = spark.sparkContext

#Decarling the functions as udf
add_bytes_text_udf = udf(add_bytes_text)
text_bytes_get_udf = udf(text_bytes_get)

#Reading the train and test hashes
files_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_train.txt").withColumn("row_id", monotonically_increasing_id()).withColumn('filename',add_bytes_text_udf('_c0')).drop('_c0')
files_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_test.txt").withColumn("row_id", monotonically_increasing_id()).withColumn('filename',add_bytes_text_udf('_c0')).drop('_c0')

#Reading Train categories
cat_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/y_train.txt").withColumn("row_id", monotonically_increasing_id()).withColumnRenamed('_c0','category')
#cat_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/y_test.txt").withColumn("row_id", monotonically_increasing_id()).withColumnRenamed('_c0','category')

#Joining train and test hashes with their corresponding categories based on row_id
train_df_1 = files_train.join(cat_train,'row_id',how = 'left').repartition(40)
#test_df_1 = files_test.join(cat_test,'row_id',how = 'left').repartition(40)

#Getting text for train and test from hashes using text_get_udf
train_df = train_df_1.withColumn('bytes_text',text_bytes_get_udf("filename")).repartition(40)
test_df = files_test.withColumn('bytes_text',text_bytes_get_udf("filename")).select("filename","bytes_text","row_id").repartition(40)

#Writing train and test into json format
train_df.write.json("gs://dip-p1-storage/data/train_full_bytes.json",mode = 'overwrite')
test_df.write.json("gs://dip-p1-storage/data/test_full_bytes.json",mode = 'overwrite')

#train_df_1 = spark.read.json("gs://dip-p1-storage/data/train_full.json")
#test_df_1 = spark.read.json("gs://dip-p1-storage/data/test_full.json")

#Stopping spark
spark.stop()