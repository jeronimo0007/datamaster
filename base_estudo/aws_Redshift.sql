-- Redshift Spectrum
CREATE EXTERNAL TABLE fraud_transactions
FROM PARQUET
LOCATION 's3://fraud-detection-data/curated/transactions/'