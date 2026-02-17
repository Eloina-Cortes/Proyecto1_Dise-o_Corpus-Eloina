# Proyecto1_Dise-o_Corpus-Eloina
Se diseño un corpus del clima de 8 ciudades del estado de Oaxaca. 
# Proyecto 1: Corpus Textual de Datos Climáticos de Oaxaca

Objetivo: Construcción de corpus textual desde Open-Meteo API (datos históricos), análisis exploratorio riguroso y evaluación de decisiones metodológicas.

---

## Estructura del Proyecto

```
API_CLIMA/
├── scripts/
│   ├── fetch_openweather.py      # Extracción desde Open-Meteo API
│   └── process_corpus.py         # Procesamiento y EDA
├── data/
│   └── corpus_weather.jsonl      # Corpus en formato JSON Lines (1,712 documentos)
├── outputs/
│   ├── wordcloud_*.png           # Nubes de palabras generadas
│   └── reporte.txt               # Reporte procesado
├── requirements.txt              # Dependencias Python
├── README.md                     # Este archivo
└── respuesta.md                  # Respuestas académicas a lineamientos
```

---

## 🔧 Configuración Inicial

### 1. Crear entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Descargar recursos NLTK (primera vez)
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## Flujo de Ejecución

### Paso 1: Extracción de datos históricos (8 ciudades)
```bash
python scripts/fetch_openweather.py
```

**Salida**: 
- `data/corpus_weather.jsonl` - Corpus multiregión (1,712 documentos: 8 ciudades × 214 días)
- Ejemplo de documentos guardados en consola

**Configuración de extracción**:
- **API**: Open-Meteo Archive API (https://archive-api.open-meteo.com/v1/archive)
- **Ventaja**: Gratuito, sin API key, datos históricos completos
- **Período**: 01 de junio 2025 - 31 de diciembre 2025 (214 días)
- **Ciudades de Oaxaca** (8 regiones):
  1. Oaxaca de Juárez (Región Central)
  2. Tehuantepec (Istmo de Tehuantepec)
  3. Puerto Escondido (Costa)
  4. Huajuapan de León (Región Mixteca)
  5. Ixtlán de Juárez (Sierra Norte)
  6. Miahuatlán de Porfirio Díaz (Región Centro)
  7. Teotitlán de Flores Magón (Sierra Norte)
  8. San Juan Bautista Tuxtepec (Papaloapan)

**Datos extraídos por ciudad y día**:
- Temperatura máxima/mínima
- Precipitación acumulada
- Velocidad máxima del viento

**Decisiones metodológicas**:
- **Unidad documental**: "Observación de clima por ciudad y día"
- **Dominio temático**: Condiciones meteorológicas históricas
- **Tipo de texto**: Descripción narrativa de variables climáticas
- **Idioma**: Español (descripciones automáticas generadas)
- **Formato**: JSONL (JSON Lines - 1 línea por documento)

### Paso 2: Procesamiento y EDA
```bash
python scripts/process_corpus.py
```

**Salida**:
- Estadísticas descriptivas impresas en consola
- Top-20 tokens más frecuentes
- Tres nubes de palabras (PNG):
  1. `wordcloud_sin_filtrado.png` - Con stopwords
  2. `wordcloud_sin_stopwords.png` - Sin stopwords españoles
  3. `wordcloud_filtrado.png` - Sin stopwords ni términos de alta frecuencia

**Análisis incluido**:
- Tokenización con NLTK (multiidioma, robusto)
- Normalización: lowercasing + eliminación no-alfabéticos
- Frecuencias léxicas: 3 variantes (sin filtrado, con stopwords, filtrado)
- Visualización de patrones por región temporal

---

## Dataset del Proyecto

### Composición Actual (DATOS REALES)

| Parámetro | Valor |
|-----------|-------|
| **Total documentos** | 1,712 ✓ |
| **Ciudades** | 8 (multiregión Oaxaca) |
| **Período temporal** | 01/06/2025 - 31/12/2025 |
| **Días cubiertos** | 214 días consecutivos |
| **Documentos por ciudad** | 214 |
| **Total palabras** | 61,816 |
| **Palabras promedio** | 36.11 por documento |
| **Variabilidad** | σ = 1.95 (muy consisten) |
| **Longitud rango** | 32-40 palabras |
| **Variables climáticas** | 4 (T.máx, T.mín, Precipitación, Viento) |
| **Idioma** | Español |
| **Formato** | JSONL (JSON Lines) |
| **Tamaño aprox.** | 500-600 KB |

### Ejemplo de Documento

```json
{
  "id": "oaxaca_de_juárez_2025-06-01",
  "city": "Oaxaca de Juárez",
  "region": "Región Central",
  "state": "Oaxaca",
  "country": "México",
  "date": "2025-06-01",
  "text": "Oaxaca de Juárez, Región Central, Oaxaca, México - Fecha: 2025-06-01. Condiciones: Temperatura máxima 23.9°C, mínima 15.6°C. Precipitación acumulada: 0.8 mm. Velocidad máxima del viento: 7.6 km/h. Día con ligeras precipitaciones de 0.8 mm. Día templado. Vientos ligeros.",
  "metadata": {
    "temp_max_celsius": 23.9,
    "temp_min_celsius": 15.6,
    "precipitation_mm": 0.8,
    "wind_speed_kmh": 7.6,
    "latitude": 17.0627,
    "longitude": -96.7236,
    "region": "Región Central"
  }
}
```

### Estadísticas Climáticas Esperadas

| Métrica | Rango |
|---------|-------|
| **Temperatura máxima** | 23-35°C (varía por región y mes) |
| **Temperatura mínima** | 12-22°C |
| **Precipitación total** | ~1,700-2,100 mm (período completo) |
| **Días con lluvia** | ~72-80% de los 214 días |
| **Velocidad viento** | 5-30 km/h |

### Características por Región

| Región | Característica Climática |
|--------|-------------------------|
| **Costera** (Puerto Escondido, Tehuantepec) | Mayor precipitación, vientos fuertes |
| **Sierra** (Ixtlán, Teotitlán, Miahuatlán) | Temperaturas más frescas, lluvia abundante |
| **Central** (Oaxaca de Juárez) | Templada, datos de referencia |
| **Papaloapan** (Tuxtepec) | Tropical, precipitaciones muy elevadas |
| **Mixteca** (Huajuapan) | Más árida, variabilidad estacional |

---

## 🛠️ Herramientas y Justificación

### API: Open-Meteo

**¿Por qué Open-Meteo?**
- ✓ Gratuito (sin limitaciones de número de peticiones)
- ✓ Sin requiere API key o autenticación
- ✓ Datos históricos completos (no solo actuales)
- ✓ Cobertura global y precisión alta
- ✓ Frecuencia: datos diarios perfectos para análisis temporal
- ✓ Reproducible: cualquiera en cualquier momento puede ejecutar el código

### Procesamiento: NLTK

**¿Por qué NLTK?**
- ✓ Estándar de facto en procesamiento de lenguaje natural
- ✓ Soporte robusto para español
- ✓ Tokenización precisa y confiable
- ✓ Stopwords multiidioma integrados
- ✓ Ampliamente utilizado en literatura académica
- ✓ Bien documentado y mantenido


## Análisis Exploratorio (EDA) - Outputs Esperados

Al ejecutar `process_corpus.py`, verás:

1. **En consola**:
   - Total de documentos procesados
   - Min/máx/promedio de longitud de documentos
   - Top-20 tokens sin stopwords
   - Top-20 tokens sin stopwords ni alta frecuencia

2. **En outputs/**:
   - `wordcloud_sin_filtrado.png` - Todas las palabras (estructura sintáctica dominada por "oaxaca", "méxico")
   - `wordcloud_sin_stopwords.png` - Palabras significativas ("lluvia", "viento", "cálido", "temperatura")
   - `wordcloud_filtrado.png` - Términos discriminativos ("lluvioso", "caluroso", "moderado", "ligero")

---

## Consideraciones Metodológicas Clave

### Decisiones Documentadas

| Aspecto | Decisión | Justificación |
|---------|----------|---------------|
| **API elegida** | Open-Meteo (gratuito, históricos) | Reproducibilidad total, sin dependencias de API keys |
| **Unidad documental** | Un documento por ciudad/día | Permite análisis temporal fino y comparación geográfica |
| **Ciudades** | 8 regiones de Oaxaca | Representa diversidad geográfica (costa, sierra, istmo, central) |
| **Período** | Junio - Diciembre 2025 | Cubre transición estacionales (lluvias → secas) |
| **Variables** | 4 parámetros climáticos | Balance entre información y complejidad |
| **Idioma generado** | Español | Descripciones narrativas naturales |
| **Tokenización** | NLTK word_tokenize | Estándar, robusto, multiidioma |
| **Normalización** | Lowercasing + filtro alfabético | Reduce ruido sin perder significado en dominio técnico |


**Última actualización**: Febrero 2026  
**Estado**: Corpus generado (1,712 documentos) | Análisis pendiente
