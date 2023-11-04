from core.models.mysql_utils import *
import itertools

def group_compositions_by_champions(max_placement, min_counter, min_datetime):
    # Join compositions with traits and filter by parameters
    champions = get_sql_data(f"SELECT c.id AS composition_id, ch.display_name AS name, ch.tier AS tier, c.placement AS placement FROM composition c JOIN champion ch ON c.id = ch.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}'")

    ## Loop over sql result and group the champions and placements by their composition_id
    champ_dict = {}
    for champion in champions:
        try: champ_dict[champion['composition_id']]['champion_tiers'].update( {champion['name'] : champion['tier']} )
        except KeyError: champ_dict.update( { 
            champion['composition_id']: {
                'champion_tiers': { champion['name'] : champion['tier'] },
                'placement': champion['placement']
                }
            } )


    ## Loop over the previously built dictionary and count similar occurences plus their placements.
    ## Stored in new dictionary with champions as key and counters as value
    grouped_compositions = {}
    for composition_id, composition_data in champ_dict.items():
        placement = composition_data['placement']
        champion_combination = frozenset(composition_data['champion_tiers'].items())  # Use frozenset to make it hashable

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
            'champion_tiers': dict(champion_combination),
            'avg_placement': round(combination_data['placement_counter'] / combination_data['counter'], 2)
            })
        del combination_data['placement_counter']
        if combination_data['counter'] >= min_counter: result.append(combination_data)

    return result


def group_compositions_by_traits(max_placement, max_avg_placement, min_counter, min_datetime, trait_name=None, n_traits=None, ignore_single_unit_traits=False):
    # Join compositions with traits and filter by parameters
    sql = f"SELECT c.id AS composition_id, t.display_name AS trait_name, t.style AS trait_style, c.placement AS placement FROM composition c JOIN trait t ON c.id = t.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}'"
    if ignore_single_unit_traits: sql += " AND t.tier_total != 1"
    traits = get_sql_data(sql)

    ## Loop over sql result and group the traits and placements by their composition_id
    trait_dict = {}
    for trait in traits:
        try: trait_dict[trait['composition_id']]['trait_styles'].update( {trait['trait_name'] : trait['trait_style']} )
        except KeyError: trait_dict.update( { 
            trait['composition_id']: {
                'trait_styles': { trait['trait_name'] : trait['trait_style'] },
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
            try: composition_data['trait_styles'][trait_name]
            except KeyError: continue

        ## If n_traits is set, limit the combination length to n_traits and build all possible combinations. Use frozenset to make it hashable as key
        if n_traits is not None:
            n_trait_combinations = itertools.combinations(composition_data['trait_styles'].items(), n_traits)
            for trait_combination in n_trait_combinations:
                if trait_name is not None:
                    try: dict(trait_combination)[trait_name]
                    except KeyError: continue
                trait_combinations.append(frozenset(trait_combination))
                    
                
        ## Per default, do not limit the combination length and use all traits
        else: trait_combinations.append(frozenset(composition_data['trait_styles'].items()))

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
            'trait_styles': dict(trait_combination),
            'avg_placement': avg_placement
            })
        del combination_data['placement_counter']
        if combination_data['counter'] >= min_counter: result.append(combination_data)

    return result