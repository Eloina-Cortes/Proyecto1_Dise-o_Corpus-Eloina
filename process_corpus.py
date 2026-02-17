import json
from collections import Counter
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np

# Descargar recursos NLTK necesarios
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

SPANISH_STOP = set(stopwords.words("spanish"))

# Stopwords adicionales específicos del dominio (opcional)
DOMAIN_STOP = {"ciudad", "país", "clima", "temperatura", "humedad"}
ALL_STOP = SPANISH_STOP | DOMAIN_STOP

def load_jsonl(path):
    """Carga corpus en formato JSONL."""
    docs = []
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: línea {line_num} inválida: {e}")
    return docs

def basic_stats(docs):

    if not docs:
        return {"n_docs": 0}
    
    lengths = [len(d["text"].split()) for d in docs]
    return {
        "n_docs": len(docs),
        "total_words": sum(lengths),
        "min_len": min(lengths),
        "max_len": max(lengths),
        "mean_len": np.mean(lengths),
        "median_len": np.median(lengths),
        "std_len": np.std(lengths)
    }

def tokenize(text):
    tokens = [t.lower() for t in word_tokenize(text, language="spanish") 
              if t.isalpha()]
    return tokens

def top_k_tokens(docs, k=20, remove_stop=True, remove_high_freq=False, high_freq_threshold=None):

    ctr = Counter()
    for d in docs:
        toks = tokenize(d["text"])
        if remove_stop:
            toks = [t for t in toks if t not in ALL_STOP]
        ctr.update(toks)
    
    if remove_high_freq and high_freq_threshold is not None:
        # Calcula percentil y filtra
        freqs = sorted(ctr.values())
        threshold_val = np.percentile(freqs, high_freq_threshold)
        ctr = Counter({token: count for token, count in ctr.items() 
                      if count <= threshold_val})
    
    return ctr.most_common(k)

def make_wordcloud(docs, path_out="outputs/wordcloud.png", 
                   remove_stop=True, remove_high_freq=False, 
                   high_freq_threshold=95):
    """
    Genera nube de palabras a partir del corpus.
    
    Args:
        docs: Lista de documentos
        path_out: Ruta de salida para la imagen
        remove_stop: Elimina stopwords
        remove_high_freq: Elimina términos de muy alta frecuencia
        high_freq_threshold: Percentil para remover términos frecuentes
    """
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    
    all_text = " ".join(d["text"] for d in docs)
    toks = tokenize(all_text)
    if remove_stop:
        toks = [t for t in toks if t not in ALL_STOP]
    
    if remove_high_freq:
        ctr = Counter(toks)
        threshold_val = np.percentile(list(ctr.values()), high_freq_threshold)
        toks = [t for t in toks if ctr[t] <= threshold_val]
    
    freq_text = " ".join(toks)
    
    wc = WordCloud(width=800, height=400, 
                   background_color="white",
                   colormap="viridis",
                   max_words=100).generate(freq_text)
    
    wc.to_file(path_out)
    return path_out

def generate_report(docs, output_dir="outputs"):
    """Genera reporte completo con estadísticas y visualizaciones."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("ANÁLISIS EXPLORATORIO DE CORPUS (EDA)")
    print("="*60)
    
    # Estadísticas básicas
    print("\n1. ESTADÍSTICAS BÁSICAS")
    print("-" * 60)
    stats = basic_stats(docs)
    for key, val in stats.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.2f}")
        else:
            print(f"  {key}: {val}")
    
    # Top-k sin filtrado
    print("\n2. TOP-20 TOKENS (sin stopwords ni filtrado)")
    print("-" * 60)
    top_all = top_k_tokens(docs, k=20, remove_stop=True)
    for i, (token, freq) in enumerate(top_all, 1):
        print(f"  {i:2d}. {token:20s} -> {freq:5d} ocurrencias")
    
    # Top-k sin stopwords y puntuación
    print("\n3. TOP-20 TOKENS (sin stopwords, sin términos de alta frecuencia)")
    print("-" * 60)
    top_filtered = top_k_tokens(docs, k=20, remove_stop=True, 
                               remove_high_freq=True, high_freq_threshold=90)
    for i, (token, freq) in enumerate(top_filtered, 1):
        print(f"  {i:2d}. {token:20s} -> {freq:5d} ocurrencias")
    
    # Generar nubes de palabras
    print("\n4. GENERANDO NUBES DE PALABRAS")
    print("-" * 60)
    
    # Nube 1: Con stopwords
    path1 = os.path.join(output_dir, "wordcloud_sin_filtrado.png")
    make_wordcloud(docs, path1, remove_stop=False, remove_high_freq=False)
    print(f"  ✓ Nube sin filtrado: {path1}")
    
    # Nube 2: Sin stopwords
    path2 = os.path.join(output_dir, "wordcloud_sin_stopwords.png")
    make_wordcloud(docs, path2, remove_stop=True, remove_high_freq=False)
    print(f"  ✓ Nube sin stopwords: {path2}")
    
    # Nube 3: Sin stopwords y sin términos frecuentes
    path3 = os.path.join(output_dir, "wordcloud_filtrado.png")
    make_wordcloud(docs, path3, remove_stop=True, 
                  remove_high_freq=True, high_freq_threshold=90)
    print(f"  ✓ Nube filtrada (sin stopwords ni top 10%): {path3}")
    
    print("\n" + "="*60)
    print("✓ EDA completado exitosamente")
    print("="*60)

if __name__ == "__main__":
    corpus_path = "data/corpus_weather.jsonl"
    
    print(f"Cargando corpus: {corpus_path}")
    docs = load_jsonl(corpus_path)
    print(f"✓ {len(docs)} documentos cargados\n")
    
    generate_report(docs)
