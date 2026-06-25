import torch
from sentence_transformers import InputExample, SentenceTransformer, losses, util

def retrieve_websites(query, top_n=5):
    model = SentenceTransformer("fine_tuned_model", device='cpu')
    website_embeddings = torch.load("website_embeddings.pt", map_location=torch.device('cpu'))
    query_embedding = model.encode(query, convert_to_tensor=True, device='cpu')
    
    similarities = {}
    for url, embedding in website_embeddings.items():
        embedding = embedding.to('cpu')
        similarity = util.pytorch_cos_sim(query_embedding, embedding).item()
        similarities[url] = similarity
        
    similar_sites = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_n = similar_sites[:top_n]
    top_websites = [url for url, similarity in top_n]
    
    print(top_websites)
    return top_websites




retrieve_websites("blue shoes for jogging", 10)
retrieve_websites("water-proof jacket for hiking", 10)
retrieve_websites("leather boots for winter", 10)
retrieve_websites("lightweight summer dresses", 10)
retrieve_websites("athletic leggings for yoga", 10)
retrieve_websites("men's casual shirts for travel", 10)
retrieve_websites("eco-friendly cotton t-shirts", 10)
retrieve_websites("women's hiking boots", 10)
retrieve_websites("sustainable denim jeans", 10)
retrieve_websites("vintage leather jackets", 10)
retrieve_websites("raincoat for outdoor activities", 10)
retrieve_websites("comfortable sneakers for walking", 10)
retrieve_websites("knit sweaters for cold weather", 10)
retrieve_websites("thermal wear for skiing", 10)
retrieve_websites("fashionable boots for autumn", 10)
retrieve_websites("warm wool scarves", 10)
retrieve_websites("organic cotton loungewear", 10)
retrieve_websites("swimwear for summer vacation", 10)
retrieve_websites("high-waisted pants for casual wear", 10)
retrieve_websites("soft wool sweaters for winter", 10)