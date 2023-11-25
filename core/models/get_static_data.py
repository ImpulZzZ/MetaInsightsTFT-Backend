import json
from core.models.mysql_utils import *

ENTITY_TYPE_TO_FILE_MAP = {
    "tft-champion": "champions.json",
    "tft-trait"   : "traits.json",
    "tft-item"    : "items.json"
}

def get_static_data():
    result = {}
    for entity_type in ENTITY_TYPE_TO_FILE_MAP:
        with open(ENTITY_TYPE_TO_FILE_MAP[entity_type]) as jsonfile:
            data = json.load(jsonfile)['data']
            for current in data:
                current_dict = {
                    current: {
                        'id': data[current]['id'],
                        'name': data[current]['name'],
                        'icon': f"/img/{entity_type}/{data[current]['image']['full']}"
                        }
                   }
                ## champions have with 'cost' an additional static value
                if entity_type == 'tft-champion': current_dict[current].update({'cost': data[current]['tier']})
                result.update(current_dict)
    return result


def build_sql_query(args, table_name):
    base_query = f"SELECT DISTINCT name, display_name, icon FROM {table_name}"

    conditions = []
    for key, value in args.items():
        if value is not None:
            conditions.append(f"{key} = '{value}'")

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    return base_query


def get_icons(name, display_name, table_name):
    args = {
        'name': name,
        'display_name': display_name
    }
    sql = build_sql_query(args, table_name)
    paths = get_sql_data(sql)

    result = {}
    for current in paths: result.update({current['display_name']: current['icon']})

    return result


def get_champion_names(patch):
    result = [""]
    champions = get_sql_data(f"SELECT DISTINCT ch.display_name FROM composition c JOIN champion ch ON c.id = ch.composition_id JOIN item i ON ch.id = i.champion_id WHERE c.patch = '{patch}' ORDER BY ch.display_name", False)
    for champion in champions:
        for name in champion:
            result.append(name)
    return result


def get_item_names(patch):
    result = [""]
    items = get_sql_data(f"SELECT DISTINCT i.display_name FROM composition c JOIN champion ch ON c.id = ch.composition_id JOIN item i ON ch.id = i.champion_id WHERE c.patch = '{patch}' AND i.display_name != '' ORDER BY i.display_name", False)
    for item in items:
        for name in item:
            result.append(name)
    return result


def get_trait_names(patch):
    result = [""]
    traits = get_sql_data(f"SELECT DISTINCT t.display_name FROM composition c JOIN trait t ON c.id = t.composition_id WHERE c.patch = '{patch}' ORDER BY t.display_name;", False)
    for trait in traits:
        for name in trait:
            result.append(name)
    return result