from openai import OpenAI
import openai
import json
from scipy.spatial import distance
from utils.utils import print_indented
from google import genai
from pandas import isna

MODEL = "gemini-embedding-001"

# Price of gemini-embedding-001: $0.15 / 1M tokens = $0.00015 / 1k tokens
COST_PER_1K_TOKENS = 0.00015

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
            
def create_movie_text(movie):
    return f"""
    Title: {movie['title']}
    Description: {movie['description']}
    Categories: {movie['listed_in']}
    """
            
def count_tokens(api_key, texts, model=MODEL):
    if isinstance(texts, str):
        texts = [texts]

    genai_client = genai.Client(api_key=api_key)
    total = 0
    for text in texts:
        result = genai_client.models.count_tokens(model=model, contents=text)
        total += result.total_tokens
    return total


def estimate_cost(api_key, texts, model=MODEL, cost_per_1k_tokens=COST_PER_1K_TOKENS):
    total_tokens = count_tokens(api_key, texts, model=model)
    cost = cost_per_1k_tokens * total_tokens / 1000
    return {"total_tokens": total_tokens, "cost_usd": cost}

def create_movie_metadatas(movies):
    metadatas = []
    for movie in movies:
        # Chroma solo acepta str/int/float/bool: los NaN de pandas se omiten
        # (country viene vacio en varias filas) y release_year se castea
        # porque pandas lo entrega como numpy.int64.
        metadata = {}
        for key in ["type", "title", "release_year", "rating", "duration", "country"]:
            value = movie.get(key)
            if value is None or isna(value):
                continue
            metadata[key] = int(value) if key == "release_year" else str(value)
        metadatas.append(metadata)
    return metadatas

