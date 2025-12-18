# Treinamento com AutoML
from azureml.train.automl import AutoMLConfig

automl_config = AutoMLConfig(
    task='classification',
    primary_metric='AUC',
    training_data=train_data,
    label_column_name='is_fraud',
    iterations=30,
    experiment_timeout_hours=1,
    compute_target='gpu-cluster'
)

# Deploy do modelo
model.deploy(
    workspace=ws,
    name='fraud-detection-endpoint',
    inference_config=inference_config,
    deployment_config=aks_config
)