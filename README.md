# Yoto Smart Feed

Automatically generates combined RSS feeds for the [Yoto Player](https://yotoplay.com) by merging episodes from multiple podcasts into a single playlist. A GitHub Action runs daily and keeps the feeds up to date.

## How it works

1. Each `.txt` file in `playlists/` defines a playlist by listing one podcast RSS feed URL per line.
2. `update_feeds.py` reads every playlist file, fetches all source feeds, collects their episodes, sorts them by date (newest first), and writes the top 15 into a combined RSS file under `feeds/`.
3. The GitHub Action commits the updated XML files back to the repo every day at 6:00 AM UTC.

The generated feed URLs follow this pattern (replace `<repo>` with your GitHub Pages or raw URL):

```
https://raw.githubusercontent.com/gccidnac/yoto-smart-feed/main/feeds/<playlist-name>-feed.xml
```

## Adding a new playlist

1. Create a new `.txt` file in `playlists/` — the filename becomes the playlist name.
2. Add one podcast RSS URL per line. Lines starting with `#` are treated as comments.

```
# playlists/science.txt
https://feeds.example.com/some-science-podcast
https://feeds.example.com/another-podcast
```

3. Push the file. The next scheduled run will generate `feeds/science-feed.xml` automatically.

To run it immediately, go to **Actions → Actualizar Feed Yoto → Run workflow** on GitHub.

## Running locally

```bash
pip install -r requirements.txt
python update_feeds.py
```

The updated XML files will appear in `feeds/`.

## Project structure

```
playlists/          # One .txt file per playlist
feeds/              # Generated RSS feeds (auto-updated by the Action)
update_feeds.py     # Feed generator script
requirements.txt    # Python dependencies (feedparser, feedgen)
.github/workflows/
  cron.yml          # Daily GitHub Action
```

## Using a feed in the Yoto app

1. In the Yoto app, create a new **Make Your Own** card.
2. Select **Podcast / RSS** and paste the raw URL of one of the generated feeds from `feeds/`.
3. The app will load the latest 15 episodes as chapters on the card.
