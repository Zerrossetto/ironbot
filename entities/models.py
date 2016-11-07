import peewee
from inspect import getmembers

sqlite_db = peewee.SqliteDatabase(':memory:')

class BaseModel(peewee.Model):
    class Meta:
        database = sqlite_db

    @property
    def to_dict(self):
        fields = getmembers(type(self), lambda m: issubclass(type(m), peewee.Field))
        return {key: getattr(self, key) for key, value in fields}


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


class MapleWeapon(BaseModel):
    id_weapon = peewee.PrimaryKeyField()
    name = peewee.TextField()
    weapon_type = peewee.TextField()
    required_level = peewee.TextField(null=True)
    required_stats = peewee.TextField(null=True)
    weapon_attack = peewee.TextField(null=True)
    magic_attack = peewee.TextField(null=True)
    attack_speed = peewee.TextField(null=True)
    job = peewee.TextField()
    effects = peewee.TextField(null=True)
    available_upgrades = peewee.TextField(null=True)
    sold_for = peewee.TextField()
    description = peewee.TextField(null=True)
    dropped_by = peewee.TextField(null=True)
    available_from = peewee.TextField(null=True)
    remarks = peewee.TextField(null=True)