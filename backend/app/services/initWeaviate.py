import weaviate, json

client = weaviate.connect_to_local()

client.is_ready()