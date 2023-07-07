import cloudscraper
import lxml.html as html
import sqlite3
import random

URL = 'https://www3.animeflv.net'

RECENT_EPISODES_IMG = '//ul[@class="ListEpisodios AX Rows A06 C04 D03"]/li/a/span[@class="Image"]/img/@src'
RECENT_EPISODES_LINK = '//ul[@class="ListEpisodios AX Rows A06 C04 D03"]/li/a/@href'
RECENT_EPISODES_NUMBER = '//ul[@class="ListEpisodios AX Rows A06 C04 D03"]/li/a/span[@class="Capi"]/text()'
RECENT_EPISODES_NAME = '//ul[@class="ListEpisodios AX Rows A06 C04 D03"]/li/a/strong[@class="Title"]/text()'

ANIME_LIST_LINK = '//ul[@class="ListAnimes AX Rows A03 C02 D02"]/li/article[@class="Anime alt B"]/a/@href'
ANIME_LIST_NAME = '//ul[@class="ListAnimes AX Rows A03 C02 D02"]/li/article[@class="Anime alt B"]/a/h3[@class="Title"]/text()'
ANIME_LIST_TYPE = '//ul[@class="ListAnimes AX Rows A03 C02 D02"]/li/article[@class="Anime alt B"]/a/div/span/text()'
ANIME_LIST_IMG = '//ul[@class="ListAnimes AX Rows A03 C02 D02"]/li/article[@class="Anime alt B"]/a/div/figure/img/@src'
ANIME_DESCRIPTION = '//div[@class="Container"]/div/main/section[@class="WdgtCn"]/div[@class="Description"]/p/text()' #URL DIFFERENT https://www3.animeflv.net/anime/MY-ANIME-NAME#

PAGINATION_SIZE = '//ul[@class="pagination"]/li/a[text() > 150]/text()'

scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome' if random.randrange(2) == 1 else 'firefox',
                'platform': 'windows',
                'desktop': True
            }
        )

def recent_animes():
    try:
        print('Fetching recent animes...')
        response = scraper.get(URL)
        if response.status_code == 200:
            home = response.content.decode('utf-8', errors='ignore')
            parsed = html.fromstring(home)
            names = parsed.xpath(RECENT_EPISODES_NAME)
            episodes = parsed.xpath(RECENT_EPISODES_NUMBER)
            images = parsed.xpath(RECENT_EPISODES_IMG)
            links = parsed.xpath(RECENT_EPISODES_LINK)
            db_conexion = sqlite3.connect("anime_db")
            cursor = db_conexion.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS recent_episodes ( name VARCHAR(256), episode INTEGER DEFAULT -10, image VARCHAR(512), link VARCHAR(512), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL )")
            cursor.execute("DELETE FROM recent_episodes")
            for i in range(len(names)):
                cursor.execute("INSERT INTO recent_episodes (name, episode, image, link) VALUES(?,?,?,?)", (names[i], int(episodes[i].replace('Episodio', '')), f'{URL}{images[i]}', f'{URL}{links[i]}'))
            db_conexion.commit()
            db_conexion.close()
            print('All recent animes have been fetched.')
        else:
            raise ValueError(f'Error: {response.status_code}')

    except ValueError as error:
        print(error)


def fill_animes():
    try:
        print('Fetching all animes...')
        response_pagination = scraper.get(f'{URL}/browse')
        home_pagination = response_pagination.content.decode('utf-8', errors='ignore')
        parsed_pagination = html.fromstring(home_pagination)
        pagination = parsed_pagination.xpath(PAGINATION_SIZE)
        print(f'Total pages: {pagination[0]}' if pagination else f'Some error ocurred, iterating over: {200}')
        for page in range(int(pagination[0]) if pagination else 200):
            response = scraper.get(f'{URL}/browse?page={page+1}')
            home = response.content.decode('utf-8', errors='ignore')
            if home == '':
                print('All animes have been fetched.')
                break
            else:
                parsed = html.fromstring(home)
                names = parsed.xpath(ANIME_LIST_NAME)
                types = parsed.xpath(ANIME_LIST_TYPE)
                images = parsed.xpath(ANIME_LIST_IMG)
                links = parsed.xpath(ANIME_LIST_LINK)
                if response.status_code == 200:
                    db_conexion = sqlite3.connect("anime_db")
                    cursor = db_conexion.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS animes (id_anime INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name VARCHAR(256) UNIQUE, type VARCHAR(50), image VARCHAR(512), link VARCHAR(512), description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL )")
                    cursor.execute("SELECT name, description FROM animes")
                    animes = cursor.fetchall()
                    for i in range(len(names)):
                        if names[i] in [x[0] for x in animes]:
                            print('Anime previusly added.')
                        else:
                            response_description = scraper.get(f'{URL}{links[i]}')
                            home_description = response_description.content.decode('utf-8', errors='ignore')
                            parsed_description = html.fromstring(home_description)
                            description = parsed_description.xpath(ANIME_DESCRIPTION)
                            cursor.execute("INSERT INTO animes (name, type, image, link, description) VALUES(?,?,?,?,?) ON CONFLICT(name) DO NOTHING", (names[i], types[i], images[i], f'{URL}{links[i]}', description[0] if description else ''))
                    db_conexion.commit()
                    db_conexion.close()
                else:
                    raise ValueError(f'Error: {response.status_code}')
            print(f'Page: {page+1}.')
            
    except ValueError as error:
        print(error)

def run():
    recent_animes()
    fill_animes()

if __name__ == '__main__':
    run()