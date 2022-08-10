from difflib import SequenceMatcher
from prettytable import PrettyTable
from music_flask import config
from music_flask.config import _logger


def turn_tuple_into_dict(the_tuple, the_keys):
    the_dict = dict()
    for key_id, key in enumerate(the_keys):
        value = the_tuple[key_id]
        if value:
            the_dict[key] = value
    return the_dict


def get_html_from_table(dicts, keys,
                        clickable_columns=('title', 'artist /-s', 'medium'),
                        sort_keys=('sort_name', 'date_orig', 'date_publ', 'album_title', 'part')):
    def wrap_with_tag(text, tag, dom_elt_id=None):
        html_id = ''
        if dom_elt_id:
            html_id = ' id="{}"'.format(dom_elt_id)
        return f'<{tag}{html_id}> {text} </{tag}>'

    def get_table_cell(cell_content, row_id, column_id, cell_tag='td'):
        if column_id in indexes_of_clickable_columns:
            html_id = 'query_{}_{}'.format(row_id, column_id)
            if isinstance(cell_content, list):
                html_cell_elements = list()
                for elt in cell_content:
                    single_html_id = html_id + '_' + '***'.join(elt.split())
                    html_cell_elements.append(wrap_with_tag(elt, 'span', single_html_id))
                    html_dom_ids.add((row_id, column_id, elt))
                cell_string = wrap_with_tag(', '.join(html_cell_elements), cell_tag)
            else:
                cell_string = wrap_with_tag(cell_content, cell_tag, html_id)
                html_dom_ids.add((row_id, column_id))
        else:
            if isinstance(cell_content, list):
                cell_string = wrap_with_tag(', '.join(cell_content), cell_tag)
            else:
                cell_string = wrap_with_tag(cell_content, cell_tag)
        # cell_string = wrap_with_tag(cell_string, cell_tag)
        return cell_string

    def get_table_row(row_content, row_id, row_tag='tr'):
        row_string = ''
        for column_id, cell_content in enumerate(row_content):
            row_string += get_table_cell(cell_content, row_id, column_id)
        row_string = wrap_with_tag(row_string, row_tag)
        return row_string

    table = turn_dicts_into_list_of_tuples_for_html(dicts, keys, sort_keys)
    table_header = table[0]
    html_dom_ids = set()
    table_rows = table[1:]
    clickable_columns = [col for col in clickable_columns if col in table_header]
    indexes_of_clickable_columns = [table_header.index(col) for col in clickable_columns]
    html_table_string = ''
    # header row
    for cell_text in table_header:
        html_table_string += wrap_with_tag(cell_text, 'th')
    html_table_string = wrap_with_tag(html_table_string, 'tr')
    # other rows
    for idx, row in enumerate(table_rows):
        html_table_string += get_table_row(row, idx + 1)
    html_table_string = wrap_with_tag(html_table_string, 'table')

    return table, html_table_string, html_dom_ids


def turn_dicts_into_list_of_tuples_for_html(dicts, keys,
                                            sort_keys=('sort_name', 'date_orig', 'date_publ', 'album_title', 'part')):
    dicts = dicts or []
    non_empty_keys = list()
    display_keys = ['#']
    for key in keys:
        display_key = config.DISPLAY_COLUMNS.get(key, None) \
            if any(str(row.get(key, '')).strip() for row in dicts) else None
        if display_key:
            non_empty_keys.append(key)
            display_keys.append(display_key)

    # change dicts into tuples
    table = list()
    for row_dict in dicts:
        table.append(tuple([''] + [str(row_dict.get(key, '')) + '/' + str(row_dict.get('parts', ''))
                           if (key == 'part_id' and row_dict.get('parts', None))
                           else row_dict.get(key, '') for key in non_empty_keys]))
    # sort them
    if sort_keys:
        sorting_keys = [config.DISPLAY_COLUMNS[k] for k in sort_keys if k in non_empty_keys]
        sorting_ids = [display_keys.index(k) for k in sorting_keys]
        sorting_ids.reverse()
        for idx in sorting_ids:
            table.sort(key=lambda x: x[idx])
    # add numbering
    final_table = [tuple(display_keys)]
    for idx, row in enumerate(table):
        final_table.append(tuple((idx + 1,) + row[1:]))
    return final_table


def turn_dicts_to_list_of_tuples(dicts, keys):
    table = list()
    table.append(keys)
    for row_dict in dicts:
        table.append(tuple(row_dict.get(key, '') for key in keys))
    return table


def similarity_ratio_for_words(a, b):
    # a = clear_word(a)
    # b = clear_word(b)
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


def similarity_ratio(sentence_a, sentence_b):
    from statistics import mean

    def clear_string(string):
        string = string.lower()
        for char in '.,/\\!@#$%^&*()[]{};:\'\"-_=+':
            string = string.replace(char, ' ')
        return string

    sentence_a = clear_string(sentence_a)
    sentence_b = clear_string(sentence_b)
    words_a = sentence_a.split()
    words_b = sentence_b.split()
    min_len = min(len(words_a), len(words_b))
    ratios = list()
    for id_a, a in enumerate(words_a):
        ratio_a, words_b = _get_ratio_and_remove_best_match(a, words_b)
        ratios.append(ratio_a)
    ratios.sort(reverse=True)
    ratios = ratios[:min_len]
    return mean(ratios) if ratios else 0


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


def get_primary_key_name(table_name):
    if table_name in {'albums', 'artists'}:
        return table_name[:-1] + '_id'
    else:
        return 'item_id'


if __name__ == '__main__':
    print(similarity_ratio('to be or not', '   '))
