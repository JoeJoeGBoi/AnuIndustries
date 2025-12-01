# AnuIndustries

Anubith Industries Discord Bot

## Apple Music downloader example

The `scripts/download_apple_music.py` module shows how to use the
[`gamdl`](https://github.com/skeithryan/gamdl) library to download Apple
Music content. To run the example you need to install `gamdl` and provide
an authenticated Netscape-format `cookies.txt` file.

```bash
pip install gamdl

# Pass a custom cookies file path (recommended on Windows where your downloads
# folder might include spaces):
python scripts/download_apple_music.py --cookies "E:/Downloads/apple-music-cookies.txt"

# Or set the APPLE_MUSIC_COOKIES environment variable once per shell session:
# PowerShell
$env:APPLE_MUSIC_COOKIES="E:/Downloads/apple-music-cookies.txt"
# CMD
set APPLE_MUSIC_COOKIES=E:\\Downloads\\apple-music-cookies.txt
# WSL/Linux/macOS
export APPLE_MUSIC_COOKIES=/home/user/Downloads/apple-music-cookies.txt

# You can also target a different Apple Music URL with --url
python scripts/download_apple_music.py --url "https://music.apple.com/your-track"
```
