from core.models.mysql_utils import *
from itertools import combinations
from datetime import datetime, timedelta

def get_best_in_slot_items(n, region, league, max_placement, min_counter, min_datetime, champion_name=None):
    ## Join compositions with champions and items, and filter by parameters
    sql = f"SELECT c.id AS composition_id, ch.id as champion_id, ch.display_name AS champion_name, i.display_name AS item_name, c.placement AS placement FROM composition c JOIN champion ch ON c.id = ch.composition_id JOIN item i ON ch.id = i.champion_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND i.display_name != '' AND c.league = '{league}' AND c.region = '{region}'"
    if champion_name is not None: sql += f" AND ch.display_name = '{champion_name}'"
    data = get_sql_data(sql)

    ## Loop over sql result and group the champions and placements by their composition_id
    champ_dict = {}
    for champion in data:
        composition_id = champion['composition_id']
        champion_name = champion['champion_name']
        item_name = champion['item_name']
        placement = champion['placement']

        if composition_id not in champ_dict:
            champ_dict[composition_id] = {
                'placement': placement,
                'champions': {}
            }

        if champion_name not in champ_dict[composition_id]['champions']:
            champ_dict[composition_id]['champions'][champion_name] = []

        champ_dict[composition_id]['champions'][champion_name].append(item_name)

        result_dict = {}
        for composition_id, composition_data in champ_dict.items():
            placement = composition_data['placement']
            for champion_name, items in composition_data['champions'].items():
                if champion_name not in result_dict:
                    result_dict[champion_name] = {}

                for item_combination in combinations(items, n):
                    item_combination = ','.join(sorted(item_combination))  # Sort the combination and join into a string

                    if item_combination not in result_dict[champion_name]:
                        result_dict[champion_name][item_combination] = {
                            'occurrences': 0,
                            'total_placement': 0,
                        }

                    result_dict[champion_name][item_combination]['occurrences'] += 1
                    result_dict[champion_name][item_combination]['total_placement'] += placement

        # Calculate average placement
        for champion_name, item_combinations in result_dict.items():
            for item_combination, data in list(item_combinations.items()):  # Use list to avoid 'dictionary changed size during iteration' error
                if data['occurrences'] < min_counter:
                    del item_combinations[item_combination]  # Remove combinations that occurred less than 8 times
                else:
                    data['avg_placement'] = data['total_placement'] / data['occurrences']
                    del data['total_placement']  # Remove total_placement as it's no longer needed

    # Sort item combinations
    for champion_name, item_combinations in result_dict.items():
        sorted_combinations = sorted(item_combinations.items(), key=lambda x: (-x[1]['occurrences'], x[1]['avg_placement']))
        result_dict[champion_name] = {k: v for k, v in sorted_combinations}

    return result_dict