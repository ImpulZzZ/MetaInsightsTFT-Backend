from core.models.mysql_utils import *
from itertools import combinations

def get_best_in_slot_items(champion_name, combination_size, patch, region, league, max_placement, min_counter, min_datetime):
    ## Join compositions with champions and items, and filter by parameters
    sql = f"SELECT c.id AS composition_id, ch.id as champion_id, ch.display_name AS champion_name, i.display_name AS item_name, c.placement AS placement FROM composition c JOIN champion ch ON c.id = ch.composition_id JOIN item i ON ch.id = i.champion_id WHERE c.placement <= {max_placement} AND c.patch = '{patch}' AND c.match_time >= '{min_datetime}' AND i.display_name != '' AND c.league = '{league}' AND c.region = '{region}' AND ch.display_name = '{champion_name}'"
    data = get_sql_data(sql)

    ## Loop over sql result and group the champions and placements by their composition_id
    champ_dict  = {}
    result_dict = {}
    for champion in data:
        composition_id = champion['composition_id']
        item_name = champion['item_name']
        placement = champion['placement']

        if composition_id not in champ_dict:
            champ_dict[composition_id] = {
                'placement': placement,
                'items': []
            }

        champ_dict[composition_id]['items'].append(item_name)

    for composition_id, composition_data in champ_dict.items():
        placement = composition_data['placement']
        items = composition_data['items']

        for item_combination in combinations(items, combination_size):
            item_combination = ','.join(sorted(item_combination))  # Sort the combination and join into a string

            if item_combination not in result_dict:
                result_dict[item_combination] = {
                    'occurrences': 0,
                    'total_placement': 0,
                }

            result_dict[item_combination]['occurrences'] += 1
            result_dict[item_combination]['total_placement'] += placement

    # Calculate average placement
    for item_combination, data in list(result_dict.items()):  # Use list to avoid 'dictionary changed size during iteration' error
        if data['occurrences'] < min_counter:
            del result_dict[item_combination]  # Remove combinations that occurred less than 8 times
        else:
            data['avg_placement'] = data['total_placement'] / data['occurrences']
            del data['total_placement']  # Remove total_placement as it's no longer needed

    # Sort item combinations
    sorted_combinations = sorted(result_dict.items(), key=lambda x: (-x[1]['occurrences'], x[1]['avg_placement']))
    result_dict = {k: v for k, v in sorted_combinations}

    return result_dict