import asyncio
import json
import re

import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
        'user-agent': 'LemonBot/0.1 (+)',
    }

def roles_from_html(html):
    soup = BeautifulSoup(html, 'lxml')

    spans = soup.find_all('span', {'class': 'notice'})
    if 'Ranked' not in str(spans[0].contents):
        return []
    scripts = soup.find_all('script')
    populator = str(scripts[-1].contents[0])
    data = populator.split('\n')[3].strip()
    json_data = re.search('{(.*?)};', data).group().replace(';', '')
    parsed = json.loads(json_data)
    players = parsed['players']
    roles = [p['role'] for p in players]
    return roles


async def main():
    all_data = {}
    with open('data.json', 'rb') as infile:
        all_data = json.load(infile)
    async with aiohttp.ClientSession() as session:
        for i in range(1,1000): #897236 is the first report from Sept 2017 (First month after new Ranked Rolelist.)
            async with await session.post(f'https://www.blankmediagames.com/Trial/viewReport.php?id={i}', headers=HEADERS) as response:
                try:
                    r = roles_from_html(await response.text())
                except Exception:
                    r = None
                print(f'Fetching report ID {i}')
                if r:
                    print('Ranked Game. Roles as follows:')
                    print(f'\t{r}')
                    all_data[f'Report {i}']=r
                    with open('data.json', 'w') as outfile:
                        json.dump(all_data, outfile)
                else:
                    print('Not a ranked Game.')



loop = asyncio.get_event_loop()
loop.run_until_complete(main())
