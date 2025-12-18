# Databricks Notebook: Data Preparation and Data Quality
# Azure Databricks (Equivalente AWS: EMR Notebooks)

# Configuração
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import great_expectations as gx
from datetime import datetime
import pandas as pd

# Inicializar Spark
spark = SparkSession.builder \
    .appName("FraudDetectionDataPrep") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

# 1. CONFIGURAÇÃO DE DATAPREP
class AzureDataPrep:
    """Classe para preparação de dados no Azure"""
    
    def __init__(self, storage_account, container):
        self.storage_account = storage_account
        self.container = container
        self.base_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net"
        
    def read_raw_data(self, file_format="parquet"):
        """Ler dados brutos do Data Lake"""
        raw_path = f"{self.base_path}/raw/transactions"
        
        if file_format == "parquet":
            df = spark.read.parquet(raw_path)
        elif file_format == "csv":
            df = spark.read.csv(raw_path, header=True, inferSchema=True)
        elif file_format == "json":
            df = spark.read.json(raw_path)
        
        print(f"Dados brutos lidos: {df.count()} registros")
        return df
    
    def clean_transactions(self, df):
        """Limpeza básica dos dados"""
        from pyspark.sql.functions import when
        
        cleaned_df = df \
            .dropDuplicates(["transaction_id"]) \
            .fillna({
                "amount": 0,
                "merchant_category": "UNKNOWN",
                "user_country": "UNKNOWN"
            }) \
            .withColumn("amount", 
                when(col("amount") < 0, 0)
                .otherwise(col("amount"))
            ) \
            .withColumn("transaction_date", 
                to_date(col("timestamp"))
            ) \
            .withColumn("transaction_hour", 
                hour(col("timestamp"))
            )
        
        return cleaned_df
    
    def enrich_data(self, df):
        """Enriquecer dados com features adicionais"""
        
        # 1. Features temporais
        df = df \
            .withColumn("is_weekend", 
                when(dayofweek(col("transaction_date")).isin([1, 7]), 1).otherwise(0)
            ) \
            .withColumn("is_night", 
                when((col("transaction_hour") >= 0) & (col("transaction_hour") < 6), 1).otherwise(0)
            ) \
            .withColumn("transaction_month", month(col("transaction_date")))
        
        # 2. Features comportamentais (requer join com histórico)
        user_stats = df.groupBy("user_id").agg(
            avg("amount").alias("user_avg_amount"),
            count("*").alias("user_total_transactions"),
            stddev("amount").alias("user_amount_stddev")
        )
        
        df = df.join(user_stats, "user_id", "left")
        
        # 3. Features de merchant
        merchant_stats = df.groupBy("merchant_id").agg(
            count("*").alias("merchant_transaction_count"),
            avg("amount").alias("merchant_avg_amount")
        )
        
        df = df.join(merchant_stats, "merchant_id", "left")
        
        return df
    
    def save_processed_data(self, df, layer="processed"):
        """Salvar dados processados"""
        processed_path = f"{self.base_path}/{layer}/transactions"
        
        df.write \
            .mode("overwrite") \
            .partitionBy("transaction_date") \
            .parquet(processed_path)
        
        print(f"Dados salvos em: {processed_path}")

# 2. DATA QUALITY COM GREAT EXPECTATIONS
class AzureDataQuality:
    """Framework de Data Quality para Azure"""
    
    def __init__(self, context_root="/dbfs/great_expectations"):
        self.context = gx.get_context(context_root_dir=context_root)
    
    def create_expectation_suite(self, df, suite_name="fraud_transactions"):
        """Criar suite de expectativas"""
        validator = self.context.sources.pyspark.get_validator(
            datasource_name="transactions_datasource",
            data_asset_name="transactions",
            batch_request={
                "dataset": df,
                "data_asset_name": "transactions"
            }
        )
        
        # Expectativas para schema
        validator.expect_column_to_exist("transaction_id")
        validator.expect_column_to_exist("user_id")
        validator.expect_column_to_exist("amount")
        validator.expect_column_to_exist("timestamp")
        
        # Expectativas para valores
        validator.expect_column_values_to_be_unique("transaction_id")
        validator.expect_column_values_to_not_be_null("amount")
        validator.expect_column_values_to_be_between(
            "amount", 
            min_value=0, 
            max_value=1000000
        )
        validator.expect_column_values_to_be_in_set(
            "currency",
            ["BRL", "USD", "EUR", "GBP"]
        )
        
        # Expectativas estatísticas
        validator.expect_column_mean_to_be_between(
            "amount",
            min_value=100,
            max_value=5000
        )
        
        # Salvar suite
        validator.save_expectation_suite(discard_failed_expectations=False)
        print(f"Suite de expectativas '{suite_name}' criada")
        
        return validator
    
    def run_data_quality_check(self, df, suite_name="fraud_transactions"):
        """Executar verificações de qualidade"""
        validator = self.create_expectation_suite(df, suite_name)
        
        # Executar validação
        results = validator.validate()
        
        # Gerar relatório
        self.generate_dq_report(results)
        
        return results
    
    def generate_dq_report(self, validation_results):
        """Gerar relatório de Data Quality"""
        report = {
            "validation_time": datetime.now().isoformat(),
            "success": validation_results.success,
            "statistics": {
                "evaluated_expectations": len(validation_results.results),
                "successful_expectations": sum(1 for r in validation_results.results if r.success),
                "unsuccessful_expectations": sum(1 for r in validation_results.results if not r.success),
            },
            "failed_expectations": []
        }
        
        for result in validation_results.results:
            if not result.success:
                report["failed_expectations"].append({
                    "expectation_type": result.expectation_config.expectation_type,
                    "column": result.expectation_config.kwargs.get("column"),
                    "details": result.result
                })
        
        # Salvar relatório no Data Lake
        report_df = spark.createDataFrame([report])
        report_path = f"abfss://reports@{storage_account}.dfs.core.windows.net/dq_reports"
        report_df.write.mode("append").json(report_path)
        
        return report
    
    def create_data_drift_monitor(self, reference_df, current_df):
        """Monitorar drift de dados"""
        from evidently.report import Report
        from evidently.metric_preset import DataDriftPreset
        
        # Converter para pandas para evidently
        reference_pd = reference_df.toPandas().sample(1000)
        current_pd = current_df.toPandas().sample(1000)
        
        # Criar relatório de drift
        drift_report = Report(metrics=[DataDriftPreset()])
        drift_report.run(
            reference_data=reference_pd,
            current_data=current_pd
        )
        
        # Salvar relatório
        drift_report.save_html("/dbfs/mnt/reports/data_drift.html")
        
        return drift_report

# 3. PIPELINE COMPLETO
def run_fraud_data_pipeline():
    """Pipeline completo de preparação de dados"""
    
    # Configurar
    storage_account = dbutils.widgets.get("storage_account")
    container = dbutils.widgets.get("container")
    
    dataprep = AzureDataPrep(storage_account, container)
    dataquality = AzureDataQuality()
    
    # 1. Ler dados brutos
    print("Passo 1: Lendo dados brutos...")
    raw_df = dataprep.read_raw_data("parquet")
    
    # 2. Executar Data Quality
    print("Passo 2: Executando Data Quality...")
    dq_results = dataquality.run_data_quality_check(raw_df)
    
    if not dq_results.success:
        print("⚠️  Alertas de Data Quality encontrados!")
        for failure in dq_results["failed_expectations"]:
            print(f"  - {failure}")
    
    # 3. Limpar dados
    print("Passo 3: Limpando dados...")
    cleaned_df = dataprep.clean_transactions(raw_df)
    
    # 4. Enriquecer dados
    print("Passo 4: Enriquecendo dados...")
    enriched_df = dataprep.enrich_data(cleaned_df)
    
    # 5. Salvar dados processados
    print("Passo 5: Salvando dados processados...")
    dataprep.save_processed_data(enriched_df, "processed")
    
    # 6. Salvar dados curados (para ML)
    print("Passo 6: Preparando dados para ML...")
    ml_df = enriched_df.select(
        "transaction_id",
        "user_id",
        "amount",
        "merchant_category",
        "is_weekend",
        "is_night",
        "user_avg_amount",
        "user_amount_stddev",
        "merchant_transaction_count",
        "is_fraud"
    ).filter(col("is_fraud").isNotNull())
    
    dataprep.save_processed_data(ml_df, "curated")
    
    print("✅ Pipeline de DataPrep concluído!")
    
    return enriched_df

# Executar pipeline
if __name__ == "__main__":
    df = run_fraud_data_pipeline()
    display(df.limit(10))