from pyspark.sql import SparkSession
from pyspark.ml.feature import CountVectorizer, NGram
from pyspark.sql.functions import split
from pyspark.sql.types import IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import IDF, Tokenizer,HashingTF,CountVectorizer,PCA
from pyspark.ml.classification import NaiveBayes,LogisticRegression,LinearSVC,MultilayerPerceptronClassifier,OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


train_df = spark.read.option("header", "true").csv("gs://dip-p1-storage/data/train_small.csv").withColumnRenamed("category","label")
train_df = train_df.withColumn("label", train_df.label.cast(IntegerType()))

test_df = spark.read.option("header", "true").csv("gs://dip-p1-storage/data/test_small.csv").withColumnRenamed("category","label")
test_df = test_df.withColumn("label", test_df.label.cast(IntegerType()))        

# Configure an ML pipeline, which consists of three stages: tokenizer, hashingTF, and lr.
tokenizer = Tokenizer(inputCol="text", outputCol="words")
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









tokenizer = Tokenizer(inputCol="text", outputCol="words")
hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="rawfeatures")
#cv = CountVectorizer(inputCol=tokenizer.getOutputCol(), outputCol="rawfeatures")
idf = IDF(inputCol = hashingTF.getOutputCol(), outputCol ="features")
pca = PCA(k=50, inputCol=idf.getOutputCol(), outputCol="pcaFeatures")
#nb = NaiveBayes(smoothing=1.0, modelType="multinomial",featuresCol="features")
#lr = LogisticRegression(maxIter=10, regParam=0.001)
svm = LinearSVC(maxIter=5, regParam=0.01,featuresCol=pca.getOutputCol(),predictionCol="label")

pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, pca,svm])

# Fit the pipeline to training documents.
model = pipeline.fit(train_df)

#Predictions
prediction = model.transform(test_df)

# compute accuracy on the test set
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction",
                                              metricName="accuracy")
accuracy = evaluator.evaluate(prediction)
print("Test set accuracy = " + str(accuracy))



