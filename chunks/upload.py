import os
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

client = QdrantClient(url="http://localhost:6333")
# Изменение 1: Загружаем модель e5
model = SentenceTransformer('intfloat/multilingual-e5-base')
collection_name = "cardiology"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        # Изменение 2: Меняем размерность вектора
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

folder_name = "result"
points = []

for i, filename in enumerate(os.listdir(folder_name)):
    if filename.endswith(".json"):
        with open(os.path.join(folder_name, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Изменение 3: Добавляем префикс
            text_to_encode = f"passage: {data['clean_text']}"
            vector = model.encode(text_to_encode).tolist()

            points.append(PointStruct(
                id=i,
                vector=vector,
                payload=data
            ))

client.upsert(collection_name=collection_name, points=points)
print(f"✅ Успешно загружено {len(points)} чанков в Qdrant!")