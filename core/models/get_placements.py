from core.models.mysql_utils import *

def get_item_placements(item_name, max_placement, min_counter, min_datetime):
    # Join compositions with champions and items, and filter by parameters
    sql = f"SELECT c.id AS composition_id, i.display_name AS item_name, c.placement AS placement FROM composition c JOIN champion ch ON c.id = ch.composition_id JOIN item i ON ch.id = i.champion_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND i.display_name != ''"
    if item_name is not None: sql += f" AND i.display_name = '{item_name}'"
    items = get_sql_data(sql)

    # Loop over sql result and group the items and placements by their composition_id
    item_dict = {}
    for item in items:
        try: 
            item_dict[item['item_name']]['counter'] += 1
            item_dict[item['item_name']]['placement_counter'] += item['placement']
        except KeyError: 
            item_dict[item['item_name']] = {'counter': 1, 'placement_counter': item['placement']}

    # Calculate average placement for each item, round it to 2 decimals and remove placement_counter
    for item_name, item_data in item_dict.items():
        item_data['avg_placement'] = round(item_data['placement_counter'] / item_data['counter'], 2)
        del item_data['placement_counter']

    # Filter out items with counter less than min_counter
    filtered_items = {item_name: item_data for item_name, item_data in item_dict.items() if item_data['counter'] >= min_counter}

    # Sort the dictionary by average placement
    sorted_items = sorted(filtered_items.items(), key=lambda x: x[1]['avg_placement'])

    return dict(sorted_items)