# Operações no Data Lake
from azure.storage.filedatalake import DataLakeServiceClient

service_client = DataLakeServiceClient(
    account_url="https://{}.dfs.core.windows.net".format(storage_account),
    credential=credential
)

# Criar estrutura de diretórios
file_system_client = service_client.create_file_system("processed")
directory_client = file_system_client.create_directory("transactions")