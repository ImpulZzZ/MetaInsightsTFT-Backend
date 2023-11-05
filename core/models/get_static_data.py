import json

DATA_VERSION  = "13.18.1"
DATA_HOME_DIR = "Set9_5_data"
CURRENT_PATCH = "13.21"
ENTITY_TYPE_TO_FILE_MAP = {
    "tft-champion": f"{DATA_HOME_DIR}/champions.json",
    "tft-trait": f"{DATA_HOME_DIR}/traits.json",
    "tft-item": f"{DATA_HOME_DIR}/items.json"
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