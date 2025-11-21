import os
import requests
from tqdm import tqdm
from pathlib import Path

LOCAL_CORPUS_FILES = {
    'hungarian': 'data/wikipedia_hu_all_nopic_2024-05.latin.step1',
    'finnish': 'data/wikipedia_fi_all_nopic_2023-05.latin.step1',
    'estonian': 'data/wikipedia_et_all_nopic_2024-05.latin.step1',
}

CORPUS_URLS = {
    'hungarian': 'https://path-to-your-hosted/hungarian_corpus.txt.zip',
    'finnish': 'https://path-to-your-hosted/finnish_corpus.txt.zip',
    'estonian': 'https://path-to-your-hosted/estonian_corpus.txt.zip',
}

CACHE_DIR = Path.home() / '.cache' / 'samponlp'

def get_corpus(language: str) -> str:
    if language in LOCAL_CORPUS_FILES:
        local_path = LOCAL_CORPUS_FILES[language]
        if os.path.exists(local_path):
            print(f"Local corpus used: {local_path}")
            return local_path
        else:
            print(f"Local corpus: {local_path} was not found, trying to download corpus...")
    
    if language not in CORPUS_URLS:
        raise ValueError(f"No built-in corpus is available for the language '{language}'. Please specify the corpus file path manually via `corpus_path` parameter.")
    
    url = CORPUS_URLS[language]
    filename = url.split('/')[-1].replace('.zip', '')
    target_path = CACHE_DIR / filename
    
    if target_path.exists():
        print(f"Using cached corpus: {target_path}")
        return str(target_path)
    
    print(f"No built-in corpus is available for the language '{language}'. Trying to download corpus...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(target_path, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)
            
    print(f"\nCorpus successfully downloaded and saved to: {target_path}")
    return str(target_path)
