# Application Insights
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module

# Criar métricas
fraud_measure = measure_module.MeasureInt(
    "fraud_transactions_count",
    "Number of fraudulent transactions",
    "count"
)

fraud_view = view_module.View(
    "fraud_transactions_view",
    "Count of fraudulent transactions",
    [],
    fraud_measure,
    aggregation_module.CountAggregation()
)

# Exportar para Azure Monitor
exporter = metrics_exporter.new_metrics_exporter(
    connection_string='InstrumentationKey={ikey}'
)