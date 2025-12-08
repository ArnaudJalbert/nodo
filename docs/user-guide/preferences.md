# User Preferences

Nodo stores your preferences in `~/.config/nodo/config.toml`. You can configure download paths, aggregator preferences, and other settings.

## Viewing Preferences

View your current preferences:

```bash
nodo config
```

## Download Path

Set the default download directory:

```bash
nodo config --download-path ~/Downloads
```

Use an absolute path:

```bash
nodo config --download-path /media/external/downloads
```

## Concurrent Downloads

Set the maximum number of simultaneous downloads:

```bash
nodo config --max-concurrent 5
```

Default is 3. Higher values may impact download speeds.

## Auto-Start Downloads

Control whether downloads start automatically:

```bash
# Enable auto-start (default)
nodo config --auto-start true

# Disable auto-start
nodo config --auto-start false
```

When disabled, you must manually start downloads with `nodo resume`.

## Favorite Download Paths

Add favorite download locations for quick access:

```bash
# Add a favorite path
nodo config --add-favorite-path ~/Downloads/Movies
nodo config --add-favorite-path ~/Downloads/Software

# List favorite paths
nodo config --list-favorite-paths

# Remove a favorite path
nodo config --remove-favorite-path ~/Downloads/Movies
```

When adding downloads, you can quickly select from favorite paths.

## Favorite Aggregators

Set preferred aggregator sources:

```bash
# Add favorite aggregators
nodo config --add-favorite-aggregator 1337x
nodo config --add-favorite-aggregator thepiratebay

# List favorite aggregators
nodo config --list-favorite-aggregators

# Remove a favorite aggregator
nodo config --remove-favorite-aggregator 1337x
```

Favorite aggregators are searched first and prioritized in results.

## qBittorrent Settings

Configure qBittorrent connection:

```bash
# Set qBittorrent Web UI URL
nodo config --qbittorrent-url http://localhost:8080

# Set credentials
nodo config --qbittorrent-username admin
nodo config --qbittorrent-password yourpassword
```

## Database Path

Set custom database location:

```bash
nodo config --database-path ~/.local/share/nodo/database.db
```

Default is `~/.local/share/nodo/database.db`.

## Configuration File

You can also edit the configuration file directly:

```bash
# Open config file in default editor
nodo config --edit
```

Or manually edit `~/.config/nodo/config.toml`:

```toml
[downloads]
path = "~/Downloads"
max_concurrent = 3
auto_start = true

[favorites]
paths = [
    "~/Downloads/Movies",
    "~/Downloads/Software"
]
aggregators = ["1337x", "thepiratebay"]

[qbittorrent]
url = "http://localhost:8080"
username = "admin"
password = "yourpassword"

[database]
path = "~/.local/share/nodo/database.db"
```

## Resetting Preferences

Reset to default preferences:

```bash
nodo config --reset
```

**Warning**: This will delete your current configuration!

## Environment Variables

Some settings can be overridden with environment variables:

```bash
# Override download path
export NODO_DOWNLOAD_PATH=~/CustomDownloads

# Override qBittorrent URL
export NODO_QBITTORRENT_URL=http://192.168.1.100:8080
```

Environment variables take precedence over configuration file settings.

## Tips

1. **Use absolute paths** - More reliable than relative paths
2. **Organize favorites** - Add commonly used paths and aggregators
3. **Secure credentials** - Don't commit config files with passwords
4. **Backup config** - Save your config file if you customize heavily

## Next Steps

- [Searching](searching.md) - Use your favorite aggregators
- [Downloading](downloading.md) - Use your favorite download paths

