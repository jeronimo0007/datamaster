# Exemplo: Producer de transações
from azure.eventhub import EventHubProducerClient, EventData

producer = EventHubProducerClient.from_connection_string(
    conn_string="Endpoint=sb://fraud-events.servicebus.windows.net/;SharedAccessKeyName=...",
    eventhub_name="transactions"
)

async def send_transaction(transaction):
    async with producer:
        event_data_batch = await producer.create_batch()
        event_data_batch.add(EventData(json.dumps(transaction)))
        await producer.send_batch(event_data_batch)