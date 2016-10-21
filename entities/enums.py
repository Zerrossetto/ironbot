import enum
from .models import Monster, Weapon


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