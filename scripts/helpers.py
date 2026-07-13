from openai import OpenAI
import openai
import json
from scipy.spatial import distance
from utils.utils import print_indented

MODEL = "gemini-embedding-001"

def read_products():
    with open("products.json", 'r', encoding='utf-8') as f:
        return json.loads(f.read())
    
def create_product_text(product):
    return f"""
    Title: {product['title']}
    Description: {product['short_description']}
    Category: {product['category']}
    Features: {', '.join(product['features'])}
    """

# Sorting by similarity
def find_n_closest(query_vector, embeddings, n=3):
    distances = []
    for index, embedding in enumerate(embeddings):
        dist = distance.cosine(query_vector, embedding)
        distances.append({'distance': dist, 'index': index})
        
    distances_sorted = sorted(distances, key=lambda x: x['distance'])
    return distances_sorted[0:n]
    
class EmbeddingClient:
    def __init__(self, api_key, base_url, model=MODEL):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def create_embeddings(self, texts):
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            response_dict = response.to_dict()
            return [item["embedding"] for item in response_dict["data"]]
        except openai.RateLimitError as e:
            print_indented(e.response.json())
        except openai.NotFoundError as e:
            print_indented(e.response.json())
        except TypeError as e:
            print(e)
        except AttributeError as e:
            print(e)