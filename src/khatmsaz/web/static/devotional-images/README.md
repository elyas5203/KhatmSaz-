# Devotional images

Place small, single-image devotional assets in this directory on the server.
The admin panel stores only the filename (for example `laan-omar.jpg`) and the
bot exposes it at `/static/devotional-images/<filename>`.

Allowed formats: JPG, JPEG, PNG, WEBP. Image files are intentionally ignored
by Git so production media is not committed accidentally.
