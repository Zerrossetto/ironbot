import asyncio
import csv
import functools
import logging
import operator
import os
import itertools
import peewee
import settings
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Optional, Generic
from entities.models import sqlite_db, Weapon, Monster, MapleWeapon
from entities.enums import MonsterLevelType, Section, Server, UrlElement

log = logging.getLogger(settings.LOGGER_HIDDENSTREET)


def convert(tag: Tag, field_type: Generic(str, int)=str, strip_comma=False):
    result = tag.find('div', class_='field-item')
    if result:
        result = result.string
    elif tag.div and 'field-label-inline' in tag.div.get('class'):
        result = tag.div.contents[-1].strip()
    else:
        try:
            result = tag.contents[-1].strip()
        except AttributeError:
            result = None
    if field_type == str:
        if result == '-' or result == '?':
            result = None
    else:
        if strip_comma:
            result = result.replace(',', '')
        try:
            result = field_type(result)
        except ValueError:
            result = None
    return result


def parse_monster_tag(tag: Tag, *args):
    cells = tag.find_all('td')
    equipment = cells[7].find_all('div', recursive=False)
    stats = cells[11].find_all('div', recursive=False)
    magic = cells[12].find_all('div', recursive=False)
    special = cells[13].find_all('div', recursive=False)
    statuses = cells[14].find_all('div', recursive=False)

    monster = dict(hiddenstreet_alias=cells[0].find('div', 'field-label-inline').a.get('href').split('/')[-1],
                   name=cells[0].find('div', 'field-label-inline').a.strong.string,
                   level=cells[0].find('strong', recursive=False),
                   health_points=convert(cells[1], int),
                   mana_points=convert(cells[2], int),
                   experience=convert(cells[3], int),
                   mesos=convert(cells[4], int),
                   knockback=convert(cells[5], int),
                   etc_drop=convert(cells[6]),
                   common_equipment=convert(equipment[0]),
                   warrior_equipment=convert(equipment[1]),
                   magician_equipment=convert(equipment[2]),
                   bowman_equipment=convert(equipment[3]),
                   thief_equipment=convert(equipment[4]),
                   pirate_equipment=convert(equipment[5]),
                   ore_drop=convert(cells[8]),
                   maker_item=convert(cells[9]),
                   useable_drop=convert(cells[10]),
                   weapon_attack=convert(stats[0], int),
                   magic_attack=convert(stats[1], int),
                   weapon_defence=convert(stats[2], int),
                   magic_defence=convert(stats[3], int),
                   phisical_dmg_reduction=convert(stats[4], int),
                   magical_dmg_reduction=convert(stats[5], int),
                   speed=convert(stats[6], int),
                   accuracy=convert(stats[7], int),
                   avoidability=convert(stats[8], int),
                   normal_to_magic=None,
                   weakness_to_magic=convert(magic[0]),
                   resistance_to_magic=convert(magic[1]),
                   immune_to_magic=convert(magic[2]),
                   unique_attack=convert(special[0]),
                   health_points_recovery=convert(special[1], int),
                   mana_points_recovery=convert(special[2], int),
                   immune_against_status=convert(statuses[0]),
                   inflict_status=convert(statuses[1]),
                   common_location=None,
                   image_url=cells[0].find('img'))
    if monster['image_url']:
        monster['image_url'] = monster['image_url'].get('src')
    try:
        tmp = monster['level'].index(' ')
        monster['level'] = int(monster['level'][:tmp])
    except ValueError:
        monster['level'] = None
    return monster


def parse_monster_bbb_tag(tag: Tag, *args):
    cells = tag.find_all('td')
    equipment = cells[7].find_all('div')
    stats = cells[11].find_all('div')
    magic = cells[12].find_all('div')
    special = cells[13].find_all('div')
    statuses = cells[14].find_all('div')
    monster = dict(hiddenstreet_alias=tag.get('id'),
                   name=cells[0].strong.string.strip(),
                   level=cells[0].contents[-1].strip(),
                   health_points=convert(cells[1], int, True),
                   mana_points=convert(cells[2], int, True),
                   experience=convert(cells[3], int, True),
                   mesos=convert(cells[4], int, True),
                   knockback=convert(cells[5], int),
                   etc_drop=convert(cells[6]),
                   common_equipment=convert(equipment[0]),
                   warrior_equipment=convert(equipment[1]),
                   magician_equipment=convert(equipment[2]),
                   bowman_equipment=convert(equipment[3]),
                   thief_equipment=convert(equipment[4]),
                   pirate_equipment=convert(equipment[5]),
                   ore_drop=convert(cells[8]),
                   maker_item=convert(cells[9]),
                   useable_drop=convert(cells[10]),
                   weapon_attack=convert(stats[0], int),
                   magic_attack=convert(stats[1], int),
                   weapon_defence=convert(stats[2], int),
                   magic_defence=convert(stats[3], int),
                   phisical_dmg_reduction=convert(stats[4], int),
                   magical_dmg_reduction=convert(stats[5], int),
                   speed=convert(stats[6], int),
                   accuracy=convert(stats[7], int),
                   avoidability=convert(stats[8], int),
                   weakness_to_magic=convert(magic[0]),
                   normal_to_magic=convert(magic[1]),
                   resistance_to_magic=convert(magic[2]),
                   immune_to_magic=convert(magic[3]),
                   unique_attack=convert(special[0]),
                   health_points_recovery=convert(special[1], int),
                   mana_points_recovery=convert(special[2], int),
                   immune_against_status=convert(statuses[0]),
                   inflict_status=convert(statuses[1]),
                   common_location=None)

    monster['image_url'] = cells[0].find('img')
    if monster['image_url']:
        monster['image_url'] = monster['image_url'].get('src')
    try:
        monster['level'] = int(monster['level'])
    except ValueError:
        monster['level'] = None
    return monster


def parse_weapon_tag(tag: Tag, weapon_type):
    cells = tag.find_all('td')
    weapon = dict(name=cells[1].strong.a.string,
                  weapon_type=weapon_type.value,
                  required_level=convert(cells[2], int),
                  required_stats=convert(cells[3]),
                  weapon_attack=convert(cells[4], int),
                  attack_speed=convert(cells[5]),
                  job=convert(cells[6]),
                  effects=convert(cells[7]),
                  available_upgrades=convert(cells[8], int),
                  sold_for=convert(cells[9]),
                  dropped_by=convert(cells[10]),
                  available_from=None,
                  remarks=None)

    try:
        tmp = weapon['sold_for'].index(' ')
        weapon['sold_for'] = int(weapon['sold_for'][:tmp].replace(',', ''))
    except ValueError:
        weapon['sold_for'] = 0
    return weapon


parse_funcs = {
    (Server.BEFORE_BIG_BANG, Monster): parse_monster_bbb_tag,
    (Server.GLOBAL, Monster): parse_monster_tag,
    (Server.EUROPE, Monster): parse_monster_tag,
    (Server.KOREA, Monster): parse_monster_tag,
    (Server.JAPAN, Monster): parse_monster_tag,
    (Server.SOUTH_EAST_ASIA, Monster): parse_monster_tag,
    (Server.CHINA, Monster): parse_monster_tag,
    (Server.TAIWAN, Monster): parse_monster_tag,
    (Server.BEFORE_BIG_BANG, Weapon): lambda *p: ...,  # still NOOP, unfortunately
    (Server.GLOBAL, Weapon): parse_weapon_tag,
    (Server.EUROPE, Weapon): parse_weapon_tag,
    (Server.KOREA, Weapon): parse_weapon_tag,
    (Server.JAPAN, Weapon): parse_weapon_tag,
    (Server.SOUTH_EAST_ASIA, Weapon): parse_weapon_tag,
    (Server.CHINA, Weapon): parse_weapon_tag,
    (Server.TAIWAN, Weapon): parse_weapon_tag
}


def build_url(server: Server = Server.GLOBAL,
              section: Section = Section.EQUIPMENT,
              subsection: Optional[UrlElement] = None,
              category: Optional[UrlElement] = None,
              page: int = 0):
    if server == Server.BEFORE_BIG_BANG:
        url = [HiddenStreet.base_url_bbb, section.url_placeholder]
    else:
        url = [HiddenStreet.base_url,
               server.url_placeholder,
               section.url_placeholder]
    url_placeholder, url_argument = section.value
    if url_argument:
        if url_argument == type(subsection):
            url.append(subsection.url_placeholder)
        else:
            raise TypeError
    if category:
        url.append(category.url_placeholder)

    return '{}?page={:d}'.format('/'.join(url), page) if page > 0 else '/'.join(url)


@asyncio.coroutine
def last_page(server, subsection, semaphore, category=None, *args, **argv):
    url = build_url(server=server, subsection=subsection, category=category, *args, **argv)
    m = 'last_page'
    with (yield from semaphore):
        with ClientSession() as client:
            log.debug('({}) client {}: connecting to url {}'.format(m, id(client), url))
            response = yield from client.get(url, compress=True)
            log.debug('({}) client {}: got {} for url {}'.format(m, id(client), response.status, url))
            resp_status = response.status
            if response.status == 200:
                page = yield from response.text()
            log.debug('({}) client {}: connection to url {} closed'.format(m, id(client), (url)))

    if resp_status != 200:
        if category is None:
            return 0, subsection
        else:
            0, category

    soup = BeautifulSoup(page, settings.BF4_PARSER)
    if server == Server.BEFORE_BIG_BANG:
        last_page_href = soup.find('li', class_='pager-last').a.get('href')
        page_nr = int(last_page_href[last_page_href.index('page=') + 5:])
    else:
        # TODO to be implemented
        page_nr = 0

    return (page_nr, subsection) if category is None else (page_nr, category)


@asyncio.coroutine
def scrape(server, subsection, semaphore, model,
           category=None, *args, **argv):
    url = build_url(server=server, subsection=subsection, category=category, *args, **argv)
    result = []
    m = 'scrape'
    with (yield from semaphore):
        with ClientSession() as client:
            log.debug('({}) client {}: connecting to url {}'.format(m, id(client), url))
            response = yield from client.get(url, compress=True)
            log.debug('({}) client {}: got {:d} for url {}'.format(m, id(client), response.status, url))
            resp_status = response.status
            if response.status == 200:
                page = yield from response.text()
            log.debug('({}) client {}: connection to url {} closed'.format(m, id(client), url))

    if resp_status != 200:
        if category is None:
            return result, subsection
        else:
            return result, category

    soup = BeautifulSoup(page, settings.BF4_PARSER)
    tag_cls_name = 'monster' if server == Server.BEFORE_BIG_BANG else 'database-info'

    for tag in soup.find_all('table', class_=tag_cls_name):
        result.append(parse_funcs[(server, model)](tag, category))

    if category:
        log.info('parsing of {} -> {} done'.format(subsection, category))
        return result, category
    else:
        log.info('parsing of {} done'.format(subsection))
        return result, subsection


class HiddenStreet:
    base_url = 'https://www.hidden-street.net'
    base_url_bbb = 'http://bbb.hidden-street.net'

    def __init__(self, loop):
        self.db = sqlite_db
        self.db.create_tables([Weapon, Monster, MapleWeapon])
        self.max_bulk_rows = 20
        self.db_refreshing = False
        self.refresh_data(loop)

        maple_weapons = []
        with open(os.path.join(os.path.dirname(__file__), 'mapleweapons.csv')) as csvfile:
            list_reader = csv.DictReader(csvfile)
            for weapon in list_reader:
                maple_weapons.append(weapon)

        with self.db.atomic():
            for i in range(0, len(maple_weapons), self.max_bulk_rows):
                top = i + self.max_bulk_rows
                MapleWeapon.insert_many(maple_weapons[i:top]).execute()
                if len(maple_weapons) == 0:
                    log.warn('empty result set for maple weapons')

    def refresh_data(self, loop):
        self.db_refreshing = True
        log.info('refreshing data...')
        semaphore = asyncio.Semaphore(5)
        f = asyncio.wait([last_page(semaphore=semaphore,
                                    server=Server.BEFORE_BIG_BANG,
                                    section=Section.MONSTER,
                                    subsection=lvl)
                          for lvl in MonsterLevelType])
        finished, pending = loop.run_until_complete(f)

        cats_pages = [itertools.product((category,), range(0, page_nr + 1))
                      for page_nr, category in
                      map(lambda task: task.result(), finished)]
        cats_pages = tuple(itertools.chain.from_iterable(cats_pages))

        log.debug(cats_pages)
        f = asyncio.wait([scrape(semaphore=semaphore,
                                 server=Server.BEFORE_BIG_BANG,
                                 section=Section.MONSTER,
                                 subsection=lvl,
                                 page=page,
                                 model=Monster)
                          for lvl, page in cats_pages])
        finished, pending = loop.run_until_complete(f)

        if __name__ == '__main__':
            loop.close()

        if Weapon.select().count() > 0:
            Weapon.delete().execute()
        if Monster.select().count() > 0:
            Monster.delete().execute()

        with self.db.atomic():
            for result, category in [task.result() for task in finished]:

                model = type(category).related_model()

                for i in range(0, len(result), self.max_bulk_rows):
                    top = i + self.max_bulk_rows
                    model.insert_many(result[i:top]).execute()

                if len(result) == 0:
                    log.warn('empty result set for {} category'.format(category))

        self.db_refreshing = False
        log.info('refreshing data... done')

    def monsters_by_name(self, monster_name: str, exact_match: bool=False):
        if self.db_refreshing:
            raise ValueError('Database refresh in progress')

        keyw = monster_name if exact_match else '%{}%'.format(monster_name)

        q = Monster.select().where(Monster.name ** keyw)
        return q.execute()

    def maple_weapon_by_name(self, *weapon_name_terms):
        if self.db_refreshing:
            raise ValueError('Database refresh in progress')

        clauses = [(MapleWeapon.name ** '%{}%'.format(term)) for term in weapon_name_terms]
        return MapleWeapon.select().where(functools.reduce(operator.or_, clauses)).execute()

    def maple_list_by_level(self, weapon_level: int=None):

        if self.db_refreshing:
            raise ValueError('DATABASE DATABASE REFRESHING THE DATABASE')

        sq = (MapleWeapon
              .select(MapleWeapon.required_level,
                      peewee.fn.group_concat(MapleWeapon.name, ', ').alias('names')
                      )
              )

        if weapon_level is not None:
            sq = sq.where(MapleWeapon.required_level == weapon_level)

        sq = sq.group_by(MapleWeapon.required_level)
        return sq.execute()


if __name__ == '__main__':
    HiddenStreet()
