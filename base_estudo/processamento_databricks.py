# Notebook Databricks: Detecção de Fraudes
from databricks.feature_store import FeatureStoreClient

# Carregar dados do Data Lake
df = spark.read.format("delta").load("abfss://processed@datalake.dfs.core.windows.net/transactions")

# Executar Data Quality
dq_results = DataQualityFramework().validate(df)

# Treinar modelo
model = FraudDetectionModel().train(df)

# Salvar resultados
model.save("abfss://models@datalake.dfs.core.windows.net/fraud_model")