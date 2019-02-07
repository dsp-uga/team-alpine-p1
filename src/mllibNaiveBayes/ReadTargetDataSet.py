from pyspark.sql import SparkSession
from pyspark.sql.functions import concat_ws
from pyspark.sql.functions import collect_list
from pyspark.sql.functions import lower
from pyspark.sql.functions import when
from pyspark.sql.functions import lit
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import StringIndexer

proj1FilePath = "gs://uga-dsp/project1/files/"
proj1DataPath = "gs://uga-dsp/project1/data/bytes/"
fileSets = { "smallTest" : ["X_small_test.txt","y_small_test"],
            "smallTrain" : ["X_small_train.txt","y_small_train"] }

spark = SparkSession.builder.master("yarn").appName("DSP P1- Data Organization").getOrCreate()

def GenCsvFile(fileSet,outputFileName):
    if( fileSet not in fileSets ):
        raise ValueError("ERROR: The argument '"+fileSet+"' is not recognized as a viable file set")
    fileListFile = fileSets[fileSet][0]
    categoryFile = fileSets[fileSet][1]
    fileNames = spark.read.option("header", "false").csv(proj1FilePath+fileListFile,inferSchema=True)
    fileNames = [x + ".bytes" for x in fileNames]
    categories = spark.read.option("header", "false").csv(proj1FilePath+categoryFile,inferSchema=True)

    schema = StructType(
            [StructField("filename",StringType(), True),
             StructField("textVector", StringType(), True),
             StructField("category",StringType(), True)]);
    masterDF = spark.createDataFrame([], schema)

    for i, file in enumerate(fileNames):
        fileContent = spark.option("header", "false").read.option("delimiter", "\s+").csv(proj1DataPath + file, names = 
                                  ["head","col1","col2","col3","col4"
                                   ,"col5","col6","col7","col8"
                                   ,"col9","col10","col11","col12"
                                   ,"col13","col14","col15","col16"])
        fileContent.withColumn("head",when(True,"1"))
        #fileContent = fileContent.drop("head")
        masterDF = fileContent.agg(concat_ws(" ",collect_list(lower(fileContent.text))).alias("fulltext")).withColumn("filename",lit(file)).withColumn("category",categories[i])
        masterDF = masterDF.select('filename','text').union(masterDF)
				
        if i > 2:
            break

    masterDF.repartition(1).write.mode("overwrite").format("com.databricks.spark.csv").save("gs://" + outputFileName, header = "true")

GenCsvFile("smallTest","dataproc-b5ac7384-e5c9-4f67-8e74-38c5f4e32af4-us/google-cloud-dataproc-metainfo/f44052a4-7432-43f0-bfc7-844fdb358228/submyers-test-1-m/smallTest_submyers")






