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



Collapse 

4:07 PM
DataFeaturesModel.txt 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, Tokenizer,HashingTF,CountVectorizer,RegexTokenizer
from pyspark.ml.classification import NaiveBayes,LogisticRegression,RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer
#Setting up Spark
spark = SparkSession.builder.master("yarn").appName("DSP P1- DataFeaturesModel").getOrCreate()
sc = spark.sparkContext
#Reading Train set and cache'ing it
train_df = spark.read.json("gs://dip-p1-storage/data/train_full.json").withColumn('text_clean', regexp_replace("text", '\w{3,20}|[\\r\\n]', '')).withColumn('label', col('category').cast(IntegerType())).select('row_id','filename','text_clean','label').repartition(30)
train_df.cache()
train_df.take(1)
#Reading Test set
test_df = spark.read.json("gs://dip-p1-storage/data/test_full.json").withColumn('text_clean', regexp_replace("fulltext", '\w{3,20}|[\\r\\n]', '')).select('row_id','filename','text_clean').repartition(30)
#Basic Data exploration on Train
train_df_cats_counts = train_df.groupBy('category').count()
# Configure an ML pipeline, which consists of three stages: tokenizer, hashingTF, and lr.
tokenizer = Tokenizer(inputCol="text_clean", outputCol="words")
wordsData = tokenizer.transform(train_df)
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=20)
featurizedData = hashingTF.transform(wordsData)
idf = IDF(inputCol="rawFeatures", outputCol="features",minDocFreq=3)
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)
rescaledData.select("label", "features").show()
pca = PCA(k=15, inputCol=idf.getOutputCol(), outputCol="pcaFeatures")
model = pca.fit(rescaledData)
result = model.transform(rescaledData)
svm = LinearSVC(maxIter=10, regParam=0.1,featuresCol="pcaFeatures")
ovr = OneVsRest(classifier=svm)
ovrModel = ovr.fit(result)
layers = [4, 5, 4, 3]
trainer = MultilayerPerceptronClassifier(maxIter=100, layers=layers, blockSize=128, seed=1234,featuresCol="pcaFeatures")
model = trainer.fit(result)
#Test set
wordsData = tokenizer.transform(test_df)
featurizedData = hashingTF.transform(wordsData)
idfModel = idf.transform(featurizedData)
rescaledData = idfModel.transform(featurizedData)
model = pca.fit(rescaledData)
result = model.transform(rescaledData)
svmPred = svm.fit(result)
# create the trainer and set its parameters 
nb = NaiveBayes(smoothing=1.0, modelType="multinomial")
################################################################################################
#New pipeline
################################################################################################
regexTokenizer = RegexTokenizer(inputCol="text_clean", outputCol="words", pattern="\\w")
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features", minDocFreq= 5) 
pipeline = Pipeline(stages=[regexTokenizer, hashingTF, idf])
pipelineFit = pipeline.fit(train_df)
train_dataset = pipelineFit.transform(train_df)
test_dataset = pipelineFit.transform(test_df)
nb = NaiveBayes(smoothing=1.0, modelType="multinomial",featuresCol="features")
nbModel = nb.fit(train_dataset)
predictions = nbModel.transform(test_dataset)
test_pred = predictions.select('row_id','prediction').withColumn('pred_label', col('prediction').cast(IntegerType())).drop('prediction')
test_pred.cache()
test_pred.take(1)
test_pred.withColumn('pred_label_corr',col('pred_label') + lit(1)).sort(asc('row_id')).select('pred_label_corr').coalesce(1).write.format('csv').mode('overwrite').save('gs://dip-p1-storage/output/pip-regextoken_hash_idf_nb.txt')
#######################################################################################################
# Convert target into numerical categories
tokenizer = Tokenizer(inputCol="text_clean", outputCol="words")
hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="rawfeatures")
#cv = CountVectorizer(inputCol=tokenizer.getOutputCol(), outputCol="rawfeatures")
#idf = IDF(inputCol = hashingTF.getOutputCol(), outputCol ="features")
#pca = PCA(k=50, inputCol=idf.getOutputCol(), outputCol="pcaFeatures")
nb = NaiveBayes(smoothing=1.0, modelType="multinomial",featuresCol="rawfeatures")
#lr = LogisticRegression(maxIter=10, regParam=0.001)
#svm = LinearSVC(maxIter=5, regParam=0.01,featuresCol=pca.getOutputCol(),predictionCol="label")
pipeline = Pipeline(stages=[tokenizer, hashingTF, nb])
# Fit the pipeline to training documents.
model = pipeline.fit(train_df)
#Predictions
prediction = model.transform(test_df)
test_pred = prediction.select('row_id','prediction').withColumn('pred_label', col('prediction').cast(IntegerType())).drop('prediction')
test_pred.cache()
test_pred.take(1)
#Saving output as a text file
#test_pred.withColumn('pred_label', col('prediction').cast(IntegerType())).select('row_id','pred_label').sort(asc('row_id')).select('pred_label').coalesce(1).write.format('csv').save('gs://dip-p1-storage/output/pip-token_hash_nb.txt')
test_pred.sort(asc('row_id')).select('pred_label').coalease(1).write.format('csv').save('gs://dip-p1-storage/output/pip-token_hash_nb.txt')
# compute accuracy on the test set
#evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction",metricName="accuracy")
#accuracy = evaluator.evaluate(prediction)
#print("Test set accuracy = " + str(accuracy))