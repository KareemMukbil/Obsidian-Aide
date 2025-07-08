from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pickle
from pathlib import Path
import numpy as np
import faiss
import requests
import tiktoken

app = Flask(__name__)
CORS(app)
tokenizer = tiktoken.get_encoding("cl100k_base")

class ObsidianChatAssistant:
    def __init__(self, index_path: str = "./index/"):
        self.index_path = Path(index_path)
        with open(self.index_path / "config.json", 'r') as f:
            self.config = json.load(f)
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.read_index(str(self.index_path / "faiss_index.bin"))
        
        with open(self.index_path / "chunks.pkl", 'rb') as f:
            self.chunks = pickle.load(f)
        with open(self.index_path / "metadata.pkl", 'rb') as f:
            self.metadata = pickle.load(f)
        
        print(f"Loaded {len(self.chunks)} chunks. System ready!")
    
    def retrieve(self, query: str, k: int = 5, folder_filter: str = None):
        embedding = self.embedding_model.encode([query])[0]
        embedding /= np.linalg.norm(embedding)
        distances, indices = self.index.search(embedding.reshape(1, -1).astype('float32'), k * 5)

        retrieved = []
        for idx in indices[0]:
            if idx == -1: 
                continue
            meta = self.metadata[idx]
            if folder_filter and folder_filter.lower() not in meta['file_path'].lower():
                continue
            retrieved.append((self.chunks[idx], meta))
            if len(retrieved) >= k:
                break
        return retrieved
    
    def generate_prompt(self, query: str, context_chunks, folder: str = None):
        system = (
            "System: You are an AI assistant for an Obsidian vault. "
            "Use only the context below. Use Obsidian links ([[...]]). Be detailed and useful.\n\n"
        )
        if folder:
            system += f"Context from folder: {folder}\n\n"
        
        for chunk, meta in context_chunks:
            system += f"From {meta['file_path']}:\n{chunk}\n\n"
        
        system += f"User: {query}\n"
        return system
    
    def generate_response(self, prompt: str):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral:instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "num_predict": 2048,
                        "num_gpu": 80,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=300
            )
            return response.json()["response"].strip()
        except Exception as e:
            return f"Error: {str(e)}"

assistant = ObsidianChatAssistant()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    
    try:
        user_prompt = data['prompt']
        folder = data.get('folder')
        context_chunks = assistant.retrieve(user_prompt, folder_filter=folder)
        full_prompt = assistant.generate_prompt(user_prompt, context_chunks, folder)
        response = assistant.generate_response(full_prompt)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "chunks": len(assistant.chunks)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)