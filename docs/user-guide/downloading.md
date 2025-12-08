# Managing Downloads

Nodo helps you track and manage your torrent downloads with a simple command-line interface.

## Adding Downloads

### From Magnet Link

Add a download using a magnet link:

```bash
nodo add magnet:?xt=urn:btih:...
```

### With Custom Title

Specify a custom title for the download:

```bash
nodo add magnet:?xt=urn:btih:... --title "My Download"
```

### To Custom Path

Download to a specific directory:

```bash
nodo add magnet:?xt=urn:btih:... --path ~/Downloads/Custom
```

## Listing Downloads

### List All Downloads

View all tracked downloads:

```bash
nodo list
```

### Filter by Status

List downloads by status:

```bash
# Active downloads
nodo list --status downloading

# Completed downloads
nodo list --status completed

# Paused downloads
nodo list --status paused

# Failed downloads
nodo list --status failed
```

### Detailed View

Show detailed information:

```bash
nodo list --detailed
```

## Checking Status

Get detailed information about a specific download:

```bash
nodo status <download-id>
```

The status shows:
- Current progress percentage
- Download speed
- Upload speed
- Estimated time remaining (ETA)
- File path
- Size and completion status

## Pausing Downloads

Pause an active download:

```bash
nodo pause <download-id>
```

Pause multiple downloads:

```bash
nodo pause <id1> <id2> <id3>
```

## Resuming Downloads

Resume a paused download:

```bash
nodo resume <download-id>
```

Resume multiple downloads:

```bash
nodo resume <id1> <id2> <id3>
```

## Removing Downloads

### Remove from Tracking

Remove a download from Nodo's tracking (keeps files):

```bash
nodo remove <download-id>
```

### Remove and Delete Files

Remove from tracking and delete downloaded files:

```bash
nodo remove <download-id> --delete-files
```

**Warning**: This permanently deletes the files!

### Remove Multiple Downloads

```bash
nodo remove <id1> <id2> <id3>
```

## Download Statuses

Downloads can be in one of these states:

- **DOWNLOADING** - Currently downloading
- **COMPLETED** - Download finished successfully
- **PAUSED** - Download paused by user
- **FAILED** - Download failed (check logs for details)

## Auto-Start Downloads

By default, downloads start automatically when added. You can disable this:

```bash
nodo config --auto-start false
```

When disabled, you'll need to manually start downloads:

```bash
nodo resume <download-id>
```

## Concurrent Downloads

Control how many downloads run simultaneously:

```bash
# Set max concurrent downloads
nodo config --max-concurrent 5
```

Nodo will automatically pause new downloads if the limit is reached.

## Monitoring Progress

### Real-time Updates

Watch download progress in real-time:

```bash
nodo status <download-id> --watch
```

### Refresh All Downloads

Sync all downloads with the torrent client:

```bash
nodo refresh
```

This updates status, progress, and completion times for all downloads.

## Tips

1. **Use descriptive titles** - Makes it easier to identify downloads later
2. **Monitor disk space** - Ensure you have enough space before adding downloads
3. **Check seeders** - Downloads with more seeders complete faster
4. **Organize by path** - Use different paths for different types of content
5. **Regular refresh** - Run `nodo refresh` periodically to sync status

## Troubleshooting

### Download Not Starting

- Check qBittorrent is running
- Verify qBittorrent connection settings
- Check if auto-start is enabled
- Manually resume the download

### Download Stuck

- Check internet connection
- Verify torrent has seeders
- Try pausing and resuming
- Check qBittorrent for errors

### Status Not Updating

- Run `nodo refresh` to sync with torrent client
- Check qBittorrent connection
- Verify download ID is correct

## Next Steps

- [Searching](searching.md) - Learn how to search for torrents
- [Preferences](preferences.md) - Configure download settings

