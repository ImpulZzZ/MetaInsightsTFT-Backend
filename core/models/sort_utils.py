def sort_composition_groups_by_occurence_and_placement(composition_groups):
    return sorted(composition_groups, key=lambda x: (x.counter, (-1 * x.avg_placement)), reverse=True)

def sort_dict_by_occurence_and_placement(dictionary):
    return dict(sorted(dictionary.items(), key=lambda item: (item[1]["counter"], (-1 * item[1]["avg_placement"])), reverse=True))

def sort_players_by_rank(players):
    return sorted(players, key=lambda k: k['leaguePoints'], reverse=True)

def sort_champions_by_stars(champions):
    return sorted(champions, key=lambda x: x.tier, reverse=True)

def sort_dict_by_value(dictionary, descending):
    return sorted(dictionary.items(), key=lambda x: x[1], reverse=descending)