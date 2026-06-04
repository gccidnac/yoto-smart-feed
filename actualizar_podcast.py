import os
import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime
import time

def generar_super_feed():
    # 1. Leer las URLs desde el archivo podcasts.txt
    if not os.path.exists("podcasts.txt"):
        print("No se encontró el archivo podcasts.txt. Creando uno vacío.")
        with open("podcasts.txt", "w") as f:
            f.write("")
        return

    with open("podcasts.txt", "r") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    if not urls:
        print("No hay URLs de podcast para procesar.")
        return

    todos_los_episodios = []

    # 2. Escanear cada podcast
    for url in urls:
        print(f"Procesando: {url}")
        try:
            feed = feedparser.parse(url)
            podcast_title = feed.feed.title if hasattr(feed.feed, 'title') else "Podcast"
            
            for entry in feed.entries:
                if not hasattr(entry, 'published_parsed'):
                    continue
                    
                pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                
                # Buscar el archivo de audio (.mp3)
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
            print(f"Error procesando la URL {url}: {e}")

    # 3. Ordenar por fecha (el más reciente primero)
    todos_los_episodios.sort(key=lambda x: x['date'], reverse=True)

    # 4. Construir el nuevo feed RSS formato Podcast
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title('Mi Mix de Podcasts Yoto')
    fg.link(href='https://github.com')
    fg.description('Lista combinada de mis podcasts favoritos para Yoto')
    fg.language('es')

    # Añadir los 15 episodios más recientes en total
    for ep in todos_los_episodios[:15]:
        fe = fg.add_entry()
        fe.title(ep['title'])
        fe.description(ep['description'])
        fe.enclosure(ep['url'], 0, 'audio/mpeg')
        fe.pubDate(ep['date'].astimezone())

    # 5. Guardar el archivo final
    fg.rss_file('yoto-feed.xml', pretty=True)
    print("¡Feed yoto-feed.xml generado con éxito!")

if __name__ == "__main__":
    generar_super_feed()
