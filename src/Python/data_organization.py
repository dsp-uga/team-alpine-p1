from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time

#spark = SparkSession.builder.master("local").appName("DSP P1- Data Organization").getOrCreate()
spark = SparkSession.builder.master("yarn").appName("DSP P1- Data Organization").getOrCreate()
#sc = spark.sparkContext

#Setting working directory to location of input file
#path = '/Users/hemanth/Desktop/MSAI/DataSciencePracticum/Projects/p1/share/data/bytes/'
path = 'gs://uga-dsp/project1/data/bytes/'
#os.chdir(path)

sc = spark.sparkContext
files_train = sc.textFile("gs://uga-dsp/project1/files/X_train.txt").collect()
files_test = sc.textFile("gs://uga-dsp/project1/files/X_test.txt").collect()
files = files_train + files_test
files = [x+'.bytes' for x in files]

broadcastVar = sc.broadcast(files)

# def add_text(s):
#     return (s+'.bytes')
# 
# add_text_udf = udf(add_text)
# 
# files_train = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_train.txt").withColumnRenamed('_c0','hash')
# files_train_df = files_train.withColumn('filename',add_text_udf(files_train.hash)).select('filename')
# 
# files_test = spark.read.option("header", "false").csv("gs://uga-dsp/project1/files/X_test.txt").withColumnRenamed('_c0','hash')
# files_test_df = files_test.withColumn('filename',add_text_udf(files_test.hash)).select('filename')
# 
# files_df = files_train_df.union(files_test_df)

#Creating empty master dataframe to store entire input text and their filenames
schema = StructType([StructField("filename",StringType(), True),StructField("text", StringType(), True)])
masterDF = spark.createDataFrame([], schema)

# def get_data_text(s):    
#     #file = "68icCkFVRJK5UtxLOqIu.bytes"
#     df = spark.read.option("header", "false").text(path + file).withColumnRenamed('value','text')
#     #Aggregating text in df into a single row
#     dfText = df.agg(concat_ws(" ",collect_list(lower(df.text))).alias('fulltext')).withColumn('filename',lit(file))
#     #Removing words having length more than 3 and less than 20, so as to keep only words with length 2
#     dfTextFilter = dfText.withColumn('text', regexp_replace(dfText.fulltext, '\w{3,20}', ''))
#     dfTextonly = dfTextFilter.select('text').collect()
#     #Appending to master dataframe
#     return(dfTextonly[0])
# 
# get_data_text_udf = udf(get_data_text)
# 
#         
# files_df_text = files_df.withColumn("text",get_data_text_udf(files_test_df))



start = time.time()
for file in broadcastVar.value:
    #Reading the text file into df
    df = spark.read.option("header", "false").text(path + file).withColumnRenamed('value','text')
    #Aggregating text in df into a single row
    dfText = df.agg(concat_ws(" ",collect_list(lower(df.text))).alias('fulltext')).withColumn('filename',lit(file))
    #Removing words having length more than 3 and less than 20, so as to keep only words with length 2
    dfTextFilter = dfText.withColumn('text', regexp_replace(dfText.fulltext, '\w{3,20}', ''))
    #Appending to master dataframe
    masterDF = dfTextFilter.select('filename','text').union(masterDF)

elapsed_time_fl = (time.time() - start)

#Writing the masterDF to csv
masterDF.repartition(1).write.mode("overwrite").format('com.databricks.spark.csv').save("gs://dip-p1-storage/data/datafull.csv",header = 'true')

#masterDF = spark.read.option("header", "true").csv("gs://dip-p1-storage/data/data_small.csv")

#Stopping spark
spark.stop()