from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
import requests
import re
from pyspark.sql.functions import lower, col, concat
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

#Function to add text to a string
def add_asm_text(s):
    return (s+'.asm')

#Function to read byte file for each hash input and return the entire file as a single string
def text_asm_get(fileName):   
	resp = requests.get('https://storage.googleapis.com/uga-dsp/project1/data/asm/' + fileName).text
	lines = resp.splitlines()
	firsts = [line.split("\\s+")[0] for line in lines]
	first = [word if ":" not in word else word.split(':')[0] for word in firsts]
	varList = " ".join(first)
	return(varList)

#Setting up Spark
spark = SparkSession.builder.master("yarn").appName("DSP P1- DataTrainTest").getOrCreate()
sc = spark.sparkContext

#Decarling the functions as udf
add_asm_text_udf = udf(add_asm_text)
text_asm_get_udf = udf(text_asm_get)

#Reading the train and test hashes
files_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_train.txt").withColumn("row_id", monotonically_increasing_id()).withColumn('filename',add_asm_text_udf('_c0')).drop('_c0')

files_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_test.txt").withColumn("row_id", monotonically_increasing_id()).withColumn('filename',add_asm_text_udf('_c0')).drop('_c0')

#Reading Train categories
cat_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/y_train.txt").withColumn("row_id", monotonically_increasing_id()).withColumnRenamed('_c0','category')
#cat_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/y_small_test.txt").withColumn("row_id", monotonically_increasing_id()).withColumnRenamed('_c0','category')

#Joining train and test hashes with their corresponding categories based on row_id
train_df_1 = files_train.join(cat_train,'row_id',how = 'left').repartition(80)
#test_df_1 = files_test.join(cat_test,'row_id',how = 'left').repartition(80)

#Getting text for train and test from hashes using text_get_udf
train_df = train_df_1.withColumn('asm_text',text_asm_get_udf("filename")).repartition(80)
test_df = files_test.withColumn('asm_text',text_asm_get_udf("filename")).repartition(80)

#Writing train and test into json format
train_df.write.json("gs://dip-p1-storage/data/train_full_asm.json",mode = 'overwrite')
test_df.write.json("gs://dip-p1-storage/data/test_full_asm.json",mode = 'overwrite')

#Stopping spark
spark.stop()