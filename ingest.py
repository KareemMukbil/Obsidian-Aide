import os
import json
import pickle
from pathlib import Path
import re
import tiktoken
import numpy as np
import faiss
from typing import List
import markdown
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

class ObsidianVaultIngester:
    def __init__(self, vault_path: str, index_path: str = "./index/"):
        self.vault_path = Path(vault_path)
        self.index_path = Path(index_path)
        self.index_path.mkdir(exist_ok=True)
        
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.chunks = []
        self.chunk_metadata = []
    
    def _clean_markdown(self, content: str) -> str:
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= 500:
            return [text]
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for word in text.split():
            word_tokens = self.tokenizer.encode(word)
            if current_tokens + len(word_tokens) > 500 and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_tokens = len(word_tokens)
            else:
                current_chunk.append(word)
                current_tokens += len(word_tokens)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _load_markdown_files(self) -> List[Tuple[str, str]]:
        files = []
        for md_file in self.vault_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                rel_path = md_file.relative_to(self.vault_path)
                files.append((str(rel_path), content))
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        return files
    
    def process_vault(self):
        print(f"Processing vault: {self.vault_path}")
        files = self._load_markdown_files()
        print(f"Found {len(files)} markdown files")
        
        for file_path, content in files:
            cleaned_content = self._clean_markdown(content)
            if not cleaned_content.strip():
                continue
            
            chunks = self._chunk_text(cleaned_content)
            for i, chunk in enumerate(chunks):
                self.chunks.append(chunk)
                self.chunk_metadata.append({
                    'file_path': file_path,
                    'chunk_id': i,
                    'chunk_count': len(chunks)
                })
        
        print(f"Created {len(self.chunks)} chunks")
    
    def build_index(self):
        if not self.chunks:
            raise ValueError("No chunks to index")
        
        embeddings = []
        for i, chunk in enumerate(self.chunks):
            if i % 100 == 0:
                print(f"Embedding chunk {i+1}/{len(self.chunks)}")
            embeddings.append(self.embedding_model.encode(chunk))
        
        embeddings = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings)
        
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        print(f"Built FAISS index with {index.ntotal} vectors")
        
        self._save_index(index)
    
    def _save_index(self, index):
        faiss.write_index(index, str(self.index_path / "faiss_index.bin"))
        with open(self.index_path / "chunks.pkl", 'wb') as f:
            pickle.dump(self.chunks, f)
        with open(self.index_path / "metadata.pkl", 'wb') as f:
            pickle.dump(self.chunk_metadata, f)
        
        config = {
            'embedding_dim': self.embedding_dim,
            'vault_path': str(self.vault_path),
            'chunk_count': len(self.chunks)
        }
        with open(self.index_path / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Index saved to {self.index_path}")

if __name__ == "__main__":
    VAULT_PATH = r"D:\FILES\Notes\Obsidian\My Life"
    
    if not os.path.exists(VAULT_PATH):
        print(f"Error: Vault path doesn't exist\n{VAULT_PATH}")
        print("Please update the path in ingest.py")
        exit(1)
    
    ingester = ObsidianVaultIngester(VAULT_PATH)
    ingester.process_vault()
    ingester.build_index()
    print("Ingestion complete! You can now start the server.")