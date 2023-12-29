from bs4 import BeautifulSoup
from urllib.request import urlopen, HTTPError, Request
from http.client import IncompleteRead

from .utils import get_log, omluva

log = get_log()


def _get_html(
    url,
    headers={
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    },
):
    log.info(f'Opening {url}')
    try:
        html = urlopen(Request(url=url, headers=headers)).read().decode('utf-8')
    except HTTPError as e:
        from requests_html import HTMLSession

        session = HTMLSession()

        r = session.get(url, headers=headers)

        r.html.render()  # this call executes the js in the page
        return r.html.text
    except IncompleteRead as e:
        html = e.partial.decode('utf-8')

    return html


def _get_team(team_name: str) -> str:
    html = _get_html(f'https://www.hltv.org/search?query={team_name}')
    soup = BeautifulSoup(html, 'html.parser')
    matches = [
        a.get('href')
        for a in soup.find_all('a')
        if len(a.get_attribute_list('href')) == 1
        and team_name in str(a.get('href'))
        and '/team/' in str(a.get('href'))
    ]
    if len(matches) > 1:
        log.warning(f'Multiple {team_name} found, picking first one from:')
        log.warning(matches)
        return matches[0]
    if len(matches) == 0:
        log.warning(f'Team {team_name} not found')
        log.info(
            [
                a.get('href')
                for a in soup.find_all('a')
                if len(a.get_attribute_list('href')) == 1
                and '/team/' in str(a.get('href'))
            ]
        )
        return ''

    return matches[0]


def upcoming(team_name: str) -> str:
    team_id = _get_team(team_name.lower().rstrip())
    if team_id == '':
        return f'Nemuzu najit {team_name}'
    url = f'https://www.hltv.org{team_id}#tab-matchesBox'
    html = _get_html(url)

    soup = BeautifulSoup(html, 'html.parser')

    # find matches div
    matches = soup.find_all('div', id='matchesBox')

    if len(matches) > 1:
        log.error(f'Multiple match boxes? {url}')
        return omluva()
    if len(matches) == 0:
        log.error(f'No match box? {url}')
        return omluva()

    matches_categories = matches[0].find_all(
        'table', {'class': ['table-container', 'match table']}
    )

    categories_labels = [h2.string for h2 in matches[0]('h2')]

    no_match = matches[0].find_all('div', {'class': ['empty-state']})
    if len(no_match) != 0 and 'No upcoming matches' in str(
        no_match[0].find_all('span')[0].string
    ):
        return f'{team_name} bohuzel nehrajou'

    if len(matches_categories) + 1 != len(categories_labels):
        print(matches_categories)
        print(categories_labels)
        raise RuntimeError(f'Hmm')

    categories_labels = categories_labels[1:]

    found = False
    upcoming = []
    for i in range(len(matches_categories)):
        if 'Upcoming matches' in categories_labels[i]:
            found = True
            upcoming = matches_categories[i].find_all('tr', {'class': ['team-row']})

    if not found:
        return ''

    resultStr = f'Nadchazejici hry {team_name}:\n'
    for match in upcoming:
        match_link = match.find_all('a', {'class': ['matchpage-button']})[0].get('href')
        enemy = match.find_all('div', {'class': 'team-flex'})[1].find('img')['alt']
        time = match.find_all('td', {'class': 'date-cell'})[0].string
        predlozka = (
            'v '
            if match.find_all('td', {'class': 'date-cell'})[0].find_all('span')[0][
                'data-time-format'
            ]
            == 'HH:mm'
            else ''
        )
        resultStr += f' - proti {enemy} {predlozka}{time} \n  (https://www.hltv.org{match_link }) \n'
    return resultStr
