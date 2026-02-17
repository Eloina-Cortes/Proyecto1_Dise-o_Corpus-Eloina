import os
import json
import requests
from typing import Dict, List
from datetime import datetime

import os
import json
import requests
from typing import Dict, List
from datetime import datetime

# Open-Meteo API (GRATUITO, sin API key requerida)
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Ciudades y coordenadas de Oaxaca, México
OAXACA_CITIES = {
    "Oaxaca de Juárez": {"lat": 17.0627, "lon": -96.7236, "region": "Región Central"},
    "Tehuantepec": {"lat": 16.3486, "lon": -95.2621, "region": "Istmo de Tehuantepec"},
    "Puerto Escondido": {"lat": 15.8537, "lon": -97.0731, "region": "Costa"},
    "Huajuapan de León": {"lat": 17.8000, "lon": -97.7833, "region": "Región Mixteca"},
    "Ixtlán de Juárez": {"lat": 17.3128, "lon": -96.4586, "region": "Sierra Norte"},
    "Miahuatlán de Porfirio Díaz": {"lat": 16.3658, "lon": -96.5847, "region": "Región Centro"},
    "Teotitlán de Flores Magón": {"lat": 17.3458, "lon": -96.3789, "region": "Sierra Norte"},
    "San Juan Bautista Tuxtepec": {"lat": 18.1548, "lon": -96.1245, "region": "Papaloapan"}
}

def fetch_historical_data(lat: float, lon: float, start_date: str, end_date: str) -> Dict:
    """
    Extrae datos históricos DIARIOS desde Open-Meteo API 
    
    Args:
        lat: Latitud de la ubicación
        lon: Longitud de la ubicación
        start_date: Fecha inicio (formato: YYYY-MM-DD)
        end_date: Fecha fin (formato: YYYY-MM-DD)
    
    Returns:
        Dict con respuesta de la API
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "temperature_unit": "celsius",
        "timezone": "America/Mexico_City"
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def record_from_response(city_name: str, region: str, lat: float, lon: float, date_str: str, daily_data: Dict, index: int) -> Dict:
    """
    Construye un documento textual a partir de datos históricos diarios.
    
    Unidad documental: Cada día de observación en cada ciudad = 1 documento.
    Texto: Descripción narrativa de las condiciones climáticas del día.
    """
    temp_max = daily_data["temperature_2m_max"][index]
    temp_min = daily_data["temperature_2m_min"][index]
    precipitation = daily_data["precipitation_sum"][index]
    wind_speed = daily_data["windspeed_10m_max"][index]
    
    # Descripción narrativa del día climático
    weather_desc = ""
    if precipitation > 0:
        if precipitation > 50:
            weather_desc = f"Día con precipitaciones abundantes, {precipitation:.1f} mm de lluvia. "
        elif precipitation > 10:
            weather_desc = f"Día lluvioso con {precipitation:.1f} mm de precipitación. "
        else:
            weather_desc = f"Día con ligeras precipitaciones de {precipitation:.1f} mm. "
    else:
        weather_desc = "Día sin lluvia. "
    
    if temp_max > 35:
        weather_desc += "Día extremadamente caluroso. "
    elif temp_max > 30:
        weather_desc += "Día muy caluroso. "
    elif temp_max > 25:
        weather_desc += "Día cálido. "
    elif temp_max > 20:
        weather_desc += "Día templado. "
    else:
        weather_desc += "Día fresco. "
    
    if wind_speed > 25:
        weather_desc += "Vientos muy fuertes."
    elif wind_speed > 15:
        weather_desc += "Vientos fuertes."
    elif wind_speed > 10:
        weather_desc += "Vientos moderados."
    else:
        weather_desc += "Vientos ligeros."
    
    # Texto completo descriptivo en español
    text = " ".join(filter(None, [
        f"{city_name}, {region}, Oaxaca, México - Fecha: {date_str}.",
        f"Condiciones: Temperatura máxima {temp_max}°C, mínima {temp_min}°C.",
        f"Precipitación acumulada: {precipitation} mm.",
        f"Velocidad máxima del viento: {wind_speed} km/h.",
        weather_desc
    ]))
    
    return {
        "id": f"{city_name.lower().replace(' ', '_')}_{date_str}",
        "city": city_name,
        "region": region,
        "state": "Oaxaca",
        "country": "México",
        "date": date_str,
        "text": text,
        "metadata": {
            "temp_max_celsius": round(temp_max, 2),
            "temp_min_celsius": round(temp_min, 2),
            "precipitation_mm": round(precipitation, 2),
            "wind_speed_kmh": round(wind_speed, 2),
            "latitude": lat,
            "longitude": lon,
            "region": region
        }
    }

def save_jsonl(docs: List[Dict], path: str):
    """Guarda documentos en formato JSONL (JSON Lines)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    # Parámetros del corpus según especificación del usuario
    start_date = "2025-06-01"  # 01 de junio 2025
    end_date = "2025-12-31"    # 31 de diciembre 2025
    out = "data/corpus_weather.jsonl"
    
    print("\n" + "="*80)
    print("EXTRACCIÓN DE CORPUS: DATOS CLIMÁTICOS HISTÓRICOS DIARIOS - OAXACA MULTIREGIÓN")
    print("="*80)
    print(f"Período: {start_date} a {end_date} (214 días)")
    print(f"Ciudades: {len(OAXACA_CITIES)}")
    for city, info in OAXACA_CITIES.items():
        print(f"  • {city:35s} ({info['region']})")
    print(f"Total documentos esperados: {len(OAXACA_CITIES)} ciudades × 214 días = {len(OAXACA_CITIES) * 214} documentos")
    print(f"API: Open-Meteo (gratuito, sin API key)")
    print(f"Guardando en: {out}")
    print("="*80 + "\n")
    
    try:
        collected = []
        city_count = 0
        
        for city_name, city_info in OAXACA_CITIES.items():
            city_count += 1
            lat = city_info["lat"]
            lon = city_info["lon"]
            region = city_info["region"]
            
            print(f"[{city_count}/{len(OAXACA_CITIES)}] Consultando {city_name:35s} ({region:20s})...", end=" ")
            
            try:
                response = fetch_historical_data(lat, lon, start_date, end_date)
                print("✓ OK")
                
                # Procesar respuesta
                daily_data = response["daily"]
                dates = daily_data["time"]
                total_days = len(dates)
                
                for idx, date_str in enumerate(dates):
                    doc = record_from_response(city_name, region, lat, lon, date_str, daily_data, idx)
                    collected.append(doc)
                
                print(f"           → {total_days} documentos generados para {city_name}")
                
            except Exception as e:
                print(f"✗ Error: {e}")
        
        # Guardar corpus
        save_jsonl(collected, out)
        
        print(f"\n" + "="*80)
        print(f"✓ ÉXITO: Corpus creado exitosamente")
        print(f"   - Documentos generados: {len(collected)}")
        print(f"   - Ruta: {out}")
        print(f"   - Formato: JSONL (JSON Lines)")
        print(f"   - Ciudades: {len(OAXACA_CITIES)}")
        print(f"   - Período: {start_date} a {end_date}")
        print("="*80)
        
        # Mostrar estadísticas básicas
        print("\n▶ ESTADÍSTICAS AGREGADAS DEL CORPUS:")
        temp_max_values = [d["metadata"]["temp_max_celsius"] for d in collected]
        temp_min_values = [d["metadata"]["temp_min_celsius"] for d in collected]
        precip_values = [d["metadata"]["precipitation_mm"] for d in collected]
        
        print(f"  • Total documentos: {len(collected)}")
        print(f"  • Por ciudad: {len(collected) // len(OAXACA_CITIES)} documentos c/u")
        print(f"  • Temperatura máxima: Min={min(temp_max_values):.1f}°C, "
              f"Max={max(temp_max_values):.1f}°C, "
              f"Promedio={sum(temp_max_values)/len(temp_max_values):.1f}°C")
        print(f"  • Temperatura mínima: Min={min(temp_min_values):.1f}°C, "
              f"Max={max(temp_min_values):.1f}°C, "
              f"Promedio={sum(temp_min_values)/len(temp_min_values):.1f}°C")
        print(f"  • Días con lluvia: {sum(1 for p in precip_values if p > 0)} de {len(precip_values)}")
        print(f"  • Precipitación total: {sum(precip_values):.1f} mm")
        
        # Mostrar ejemplo de documento
        print(f"\n▶ EJEMPLO DE DOCUMENTO:")
        print("-" * 80)
        example = collected[0]
        print(f"ID: {example['id']}")
        print(f"Ciudad: {example['city']} ({example['region']})")
        print(f"Fecha: {example['date']}")
        print(f"Texto:\n{example['text']}\n")
        print(f"Metadatos:")
        for key, val in example['metadata'].items():
            if key not in ['latitude', 'longitude']:
                print(f"  - {key}: {val}")
        print("-" * 80 + "\n")
        
    except Exception as e:
        print(f"✗ Error durante la extracción: {e}")
        import traceback
        traceback.print_exc()
