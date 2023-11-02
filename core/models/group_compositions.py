from core.models.mysql_utils import *

## Old version
# def group_compositions_by_items(compositions):
#     processed   = []
#     result      = []
#     num_comps   = len(compositions)
    
#     # loop over every composition
#     for x in range(0, num_comps):

#         # skip processed compositions
#         if x in processed: continue

#         # initialize new composition group with current composition
#         current_comp_group = [compositions[x]]

#         # compare each element x with y > x
#         for y in range(x+1, num_comps):
#             if compositions[x].champion_item_dict == compositions[y].champion_item_dict:
#                 current_comp_group.append(compositions[y])
#                 processed.append(y)
                        
#         result.append(CompositionGroup(current_comp_group))
    
#     return result

# def group_compositions_by_champions(compositions):
#     processed   = []
#     result      = []
#     num_comps   = len(compositions)
    
#     # loop over every composition
#     for x in range(0, num_comps):

#         # skip processed compositions
#         if x in processed: continue

#         # initialize new composition group with current composition
#         current_comp_group = [compositions[x]]

#         # compare each element x with y > x
#         for y in range(x+1, num_comps):
#             if compositions[x].champion_names == compositions[y].champion_names:
#                 current_comp_group.append(compositions[y])
#                 processed.append(y)
        
#         result.append(CompositionGroup(current_comp_group))
    
#     return result


def group_compositions_by_traits(max_placement, min_counter, min_datetime):
    # Join compositions with traits and filter by parameters
    traits = get_sql_data(f"SELECT c.id AS composition_id, c.patch AS patch, t.display_name AS trait_name, t.style AS trait_style, c.placement AS placement, c.match_time AS match_time FROM composition c JOIN trait t ON c.id = t.composition_id WHERE c.placement <= {max_placement} AND c.match_time >= '{min_datetime}' ORDER BY trait_name")

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
        trait_combination = frozenset(composition_data['trait_styles'].items())  # Use frozenset to make it hashable

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
        combination_data.update({
            'trait_styles': dict(trait_combination),
            'avg_placement': round(combination_data['placement_counter'] / combination_data['counter'], 2)
            })
        del combination_data['placement_counter']
        if combination_data['counter'] >= min_counter: result.append(combination_data)

    return result