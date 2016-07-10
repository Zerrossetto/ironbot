#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import enum
import asyncio
import logging.config
import os
import aiohttp
from typing import Optional
from bs4 import BeautifulSoup
import peewee

logging.config.fileConfig(os.path.join('ironbot', 'logger.conf'),
                          disable_existing_loggers=False)
log = logging.getLogger('hiddenstreet')


class BaseModel(peewee.Model):
    class Meta:
        database = peewee.SqliteDatabase(':memory:')

    @staticmethod
    def convert(tag, field_type=str, strip_comma=False):
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


class Weapon(BaseModel):
    id_weapon = peewee.PrimaryKeyField()
    name = peewee.TextField()
    weapon_type = peewee.TextField()
    required_level = peewee.IntegerField(null=True)
    required_stats = peewee.TextField(null=True)
    weapon_attack = peewee.IntegerField(null=True)
    attack_speed = peewee.TextField(null=True)
    job = peewee.TextField()
    effects = peewee.TextField(null=True)
    available_upgrades = peewee.IntegerField(null=True)
    sold_for = peewee.IntegerField()
    description = peewee.TextField(null=True)
    dropped_by = peewee.TextField(null=True)
    available_from = peewee.TextField(null=True)
    remarks = peewee.TextField(null=True)

    def to_dict(self):
        return {
            'name': self.name,
            'weapon_type': self.weapon_type,
            'required_level': self.required_level,
            'required_stats': self.required_stats,
            'weapon_attack': self.weapon_attack,
            'attack_speed': self.attack_speed,
            'job': self.job,
            'effects': self.effects,
            'available_upgrades': self.available_upgrades,
            'sold_for': self.sold_for,
            'dropped_by': self.dropped_by,
            'available_from': self.available_from,
            'remarks': self.remarks}

    @staticmethod
    def parse_tag(tag, weapon_type):
        cells = tag.find_all('td')
        weapon = {'name': cells[1].strong.a.string,
                  'weapon_type': weapon_type.value,
                  'required_level': BaseModel.convert(cells[2], int),
                  'required_stats': BaseModel.convert(cells[3]),
                  'weapon_attack': BaseModel.convert(cells[4], int),
                  'attack_speed': BaseModel.convert(cells[5]),
                  'job': BaseModel.convert(cells[6]),
                  'effects': BaseModel.convert(cells[7]),
                  'available_upgrades': BaseModel.convert(cells[8], int),
                  'sold_for': BaseModel.convert(cells[9]),
                  'dropped_by': BaseModel.convert(cells[10]),
                  'available_from': None,
                  'remarks': None}
        try:
            tmp = weapon['sold_for'].index(' ')
            weapon['sold_for'] = int(weapon['sold_for'][:tmp].replace(',', ''))
        except ValueError:
            weapon['sold_for'] = 0
        return weapon


class Monster(BaseModel):
    id_monster = peewee.PrimaryKeyField()
    hiddenstreet_alias = peewee.TextField(unique=True)
    image_url = peewee.TextField(null=True)
    name = peewee.TextField()
    level = peewee.IntegerField(null=True)
    health_points = peewee.IntegerField(null=True)
    mana_points = peewee.IntegerField(null=True)
    experience = peewee.IntegerField(null=True)
    mesos = peewee.IntegerField(null=True)
    knockback = peewee.IntegerField(null=True)
    etc_drop = peewee.TextField(null=True)
    common_equipment = peewee.TextField(null=True)
    warrior_equipment = peewee.TextField(null=True)
    magician_equipment = peewee.TextField(null=True)
    bowman_equipment = peewee.TextField(null=True)
    thief_equipment = peewee.TextField(null=True)
    pirate_equipment = peewee.TextField(null=True)
    ore_drop = peewee.TextField(null=True)
    maker_item = peewee.TextField(null=True)
    useable_drop = peewee.TextField(null=True)
    weapon_attack = peewee.IntegerField(null=True)
    magic_attack = peewee.IntegerField(null=True)
    weapon_defence = peewee.IntegerField(null=True)
    magic_defence = peewee.IntegerField(null=True)
    phisical_dmg_reduction = peewee.IntegerField(null=True)
    magical_dmg_reduction = peewee.IntegerField(null=True)
    speed = peewee.IntegerField(null=True)
    accuracy = peewee.IntegerField(null=True)
    avoidability = peewee.IntegerField(null=True)
    weakness_to_magic = peewee.TextField(null=True)
    normal_to_magic = peewee.TextField(null=True)
    resistance_to_magic = peewee.TextField(null=True)
    immune_to_magic = peewee.TextField(null=True)
    unique_attack = peewee.TextField(null=True)
    health_points_recovery = peewee.IntegerField(null=True)
    mana_points_recovery = peewee.IntegerField(null=True)
    immune_against_status = peewee.TextField(null=True)
    inflict_status = peewee.TextField(null=True)
    common_location = peewee.TextField(null=True)

    def to_dict(self):
        return {
            'hiddenstreet_alias': self.hiddenstreet_alias,
            'name': self.name,
            'level': self.level,
            'health_points': self.health_points,
            'mana_points': self.mana_points,
            'experience': self.experience,
            'mesos': self.mesos,
            'knockback': self.knockback,
            'etc_drop': self.etc_drop,
            'common_equipment': self.common_equipment,
            'warrior_equipment': self.warrior_equipment,
            'magician_equipment': self.magician_equipment,
            'bowman_equipment': self.bowman_equipment,
            'thief_equipment': self.thief_equipment,
            'pirate_equipment': self.pirate_equipment,
            'ore_drop': self.ore_drop,
            'maker_item': self.maker_item,
            'useable_drop': self.useable_drop,
            'weapon_attack': self.weapon_attack,
            'magic_attack': self.magic_attack,
            'weapon_defence': self.weapon_defence,
            'magic_defence': self.magic_defence,
            'phisical_dmg_reduction': self.phisical_dmg_reduction,
            'magical_dmg_reduction': self.magical_dmg_reduction,
            'speed': self.speed,
            'accuracy': self.accuracy,
            'avoidability': self.avoidability,
            'weakness_to_magic': self.weakness_to_magic,
            'resistance_to_magic': self.resistance_to_magic,
            'immune_to_magic': self.immune_to_magic,
            'unique_attack': self.unique_attack,
            'health_points_recovery': self.health_points_recovery,
            'mana_points_recovery': self.mana_points_recovery,
            'immune_against_status': self.immune_against_status,
            'inflict_status': self.inflict_status,
            'common_location': self.common_location}

    @staticmethod
    def parse_tag(tag, *args):
        cells = tag.find_all('td')
        equipment = cells[7].find_all('div', recursive=False)
        stats = cells[11].find_all('div', recursive=False)
        magic = cells[12].find_all('div', recursive=False)
        special = cells[13].find_all('div', recursive=False)
        statuses = cells[14].find_all('div', recursive=False)
        monster = {
            'hiddenstreet_alias': cells[0].find('div', 'field-label-inline')
                                          .a.get('href').split('/')[-1],
            'name': cells[0].find('div', 'field-label-inline').a.strong.string,
            'level': cells[0].find('strong', recursive=False),
            'health_points': BaseModel.convert(cells[1], int),
            'mana_points': BaseModel.convert(cells[2], int),
            'experience': BaseModel.convert(cells[3], int),
            'mesos': BaseModel.convert(cells[4], int),
            'knockback': BaseModel.convert(cells[5], int),
            'etc_drop': BaseModel.convert(cells[6]),
            'common_equipment': BaseModel.convert(equipment[0]),
            'warrior_equipment': BaseModel.convert(equipment[1]),
            'magician_equipment': BaseModel.convert(equipment[2]),
            'bowman_equipment': BaseModel.convert(equipment[3]),
            'thief_equipment': BaseModel.convert(equipment[4]),
            'pirate_equipment': BaseModel.convert(equipment[5]),
            'ore_drop': BaseModel.convert(cells[8]),
            'maker_item': BaseModel.convert(cells[9]),
            'useable_drop': BaseModel.convert(cells[10]),
            'weapon_attack': BaseModel.convert(stats[0], int),
            'magic_attack': BaseModel.convert(stats[1], int),
            'weapon_defence': BaseModel.convert(stats[2], int),
            'magic_defence': BaseModel.convert(stats[3], int),
            'phisical_dmg_reduction': BaseModel.convert(stats[4], int),
            'magical_dmg_reduction': BaseModel.convert(stats[5], int),
            'speed': BaseModel.convert(stats[6], int),
            'accuracy': BaseModel.convert(stats[7], int),
            'avoidability': BaseModel.convert(stats[8], int),
            'normal_to_magic': None,
            'weakness_to_magic': BaseModel.convert(magic[0]),
            'resistance_to_magic': BaseModel.convert(magic[1]),
            'immune_to_magic': BaseModel.convert(magic[2]),
            'unique_attack': BaseModel.convert(special[0]),
            'health_points_recovery': BaseModel.convert(special[1], int),
            'mana_points_recovery': BaseModel.convert(special[2], int),
            'immune_against_status': BaseModel.convert(statuses[0]),
            'inflict_status': BaseModel.convert(statuses[1]),
            'common_location': None
        }
        monster['image_url'] = cells[0].find('img')
        if monster['image_url']:
            monster['image_url'] = monster['image_url'].get('src')
        try:
            tmp = monster['level'].index(' ')
            monster['level'] = int(monster['level'][:tmp])
        except ValueError:
            monster['level'] = None
        return monster

    @staticmethod
    def parse_bbb_tag(tag, *args):
        cells = tag.find_all('td')
        equipment = cells[7].find_all('div')
        stats = cells[11].find_all('div')
        magic = cells[12].find_all('div')
        special = cells[13].find_all('div')
        statuses = cells[14].find_all('div')
        monster = {
            'hiddenstreet_alias': tag.get('id'),
            'name': cells[0].strong.string.strip(),
            'level': cells[0].contents[-1].strip(),
            'health_points': BaseModel.convert(cells[1], int, True),
            'mana_points': BaseModel.convert(cells[2], int, True),
            'experience': BaseModel.convert(cells[3], int, True),
            'mesos': BaseModel.convert(cells[4], int, True),
            'knockback': BaseModel.convert(cells[5], int),
            'etc_drop': BaseModel.convert(cells[6]),
            'common_equipment': BaseModel.convert(equipment[0]),
            'warrior_equipment': BaseModel.convert(equipment[1]),
            'magician_equipment': BaseModel.convert(equipment[2]),
            'bowman_equipment': BaseModel.convert(equipment[3]),
            'thief_equipment': BaseModel.convert(equipment[4]),
            'pirate_equipment': BaseModel.convert(equipment[5]),
            'ore_drop': BaseModel.convert(cells[8]),
            'maker_item': BaseModel.convert(cells[9]),
            'useable_drop': BaseModel.convert(cells[10]),
            'weapon_attack': BaseModel.convert(stats[0], int),
            'magic_attack': BaseModel.convert(stats[1], int),
            'weapon_defence': BaseModel.convert(stats[2], int),
            'magic_defence': BaseModel.convert(stats[3], int),
            'phisical_dmg_reduction': BaseModel.convert(stats[4], int),
            'magical_dmg_reduction': BaseModel.convert(stats[5], int),
            'speed': BaseModel.convert(stats[6], int),
            'accuracy': BaseModel.convert(stats[7], int),
            'avoidability': BaseModel.convert(stats[8], int),
            'weakness_to_magic': BaseModel.convert(magic[0]),
            'normal_to_magic': BaseModel.convert(magic[1]),
            'resistance_to_magic': BaseModel.convert(magic[2]),
            'immune_to_magic': BaseModel.convert(magic[3]),
            'unique_attack': BaseModel.convert(special[0]),
            'health_points_recovery': BaseModel.convert(special[1], int),
            'mana_points_recovery': BaseModel.convert(special[2], int),
            'immune_against_status': BaseModel.convert(statuses[0]),
            'inflict_status': BaseModel.convert(statuses[1]),
            'common_location': None
        }
        monster['image_url'] = cells[0].find('img')
        if monster['image_url']:
            monster['image_url'] = monster['image_url'].get('src')
        try:
            monster['level'] = int(monster['level'])
        except ValueError:
            monster['level'] = None
        return monster


class UrlElement(enum.Enum):

    def __init__(self, url_placeholder, url_argument=None):
        self.url_placeholder = url_placeholder
        self.url_argument_type = url_argument

    def __repr__(self):
        return '<{}.{}: {}, abbr: {}>'.format(self.__class__.__name__,
                                              self.name,
                                              self.value,
                                              self.url_placeholder)

    def __str__(self):
        return self.url_placeholder


class Server(UrlElement):
    GLOBAL = ('gms')
    EUROPE = ('ems')
    KOREA = ('kms')
    JAPAN = ('jms')
    SOUTH_EAST_ASIA = ('msea')
    CHINA = ('cms')
    TAIWAN = ('twms')
    BEFORE_BIG_BANG = ('bbb')


class ClassType(UrlElement):

    ADMIN = ('admin')
    ADVENTURER = ('adventurer')
    CYGNUS_KNIGHT = ('cygnus-knight')
    GUILD = ('guild')
    HEROES = ('heroes')
    RESISTANCE = ('resistance')
    NOVA = ('nova')
    SENGOKU = ('sengoku')
    CHILD_OF_GOD = ('child-of-god')
    BEAST_TAMER = ('beast-tamer')


class EquipmentType(UrlElement):

    ACCESSORY = ('acessory')
    ARMOUR = ('armour')
    TAMING_MOB = ('taming-mob')
    ANDROID = ('android')
    WEAPON = ('weapon')
    MONSTER_CARD_SET = ('monster-card-set')


class WeaponType(UrlElement):

    BOW = ('bow')
    CANE = ('cane')
    CANNON = ('cannon')
    CLAW = ('claw')
    DAGGER = ('dagger')
    DUAL_BOW = ('dual-bow')
    GUN = ('gun')
    KATARA = ('katara')
    KNUCKLE = ('knuckle')
    MERCEDES_ARROW = ('mercedes-arrow')
    ONE_HANDED_AXE = ('one-handed-axe')
    ONE_HANDED_BLUNT_WEAPON = ('one-handed-blunt-weapon')
    ONE_HANDED_SWORD = ('one-handed-sword')
    PICKAXE = ('pickaxe')
    POLEARM = ('polearm')
    SHINING_ROD = ('shining-rod')
    SHOVEL = ('shovel')
    SPEAR = ('spear')
    STAFF = ('staff')
    TOTEM = ('totem')
    TWO_HANDED_AXE = ('two-handed-axe')
    TWO_HANDED_BLUNT_WEAPON = ('two-handed-blunt-weapon')
    TWO_HANDED_SWORD = ('two-handed-sword')
    WAND = ('wand')

    @classmethod
    def related_model(cls):
        return Weapon


class ItemType(UrlElement):

    USEABLE = ('useable-item')
    ORE = ('ore')
    MISCELLANEOUS = ('misc-item')
    SET_UP = ('setup')
    MAKER = ('maker-item')
    PROFESSION = ('profession-item')


class MonsterLevelType(UrlElement):
    LEVEL_1_TO_10 = ('1-10')
    LEVEL_11_TO_20 = ('11-20')
    LEVEL_21_TO_30 = ('21-30')
    LEVEL_31_TO_40 = ('31-40')
    LEVEL_41_TO_50 = ('41-50')
    LEVEL_51_TO_60 = ('51-60')
    LEVEL_61_TO_70 = ('61-70')
    LEVEL_71_TO_80 = ('71-80')
    LEVEL_81_TO_90 = ('81-90')
    LEVEL_91_TO_100 = ('91-100')
    # These are non-bbb related
    LEVEL_101_TO_120 = ('101-120')
    LEVEL_121_TO_140 = ('121-140')
    LEVEL_141_TO_160 = ('141-160')
    LEVEL_161_TO_180 = ('161-180')
    LEVEL_181_TO_200 = ('181-200')
    # These are bbb only
    LEVEL_101_TO_150 = ('101-150')
    LEVEL_151_TO_200 = ('151-200')

    @classmethod
    def related_model(cls):
        return Monster


class Section(UrlElement):

    EXPERIENCE_TABLE = ('experience-table')
    TOOLS = ('pet-closensess-table')
    CLASS = ('class', ClassType)
    EQUIPMENT = ('equipment', EquipmentType)
    ITEM = ('item', ItemType)
    MONSTER = ('monster', MonsterLevelType)


class HiddenStreet:

    base_url = 'https://www.hidden-street.net'
    base_url_bbb = 'http://bbb.hidden-street.net'

    def __init__(self):
        self.db = BaseModel._meta.database
        self.db.create_tables([Weapon, Monster])
        self.max_bulk_rows = 20
        self.db_refreshing = False
        self.refresh_data()

    def refresh_data(self):
        self.db_refreshing = True
        log.info('refreshing data...')
        loop = asyncio.get_event_loop()
        semaphore = asyncio.Semaphore(5)
        f = asyncio.wait([HiddenStreet.last_page(semaphore=semaphore,
                                                 server=Server.BEFORE_BIG_BANG,
                                                 section=Section.MONSTER,
                                                 subsection=lvl)
                          for lvl in MonsterLevelType])
        finished, pending = loop.run_until_complete(f)

        cats_pages = []
        for last_page, category in [task.result() for task in finished]:
            for i in range(last_page + 1):
                    cats_pages.append((category, i))

        log.debug(cats_pages)
        # f = asyncio.wait([HiddenStreet.scrape(semaphore=semaphore,
        #                                       server=Server.BEFORE_BIG_BANG,
        #                                       section=Section.EQUIPMENT,
        #                                       subsection=EquipmentType.WEAPON,
        #                                       category=w, model=Weapon)
        #                   for w in WeaponType] +
        #                  [HiddenStreet.scrape(semaphore=semaphore,
        #                                       server=Server.BEFORE_BIG_BANG,
        #                                       section=Section.MONSTER,
        #                                       subsection=lvl, model=Monster)
        #                   for lvl in MonsterLevelType])
        f = asyncio.wait([HiddenStreet.scrape(semaphore=semaphore,
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
        # lvl = MonsterLevelType.LEVEL_21_TO_30
        # f = asyncio.wait([HiddenStreet.scrape(semaphore=semaphore,
        #                                       section=Section.MONSTER,
        #                                       subsection=lvl,
        #                                       model=Monster)])

        with self.db.atomic():
            for result, category in [task.result() for task in finished]:
                for i in range(0, len(result), self.max_bulk_rows):
                    top = i + self.max_bulk_rows
                    type(category).related_model() \
                                  .insert_many(result[i:top]) \
                                  .execute()
                if len(result) == 0:
                    log.warn('empty result set for '
                             '{} category'.format(category))

        # query = Weapon.select(Weapon.weapon_type) \
        #               .group_by(Weapon.weapon_type)
        # print([weapon.weapon_type for weapon in query.execute()])
        # print([m.name for m in Monster.select(Monster.name).execute()])

        self.db_refreshing = False
        log.info('refreshing data... done')

    def monsters_by_name(self, monster_name, exact_match=False):
        if self.db_refreshing:
            raise ValueError('Database refresh in progress')

        if exact_match:
            keyw = monster_name
        else:
            keyw = '%{}%'.format(monster_name)

        q = Monster.select().where(Monster.name ** keyw)
        return q.execute()

    @asyncio.coroutine
    def last_page(server, subsection, semaphore, category=None, *args, **argv):
        url = HiddenStreet.build_url(server=server, subsection=subsection,
                                     category=category, *args, **argv)
        with (yield from semaphore):
            log.info('connecting to url {}'.format(url))
            response = yield from aiohttp.request('GET', url, compress=True)
            log.debug('gotten {} for url {}'.format(response.status, url))
            page = yield from response.text()
        log.debug('connection to url {} closed'.format(url))
        if response.status != 200:
            if category:
                return 0, category
            else:
                return 0, subsection
        soup = BeautifulSoup(page, 'lxml')
        if server == Server.BEFORE_BIG_BANG:
            last_page_href = soup.find('li', class_='pager-last').a.get('href')
            last_page = int(last_page_href[last_page_href.index('page=')+5:])
        else:
            # TODO to be implemented
            last_page = 0
        if category:
            return last_page, category
        else:
            return last_page, subsection

    @asyncio.coroutine
    def scrape(server, subsection, semaphore, model,
               category=None, *args, **argv):
        url = HiddenStreet.build_url(server=server, subsection=subsection,
                                     category=category, *args, **argv)
        result = []
        with (yield from semaphore):
            log.info('connecting to url {}'.format(url))
            response = yield from aiohttp.request('GET', url, compress=True)
            log.debug('gotten {:d} for url {}'.format(response.status, url))
            page = yield from response.text()
        log.info('connection to url {} closed'.format(url))
        if response.status != 200:
            if category:
                return result, category
            else:
                return result, subsection
        soup = BeautifulSoup(page, 'lxml')
        if server == Server.BEFORE_BIG_BANG:
            for tag in soup.find_all('table', class_='monster'):
                result.append(model.parse_bbb_tag(tag, category))
        else:
            for tag in soup.find_all('table', class_='database-info'):
                result.append(model.parse_tag(tag, category))

        if category:
            log.info('parsing of {} -> {} done'.format(subsection, category))
            return result, category
        else:
            log.info('parsing of {} done'.format(subsection))
            return result, subsection

    @staticmethod
    def build_url(server: Server=Server.GLOBAL,
                  section: Section=Section.EQUIPMENT,
                  subsection: Optional[UrlElement]=None,
                  category: Optional[UrlElement]=None,
                  page: int=0):

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

        if page > 0:
            return '{}?page={:d}'.format('/'.join(url), page)
        else:
            return '/'.join(url)

if __name__ == '__main__':
    HiddenStreet()
