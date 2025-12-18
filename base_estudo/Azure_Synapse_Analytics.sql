-- Synapse SQL
CREATE EXTERNAL TABLE fraud_transactions
WITH (
    LOCATION = 'transactions/',
    DATA_SOURCE = fraud_data_lake,
    FILE_FORMAT = parquet_format
) AS
SELECT 
    transaction_id,
    user_id,
    amount,
    fraud_score,
    CASE WHEN fraud_score > 0.7 THEN 1 ELSE 0 END as is_fraud
FROM 
    OPENROWSET(
        BULK 'abfss://curated@stfraudprod.dfs.core.windows.net/transactions/*.parquet',
        FORMAT = 'PARQUET'
    ) AS transactions