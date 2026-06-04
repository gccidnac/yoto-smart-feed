<import os
import feedparser
from feedgen.feed import FeedGenerator
from datetime import datetime
import time

FOLDER_PLAYLISTS = "playlists"
FOLDER_OUTPUT = "feeds"

def process_playlist_file(filepath):
    urls = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_clean = line.strip()
            # Ignore empty lines and lines starting with # (comments)
            if not line_clean or line_clean.startswith("#"):
                continue
            urls.append(line_clean)
    return urls

def generate_feeds():
    if not os.path.exists(FOLDER_PLAYLISTS):
        print(f"Playlist folder '{FOLDER_PLAYLISTS}' not found. Creating it...")
        os.makedirs(FOLDER_PLAYLISTS)
        return

    # Ensure output folder exists
    if not os.path.exists(FOLDER_OUTPUT):
        print(f"Creating output folder '{FOLDER_OUTPUT}'...")
        os.makedirs(FOLDER_OUTPUT)

    # Find all .txt files inside the playlists folder
    files = [f for f in os.listdir(FOLDER_PLAYLISTS) if f.endswith(".txt")]

    if not files:
        print("No .txt files found in the playlists folder.")
        return

    for file in files:
        playlist_name = os.path.splitext(file)[0]
        filepath = os.path.join(FOLDER_PLAYLISTS, file)
        
        print(f"\n--- Processing Playlist: {playlist_name.upper()} ---")
        urls = process_playlist_file(filepath)
        
        if not urls:
            print(f"Playlist '{playlist_name}' is empty or only contains comments.")
            continue

        all_episodes = []

        for url in urls:
            print(f"  Reading feed: {url}")
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
                        all_episodes.append({
                            'title': f"[{podcast_title}] {entry.title}",
                            'description': getattr(entry, 'summary', ''),
                            'url': enclosure_url,
                            'date': pub_date
                        })
            except Exception as e:
                print(f"  Error reading {url}: {e}")

        if not all_episodes:
            print(f"  No valid audio episodes found for '{playlist_name}'.")
            continue

        # Sort episodes by publication date (newest first)
        all_episodes.sort(key=lambda x: x['date'], reverse=True)

        # Build the specific RSS feed for this playlist
        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title(f"Yoto Mix: {playlist_name.capitalize()}")
        fg.link(href='https://github.com')
        fg.description(f"Combined playlist for Yoto Player generated from {file}")
        fg.language('en')

        # Save the 15 most recent episodes
        for ep in all_episodes[:15]:
            fe = fg.add_entry()
            fe.title(ep['title'])
            fe.description(ep['description'])
            fe.enclosure(ep['url'], 0, 'audio/mpeg')
            fe.pubDate(ep['date'].astimezone())

        # Output path (e.g., feeds/kids_podcasts-feed.xml)
        output_filename = os.path.join(FOLDER_OUTPUT, f"{playlist_name}-feed.xml")
        fg.rss_file(output_filename, pretty=True)
        print(f"¡Success! Generated file: {output_filename}")

if __name__ == "__main__":
    generate_feeds()
