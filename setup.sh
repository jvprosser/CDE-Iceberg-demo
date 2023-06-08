#!bash
pip install pandas numpy scikit-learn
mkdir -p data
touch data/features.txt
hdfs dfs -copyFromLocal wine-quality-*csv s3a://go01-demo/tmp/
