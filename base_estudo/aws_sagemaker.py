# Amazon SageMaker
import sagemaker
from sagemaker.sklearn.estimator import SKLearn

estimator = SKLearn(
    entry_point='train.py',
    role=sagemaker.get_execution_role(),
    instance_count=1,
    instance_type='ml.m5.xlarge',
    framework_version='0.23-1'
)

estimator.fit({'train': 's3://bucket/train', 'test': 's3://bucket/test'})