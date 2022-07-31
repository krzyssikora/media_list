from difflib import SequenceMatcher
from prettytable import PrettyTable


def turn_tuple_into_dict(the_tuple, the_keys):
    the_dict = dict()
    for key_id, key in enumerate(the_keys):
        value = the_tuple[key_id]
        if value:
            the_dict[key] = value
    return the_dict


def similarity_ratio_for_words(a, b):
    return SequenceMatcher(None, a, b).ratio()


def _get_ratio_and_remove_best_match(word_a, words_b):
    max_ratio = 0
    best_word_b = None
    for word_b in words_b:
        ratio = similarity_ratio_for_words(word_a, word_b)
        if ratio > max_ratio:
            max_ratio = ratio
            best_word_b = word_b
    if best_word_b:
        words_b.remove(best_word_b)
    return max_ratio, words_b


def similarity_ratio(sentance_a, sentance_b):
    from statistics import mean
    words_a = sentance_a.split()
    words_b = sentance_b.split()
    min_len = min(len(words_a), len(words_b))
    ratios = list()
    for id_a, a in enumerate(words_a):
        ratio_a, words_b = _get_ratio_and_remove_best_match(a, words_b)
        ratios.append(ratio_a)
    ratios.sort(reverse=True)
    ratios = ratios[:min_len]
    return mean(ratios)


def pretty_table_from_dicts(dicts, column_names=None, max_column_width=None):
    """
    creates a nice table with values from each dict displayed in a separate row
    Args:
        dicts: a single dict or a list of dicts
        column_names (list): keys from the dicts, may be a subset or a superset
        max_column_width (int): maximum width of a column
    Returns:
        a string with a nice table
    """
    if isinstance(dicts, dict):
        dicts = [dicts]

    table = PrettyTable()
    table.align = 'l'
    if column_names is None:
        column_names = set().union(set(row_dict.keys()) for row_dict in dicts)
    non_empty_columns = [column for column in column_names if any(row.get(column, None) for row in dicts)]
    table.field_names = non_empty_columns
    for row_dict in dicts:
        row = [row_dict.get(column, '') or '' for column in non_empty_columns]
        if max_column_width:
            row = [str(elt)[:max_column_width] for elt in row]
        table.add_row(row)
    return table


def pretty_table_from_tuples(tuples, column_names=None, max_column_width=None):
    """
    creates a nice table with values from each tuple displayed in a separate row
    Args:
        tuples: a single tuple or a list of tuples
        column_names (list): keys from the dicts, may be a subset or a superset
        max_column_width (int): maximum width of a column
    Returns:
        a string with a nice table
    """
    if isinstance(tuples, tuple):
        tuples = [tuples]

    table = PrettyTable()
    table.align = 'l'
    if column_names is None:
        column_names = [i for i in range(len(tuples[0]))]

    non_empty_column_indices = [i for i in range(len(column_names)) if any(row[i] for row in tuples)]
    table.field_names = [column_names[i] for i in non_empty_column_indices]
    for row_tuple in tuples:
        row = [elt if elt else '' for elt in row_tuple]
        row = [row[i] for i in non_empty_column_indices]
        if max_column_width:
            row = [str(elt)[:max_column_width] for elt in row]
        table.add_row(row)
    return table
