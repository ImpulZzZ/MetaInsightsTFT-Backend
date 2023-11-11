from core.models.mysql_utils import *

def get_item_placements(item_name, region, league, max_placement, min_counter, min_datetime):
    # Join compositions with champions and items, and filter by parameters
    sql = f"SELECT c.id AS composition_id, i.display_name AS item_name, c.placement AS placement FROM composition c JOIN champion ch ON c.id = ch.composition_id JOIN item i ON ch.id = i.champion_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND i.display_name != '' AND c.league = '{league}' AND c.region = '{region}'"
    if item_name is not None: sql += f" AND i.display_name = '{item_name}'"
    items = get_sql_data(sql)

    # Loop over sql result and group the items and placements by their composition_id
    item_dict = {}
    for item in items:
        item_name = item['item_name']
        try: 
            item_dict[item_name]['counter'] += 1
            item_dict[item_name]['placement_counter'] += item['placement']
        except KeyError: 
            item_dict[item_name] = {'counter': 1, 'placement_counter': item['placement']}

    # Calculate average placement for each item, round it to 2 decimals and remove placement_counter
    for item_name, item_data in item_dict.items():
        item_data['avg_placement'] = round(item_data['placement_counter'] / item_data['counter'], 2)
        del item_data['placement_counter']

    # Filter out items with counter less than min_counter
    filtered_items = {item_name: item_data for item_name, item_data in item_dict.items() if item_data['counter'] >= min_counter}

    # Sort the dictionary by average placement
    sorted_items = sorted(filtered_items.items(), key=lambda x: x[1]['avg_placement'])

    return dict(sorted_items)


def get_champion_placements(champion_name, region, league, max_placement, min_datetime):
    # Join compositions with champions, and filter by parameters
    sql = f"SELECT c.id AS composition_id, ch.display_name AS champion_name, ch.tier AS champion_tier, c.placement AS placement FROM composition c JOIN champion ch ON c.id = ch.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND c.league = '{league}' AND c.region = '{region}'"
    if champion_name is not None: sql += f" AND ch.display_name = '{champion_name}'"
    champions = get_sql_data(sql)

    # Loop over sql result and group the champions, tiers and placements by their composition_id
    champion_dict = {}
    for champion in champions:
        champion_name = champion['champion_name']
        champion_tier = champion['champion_tier']
        if champion_name not in champion_dict:
            champion_dict[champion_name] = {}
        if champion_tier not in champion_dict[champion_name]:
            champion_dict[champion_name][champion_tier] = {'counter': 0, 'placement_counter': 0}
        champion_dict[champion_name][champion_tier]['counter'] += 1
        champion_dict[champion_name][champion_tier]['placement_counter'] += champion['placement']

    # Calculate average placement for each champion tier and remove placement_counter
    for champion_name, champion_data in champion_dict.items():
        for champion_tier, tier_data in champion_data.items():
            tier_data['avg_placement'] = round(tier_data['placement_counter'] / tier_data['counter'], 2)
            del tier_data['placement_counter']

    return champion_dict


def get_trait_placements(trait_name, region, league, max_placement, min_datetime):
    # Join compositions with champions, and filter by parameters
    sql = f"SELECT c.id AS composition_id, t.display_name AS trait_name, t.style AS trait_style, c.placement AS placement FROM composition c JOIN trait t ON c.id = t.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND c.league = '{league}' AND c.region = '{region}'"
    if trait_name is not None: sql += f" AND ch.display_name = '{trait_name}'"
    traits = get_sql_data(sql)

    # Loop over sql result and group the traits, styles and placements by their composition_id
    trait_dict = {}
    for trait in traits:
        trait_name = trait['trait_name']
        trait_style = trait['trait_style']
        if trait_name not in trait_dict:
            trait_dict[trait_name] = {}
        if trait_style not in trait_dict[trait_name]:
            trait_dict[trait_name][trait_style] = {'counter': 0, 'placement_counter': 0}
        trait_dict[trait_name][trait_style]['counter'] += 1
        trait_dict[trait_name][trait_style]['placement_counter'] += trait['placement']

    # Calculate average placement for each trait style and remove placement_counter
    for trait_name, trait_data in trait_dict.items():
        for trait_style, style_data in trait_data.items():
            style_data['avg_placement'] = round(style_data['placement_counter'] / style_data['counter'], 2)
            del style_data['placement_counter']

    return trait_dict