# Databricks Notebook
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()
features = fs.create_table(
    name="fraud_features",
    primary_keys=["transaction_id"],
    df=feature_df,
    description="Features para detecção de fraudes"
)