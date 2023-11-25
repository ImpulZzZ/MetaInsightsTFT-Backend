from core.models.mysql_utils import *
import itertools

def group_compositions_by_champions(patch, region, league, max_placement, min_counter, min_datetime, champion_name=None, combination_size=None):
    # Join compositions with champions and filter by parameters
    champions = get_sql_data(f"SELECT c.id AS composition_id, ch.display_name AS name, ch.tier AS tier, c.placement AS placement, c.patch AS patch FROM composition c JOIN champion ch ON c.id = ch.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND c.patch = '{patch}' AND c.league = '{league}' AND c.region = '{region}'")

    ## Loop over sql result and group the champions and placements by their composition_id
    champ_dict = {}
    for champion in champions:
        try: champ_dict[champion['composition_id']]['combination'].update( {champion['name'] : champion['tier']} )
        except KeyError: champ_dict.update( { 
            champion['composition_id']: {
                'combination': { champion['name'] : champion['tier'] },
                'placement': champion['placement']
                }
            } )


    ## Loop over the previously built dictionary and count similar occurences plus their placements.
    ## Stored in new dictionary with champions as key and counters as value
    grouped_compositions = {}
    for composition_id, composition_data in champ_dict.items():
        if champion_name is not None:
            try: composition_data['combination'][champion_name]
            except KeyError: continue

        placement = composition_data['placement']
        champion_combinations = []
        champion_combination = frozenset(composition_data['combination'].items())  # Use frozenset to make it hashable

        try:
            grouped_compositions[champion_combination]['counter'] += 1
            grouped_compositions[champion_combination]['placement_counter'] += placement
        except KeyError: grouped_compositions.update( { champion_combination: {'counter': 1, 'placement_counter': placement} } )

        ## If combination_size is set, limit the combination length to combination_size and build all possible combinations. Use frozenset to make it hashable as key
        if combination_size is not None:
            n_champion_combinations = itertools.combinations(composition_data['combination'].items(), combination_size)
            for champion_combination in n_champion_combinations:
                if champion_name is not None:
                    try: dict(champion_combination)[champion_name]
                    except KeyError: continue
                champion_combinations.append(frozenset(champion_combination))

        ## Per default, do not limit the combination length and use all champions
        else: champion_combinations.append(frozenset(composition_data['combination'].items()))

        for champion_combination in champion_combinations:
            try:
                grouped_compositions[champion_combination]['counter'] += 1
                grouped_compositions[champion_combination]['placement_counter'] += placement
            except KeyError: grouped_compositions.update( { champion_combination: {'counter': 1, 'placement_counter': placement} } )

    ## Sort the dictionary, so that the most occurences are first.
    ## If occurences are equal, put the one with lower placement counter above
    sorted_by_counter_and_placement = sorted(grouped_compositions.items(), key=lambda item: (item[1]["counter"], (-1 * item[1]["placement_counter"])), reverse=True)

    ## Lastly loop over sorted dictionary, compute average placement and built a result dictionary for api
    result = []
    for champion_combination, combination_data in sorted_by_counter_and_placement:
        combination_data.update({
            'combination': dict(champion_combination),
            'avg_placement': round(combination_data['placement_counter'] / combination_data['counter'], 2)
            })
        del combination_data['placement_counter']
        if combination_data['counter'] >= min_counter: result.append(combination_data)

    return result


def group_compositions_by_traits(patch, region, league, max_placement, max_avg_placement, min_counter, min_datetime, trait_name=None, combination_size=None, ignore_single_unit_traits=False):
    # Join compositions with traits and filter by parameters
    sql = f"SELECT c.id AS composition_id, t.display_name AS trait_name, t.style AS trait_style, c.placement AS placement, c.patch AS patch FROM composition c JOIN trait t ON c.id = t.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' AND c.patch = '{patch}' AND c.league = '{league}' AND c.region = '{region}'"
    if ignore_single_unit_traits: sql += " AND t.tier_total != 1"
    traits = get_sql_data(sql)

    ## Loop over sql result and group the traits and placements by their composition_id
    trait_dict = {}
    for trait in traits:
        try: trait_dict[trait['composition_id']]['combination'].update( {trait['trait_name'] : trait['trait_style']} )
        except KeyError: trait_dict.update( { 
            trait['composition_id']: {
                'combination': { trait['trait_name'] : trait['trait_style'] },
                'placement': trait['placement']
                }
            } )

    ## Loop over the previously built dictionary and count similar occurences plus their placements.
    ## Stored in new dictionary with traits as key and counters as value
    grouped_compositions = {}
    for composition_id, composition_data in trait_dict.items():
        placement = composition_data['placement']
        trait_combinations = []

        if trait_name is not None:
            try: composition_data['combination'][trait_name]
            except KeyError: continue

        ## If combination_size is set, limit the combination length to combination_size and build all possible combinations. Use frozenset to make it hashable as key
        if combination_size is not None:
            n_trait_combinations = itertools.combinations(composition_data['combination'].items(), combination_size)
            for trait_combination in n_trait_combinations:
                if trait_name is not None:
                    try: dict(trait_combination)[trait_name]
                    except KeyError: continue
                trait_combinations.append(frozenset(trait_combination))
                    
                
        ## Per default, do not limit the combination length and use all traits
        else: trait_combinations.append(frozenset(composition_data['combination'].items()))

        for trait_combination in trait_combinations:
            try:
                grouped_compositions[trait_combination]['counter'] += 1
                grouped_compositions[trait_combination]['placement_counter'] += placement
            except KeyError: grouped_compositions.update( { trait_combination: {'counter': 1, 'placement_counter': placement} } )

    ## Sort the dictionary, so that the most occurences are first.
    ## If occurences are equal, put the one with lower placement counter above
    sorted_by_counter_and_placement = sorted(grouped_compositions.items(), key=lambda item: (item[1]["counter"], (-1 * item[1]["placement_counter"])), reverse=True)

    ## Lastly loop over sorted dictionary, compute average placement and built a result dictionary for api
    result = []
    for trait_combination, combination_data in sorted_by_counter_and_placement:
        avg_placement = round(combination_data['placement_counter'] / combination_data['counter'], 2)
        if avg_placement > max_avg_placement: continue
        combination_data.update({
            'combination': dict(sorted(dict(trait_combination).items(), key=lambda item: (-item[1], item[0]))),
            'avg_placement': avg_placement
            })
        del combination_data['placement_counter']
        if combination_data['counter'] >= min_counter: result.append(combination_data)

    return result