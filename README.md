# CSCI 8360 - Project 1 - Malware Classification

## Synopsis

To address the [Kaggel Microsoft Maleware Classification Problem](https://www.kaggle.com/c/malware-classification), we implemented
a Python Spark ([pyspark](https://spark.apache.org/docs/2.2.1/api/python/pyspark.html)) script that trains data science models to 
classify malware files. As part of the University of Georgia Computer Science course CSCI 8360, the software's design centers on execution
in the [Google Cloud Platform](https://cloud.google.com/) along with accessing pertenant data through a 
[Google Data Storage](https://cloud.google.com/storage/) course related 
[location](https://console.cloud.google.com/storage/browser/uga-dsp/project1) 
managed by the professor Quinn. This document discusses the data science models supported by our software, the parameters necessary for 
instantiating them, and instructions on how to execute this code.

### Authors

