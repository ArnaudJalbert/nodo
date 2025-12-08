# Searching for Torrents

Nodo allows you to search for torrents across multiple aggregator sources simultaneously.

## Basic Search

Search for torrents using a simple query:

```bash
nodo search "ubuntu 24.04"
```

This will search across all configured aggregators and display results.

## Search Options

### Limit Results

Limit the number of results per aggregator:

```bash
nodo search "ubuntu" --max-results 5
```

### Filter by Source

Search only specific aggregators:

```bash
nodo search "ubuntu" --source 1337x
nodo search "ubuntu" --source 1337x --source thepiratebay
```

### Sort Results

Sort results by different criteria:

```bash
# Sort by seeders (default)
nodo search "ubuntu" --sort seeders

# Sort by size
nodo search "ubuntu" --sort size

# Sort by date
nodo search "ubuntu" --sort date
```

## Understanding Results

Search results display the following information:

- **Title**: Name of the torrent
- **Size**: File size (e.g., "1.5 GB")
- **Seeders**: Number of seeders (higher is better)
- **Leechers**: Number of leechers
- **Source**: Which aggregator found it
- **Date**: When the torrent was uploaded

## Adding a Download from Search

After searching, you can add a download directly:

```bash
# Search and select by index
nodo search "ubuntu" --add 0

# Or use the magnet link
nodo add magnet:?xt=urn:btih:...
```

## Tips

1. **Use specific queries** - More specific queries yield better results
2. **Check seeders** - Higher seeder counts mean faster downloads
3. **Multiple sources** - Search across multiple aggregators for better coverage
4. **Favorite aggregators** - Configure favorite sources for faster searches

## Troubleshooting

### No Results Found

- Check your internet connection
- Verify aggregator sources are accessible
- Try a different search query
- Check if aggregators are blocked in your region

### Timeout Errors

- Some aggregators may be slow or unavailable
- Try searching fewer sources at once
- Increase timeout settings in configuration

## Next Steps

- [Downloading](downloading.md) - Learn how to manage downloads
- [Preferences](preferences.md) - Configure search and download settings

