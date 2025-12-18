# Azure ML
from azureml.core import Workspace, Experiment, Environment
from azureml.train.automl import AutoMLConfig

ws = Workspace.from_config()
experiment = Experiment(ws, 'fraud-detection')

automl_config = AutoMLConfig(
    task='classification',
    training_data=train_data,
    label_column_name='is_fraud',
    compute_target='gpu-cluster',
    enable_onnx_compatible_models=True,
    primary_metric='AUC'
)