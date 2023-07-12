import requests

response = requests.get('https://mega.nz/file/lUhA0LYI#eb5f2QCHiC5KECB47gtMvEaJ_GFYAgNk3b-y8Dak0sw')
open("anime.mp4", "wb").write(response.content)
print("lest see")