import asyncio
import json
import re
from enum import Enum
from time import time

import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    'user-agent': 'Mozilla/5.0 (compatible; LemonBot/0.1; +https://github.com/doublemon/lemonbot/blob/master/README.md)',
}


class GameMode(Enum):
    CLASSIC = 0
    RANKED = 1
    ALLANY = 2
    CUSTOM = 3
    RAINBOW = 4


class RoleParser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'lxml')
        notices = self.soup.find_all('span', {'class': 'notice'})
        self.is_ranked = False
        self.unique_roles = True
        for notice in notices:
            if 'Ranked' in notice.text:
                self.is_ranked = True

    def parse_roles(self):
        scripts = self.soup.find_all('script')
        populator = ''.join([script.text for script in scripts if not script.get('src', False)])
        report_data = re.search('data = .*?;', populator).group()
        data_strip = re.sub('data = ', '', report_data)
        data_strip = re.sub(';', '', data_strip)
        data = json.loads(data_strip)
        players = data.get('players')
        roles = [p.get('role') for p in players]
        return roles


async def main():
    file_name = f'scrape/role_scrape_{int(time())}.json'
    with open(file_name, 'w+'):
        pass
    role_scrape = []
    async with aiohttp.ClientSession() as session:
        for i in range(1003000,
                       1007000):  # 897236 is the first report from Sept 2017 (First month after new Ranked Role List.)
            async with await session.get(f'https://www.blankmediagames.com/Trial/viewReport.php?id={i}',
                                         headers=HEADERS) as response:
                print(f'Fetching report: ID {i}.')
                if response.status == 200:
                    html = await response.text(encoding='utf-8')
                    parser = RoleParser(html)
                    if parser.is_ranked:
                        roles = parser.parse_roles()
                        if roles.count('Mafioso') <= 1 and roles.count('Godfather') <= 1:
                            print(f'\t{roles}')
                            role_scrape.append(roles)

                        else:
                            print('\tMultiple Mafioso/Godfather.')
                    else:
                        print('\tNot a Ranked Game.')

    with open(file_name, 'w') as outfile:
        json.dump(role_scrape, outfile)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
