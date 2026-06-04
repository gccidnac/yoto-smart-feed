import os
import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime
import time

FOLDER_PLAYLISTS = "playlists"

def procesar_fichero_playlist(filepath):
    urls = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_clean = line.strip()
            if not line_clean or line_clean.startswith("#"):
                continue
            urls.append(line_clean)
    return urls

def generar_feeds():
    if not os.path.exists(FOLDER_PLAYLISTS):
        print(f"No se encontró la carpeta '{FOLDER_PLAYLISTS}'. Creándola...")
        os.makedirs(FOLDER_PLAYLISTS)
        return

    # Buscar todos los archivos .txt dentro de la carpeta playlists
    archivos = [f for f in os.listdir(FOLDER_PLAYLISTS) if f.endswith(".txt")]

    if not archivos:
        print("No se encontraron archivos .txt en la carpeta playlists.")
        return

    for archivo in archivos:
        nombre_playlist = os.path.splitext(archivo)[0] # Ej: "noticias" o "infantil"
        filepath = os.path.join(FOLDER_PLAYLISTS, archivo)
        
        print(f"\n--- Procesando Playlist: {nombre_playlist.upper()} ---")
        urls = procesar_fichero_playlist(filepath)
        
        if not urls:
            print(f"La playlist '{nombre_playlist}' está vacía o solo contiene comentarios.")
            continue

        todos_los_episodios = []

        for url in urls:
            print(f"  Leyendo feed: {url}")
            try:
                feed = feedparser.parse(url)
                podcast_title = feed.feed.title if hasattr(feed.feed, 'title') else "Podcast"
                
                for entry in feed.entries:
                    if not hasattr(entry, 'published_parsed'):
                        continue
                        
                    pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    
                    enclosure_url = ""
                    if hasattr(entry, 'enclosures'):
                        for enc in entry.enclosures:
                            if enc.type.startswith('audio/'):
                                enclosure_url = enc.href
                                break
                    
                    if enclosure_url:
                        todos_los_episodios.append({
                            'title': f"[{podcast_title}] {entry.title}",
                            'description': getattr(entry, 'summary', ''),
                            'url': enclosure_url,
                            'date': pub_date
                        })
            except Exception as e:
                print(f"  Error leyendo {url}: {e}")

        if not todos_los_episodios:
            print(f"  No se encontraron episodios de audio válidos para '{nombre_playlist}'.")
            continue

        # Ordenar episodios de esta playlist por fecha
        todos_los_episodios.sort(key=lambda x: x['date'], reverse=True)

        # Construir el feed RSS específico para esta playlist
        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title(f"Yoto Mix: {nombre_playlist.capitalize()}")
        fg.link(href='https://github.com')
        fg.description(f"Playlist combinada para Yoto generada desde {archivo}")
        fg.language('es')

        # Guardar los 15 más recientes
        for ep in todos_los_episodios[:15]:
            fe = fg.add_entry()
            fe.title(ep['title'])
            fe.description(ep['description'])
            fe.enclosure(ep['url'], 0, 'audio/mpeg')
            fe.pubDate(ep['date'].astimezone())

        # Nombre del archivo de salida (Ej: noticias-feed.xml o infantil-feed.xml)
        output_filename = f"{nombre_playlist}-feed.xml"
        fg.rss_file(output_filename, pretty=True)
        print(f"¡Éxito! Generado el archivo: {output_filename}")

if __name__ == "__main__":
    generar_feeds()
