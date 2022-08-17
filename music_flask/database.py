import sys
import sqlite3
import re

from music_flask_red import utils, config, api
from music_flask_red.config import _logger


class DBError(Exception):
    def __init__(self, error_message=None):
        if error_message:
            _logger.error(error_message)
        sys.exit(1)


def get_similar(table_name, item_dict, return_field=None, similarity_level=0.8):
    """
    Args:
        table_name: db table name
        item_dict: A dict whose keys are subset of table column names and values are supposed to be table entries
        return_field: A field which is to be returned.
                        If None - primary key will be returned.
                        If 'all' - whole dicts will be returned
        similarity_level: a float between 0 and 1, where 1 means that
                        each word from a shorter string is identical to a word in a longer string

    Returns:
        a set of entries from return_field column, or whole dicts
    """
    if return_field is None:
        return_field = utils.get_primary_key_name(table_name)
    table_column_names = config.DB_COLUMNS[table_name]
    fields = set(table_column_names).intersection(f for f in item_dict.keys() if item_dict.get(f, None))
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute('SELECT * FROM {}'.format(table_name))
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    similar_items = set()
    for row in lines:
        current_dict = dict()
        for c, r in zip(table_column_names, row):
            current_dict[c] = r
        current_similarity_ratio = max(utils.similarity_ratio(str(item_dict[field]).lower(),
                                                              str(current_dict[field]).lower())
                                       for field in fields)

        if current_similarity_ratio >= similarity_level:
            current_dict['similarity'] = current_similarity_ratio
            if return_field == 'all':
                similar_items.add(current_dict)
            else:
                similar_items.add(current_dict[return_field])
    return similar_items or set()


def get_similar_artists(artist_dict, similarity_level=0.8):
    return get_similar('artists', artist_dict, 'all', similarity_level=similarity_level)


def get_similar_albums(albums_dict, similarity_level=0.8):
    return get_similar('albums', albums_dict, 'all', similarity_level=similarity_level)


def get_similar_artists_ids(artist_dict, similarity_level=0.8):
    return get_similar('artists', artist_dict, 'artist_id', similarity_level=similarity_level)


def get_similar_albums_ids(album_dict, similarity_level=0.8):
    return get_similar('albums', album_dict, 'album_id', similarity_level=similarity_level)


def get_similar_artists_names(artist_dict, similarity_level=0.8):
    return get_similar('artists', artist_dict, 'artist_name', similarity_level=similarity_level)


def get_similar_album_titles(album_dict, similarity_level=0.8):
    return get_similar('albums', album_dict, 'album_title', similarity_level=similarity_level)


def add_record_to_table(record, table, artist_from_album=False):
    """
    Adds a record to db table.

    Args:
        record (dict): keys is a subset of table column names
        table (str): 'artists' or 'albums'
        artist_from_album (bool): True when it is artist to be added called from adding album.
            The user's input is compared with existing db records in 'artists' table.
            User is shown matching (similar) records.
            If called from adding artist (artist_from_album == False):
                user is to decide whether to add a new or not.
            If called from adding album (artist_from_album == True):
                user is to decide which artist from similar is the one they want, or add a new one.
    Returns:
        id of the added record (album_id or artist_id depending on the table)

    """

    def add_single_ready_record_to_table(rec, tab):
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        placeholder = ", ".join(['?'] * len(rec))
        stmt = "INSERT INTO {table} ({columns}) VALUES ({values});".format(table=tab,
                                                                           columns=",".join(rec.keys()),
                                                                           values=placeholder)
        cur.execute(stmt, list(rec.values()))
        conditions = ' AND '.join(str(k) + '="' + str(v) + '"' for k, v in rec.items() if v)
        primary_key = 'item_id' if 'item_id' in get_db_columns()[tab] else tab[:-1] + '_id'
        cur.execute("SELECT {idx} FROM {table} WHERE {conditions}".format(idx=primary_key,
                                                                          table=tab,
                                                                          conditions=conditions))
        idx = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return idx

    if table not in config.DB_TABLES:
        raise DBError('There is no table "{}" in the database.'.format(table))

    if table == 'artists':
        # "artists" - simple case
        # check if there is such an artist in the database
        similar_artists = get_similar_artists(record)
        add_record = True
        if similar_artists:
            if artist_from_album:
                artist_chosen = api.get_single_choice_from_db_list(choices=similar_artists,
                                                                   noun_singular='artist',
                                                                   sort_column='similarity')
                if artist_chosen:
                    return artist_chosen['artist_id']
            else:
                table_keys = list(list(similar_artists)[0].keys())
                table_keys.remove('similarity')
                # table_keys.append('similarity')
                # todo make api display the following - i.e. return it
                print('The following artists were found in the database:')
                print(utils.pretty_table_from_dicts(similar_artists, table_keys))
                decision = input('Do you still want to add the new artist (y/n)? ')
                add_record = decision in {'y', 'Y'}

        if add_record:
            return add_single_ready_record_to_table(record, table)
    # elif table == 'albums':
    else:
        return add_single_ready_record_to_table(record, table)
    return None


def get_db_columns():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    ret_dict = dict()
    for table in config.DB_TABLES:
        command = "SELECT sql FROM sqlite_master WHERE tbl_name = '{}' AND type = 'table'".format(table)
        cur.execute(command)
        my_string = cur.fetchall()[0][0].replace('\n', '')
        pattern = r'\((.+)\)'
        separated = re.search(pattern, my_string)[1].split(',')
        columns = [elt.strip().split()[0] for elt in separated]
        ret_dict[table] = columns
    conn.commit()
    cur.close()
    return ret_dict


def get_record_by_id(table_name, idx):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    idx_name = utils.get_primary_key_name(table_name)
    cur.execute("SELECT * FROM {} WHERE {} = (?)".format(table_name, idx_name), (idx, ))
    record = cur.fetchall()
    conn.commit()
    cur.close()
    if record:
        if len(record) > 1:
            raise DBError(table_name[:-1] + '_id = ' + str(idx) + ' is not unique!')
        record = record[0]
        record_dict = utils.turn_tuple_into_dict(record, config.DB_COLUMNS[table_name])
        return record_dict or dict()

    return dict()


def get_artist_by_id(idx):
    return get_record_by_id('artists', idx)


def get_album_by_id(idx):
    record_dict = get_record_by_id('albums', idx)
    if record_dict:
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        # todo collect artists roles / functions, too (like: guitar, composer, bass OR writer, translator)
        #  - it needs artist role / function to be in albums_artists table;
        #  they could be then displayed in the form 'Mike Patton (vocal, keyboard), Tomasz Mann (writer)'
        # cur.execute("""
        #             SELECT artists.artist_name
        #             FROM albums_artists JOIN artists
        #             ON albums_artists.artist_id = artists.artist_id
        #             WHERE albums_artists.publ_role LIKE 'title%'
        #             AND albums_artists.album_id = {}
        #             """.format(idx))
        # lines = cur.fetchall()
        # lines = [line[0] for line in lines]
        # record_dict['artist_name'] = lines
        # conn.commit()
        # cur.close()

        cur.execute("""
                            SELECT artists.artist_name, albums_artists.publ_role
                            FROM albums_artists JOIN artists
                            ON albums_artists.artist_id = artists.artist_id
                            AND albums_artists.album_id = {}
                            """.format(idx))
        # WHERE albums_artists.publ_role LIKE 'title%'
        lines = cur.fetchall()
        lines = ([line[0] for line in lines if line[1] == 'title'], [line[0] for line in lines if line[1] == 'other'])
        record_dict['artist_name'] = lines
        conn.commit()
        cur.close()
    return record_dict


def _get_albums_from_artist_names(fields_1, values_1):
    # get album ids from albums_artists table
    if isinstance(fields_1, dict):
        artist_name_value = fields_1.pop('artist_name')
    else:
        artist_name_idx = fields_1.index('artist_name')
        fields_1.remove('artist_name')
        artist_name_value = values_1.pop(artist_name_idx)
    artist_name_value = get_similar_artists_names({'artist_name': artist_name_value})

    albums_with_artists = set()
    for artist_name in artist_name_value:
        # get arist_id from artists table
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT artist_id FROM artists WHERE artist_name = (?)", (artist_name,))
        artists_ids = cur.fetchall()
        conn.commit()
        cur.close()
        # now get albums_ids for each of the artists
        if artists_ids:
            conn = sqlite3.connect(config.DATABASE)
            cur = conn.cursor()
            artists_ids = set(idx[0] for idx in artists_ids)
            for artist_id in artists_ids:
                cur.execute("SELECT album_id FROM albums_artists WHERE artist_id = (?)", (artist_id,))
                albums_ids = cur.fetchall()
                if albums_ids:
                    albums_with_artists = albums_with_artists.union(set(idx[0] for idx in albums_ids))
            conn.commit()
            cur.close()
    return albums_with_artists, fields_1, values_1


def _get_albums_from_title(fields_1, values_1):
    if isinstance(fields_1, dict):
        album_title_value = fields_1.pop('album_title')
    else:
        album_title_idx = fields_1.index('album_title')
        fields_1.remove('album_title')
        album_title_value = values_1.pop(album_title_idx)
    album_title_value = get_similar_album_titles({'album_title': album_title_value})

    albums_from_title = set()
    for album_title in album_title_value:
        # get album_id from albums table
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT album_id FROM albums WHERE album_title = (?)", (album_title,))
        albums_ids = cur.fetchall()
        conn.commit()
        cur.close()
        if albums_ids:
            albums_from_title = albums_from_title.union(set(idx[0] for idx in albums_ids))

    return albums_from_title, fields_1, values_1


def _get_fields_and_values_refactored(table_name, fields_1, values_1):
    # split fields from their values if given together
    albums_with_artists = None
    if table_name == 'albums' and 'artist_name' in fields_1:
        # get album ids from albums_artists table
        albums_with_artists, fields_1, values_1 = _get_albums_from_artist_names(fields_1, values_1)

    albums_from_title = None
    if table_name == 'albums' and 'album_title' in fields_1:
        # get album ids from its approx title
        albums_from_title, fields_1, values_1 = _get_albums_from_title(fields_1, values_1)

    if albums_with_artists is None and albums_from_title is None:
        albums_ids_from_artists_and_albums = None
    elif albums_with_artists is None or albums_from_title is None:
        albums_ids_from_artists_and_albums = (albums_with_artists or set()).union(albums_from_title or set())
    else:
        albums_ids_from_artists_and_albums = albums_with_artists.intersection(albums_from_title)

    if isinstance(fields_1, dict):
        fields_2 = list()
        values_2 = list()
        for field_1, value_1 in fields_1.items():
            # change value-list into a string
            if isinstance(value_1, list) and len(value_1) > 0:
                value_1 = ['(' + ' OR '.join(str(field_1) + ' = "' + str(v) + '"' for v in value_1) + ')']
                field_1 = ''
            fields_2.append(field_1)
            values_2.append(value_1)
    else:
        fields_2 = fields_1
        # change value-list into a string
        values_2 = list()
        for val_id, value_1 in enumerate(values_1):
            if isinstance(value_1, list) and len(value_1) > 0:
                values_2.append(
                    ['(' + ' OR '.join(str(fields_2[val_id]) + ' = "' + str(v) + '"' for v in value_1) + ')'])
                fields_2[val_id] = ''
            else:
                values_2.append(value_1)
    return fields_2, values_2, albums_ids_from_artists_and_albums


def get_records_ids_from_query(table_name,
                               fields, values=None,
                               record_ids_already_chosen=None,
                               conjunction='AND'):
    db_fields, db_values, albums_ids_from_artists_and_albums = \
        _get_fields_and_values_refactored(table_name, fields, values)
    idx_name = utils.get_primary_key_name(table_name)

    record_ids = None
    if db_fields:
        conditions = ' AND '.join(str(field)
                                  + (' = ' if field != '' else '')
                                  + (('"' + str(value) + '"')
                                     if isinstance(value, str) else
                                     (str(value[0]) if isinstance(value, list) else str(value))) + ' '
                                  for field, value in zip(db_fields, db_values) if value)

        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT {} FROM {} WHERE {}".format(idx_name, table_name, conditions))
        record_ids = cur.fetchall()
        conn.commit()
        cur.close()

        record_ids = set(idx[0] for idx in record_ids) if record_ids else set()

        if albums_ids_from_artists_and_albums is not None:
            record_ids = record_ids.intersection(albums_ids_from_artists_and_albums)
    elif albums_ids_from_artists_and_albums is not None:
        record_ids = albums_ids_from_artists_and_albums

    if record_ids_already_chosen is not None:
        if conjunction == 'AND':
            record_ids = record_ids.intersection(record_ids_already_chosen)
        elif conjunction == 'OR':
            record_ids = record_ids.union(record_ids_already_chosen)

    return record_ids or set()


def get_records_from_their_ids(table_name, records_ids):
    if records_ids:
        if table_name == 'albums':
            records = [get_album_by_id(idx) for idx in records_ids]
        elif table_name == 'artists':
            records = [get_artist_by_id(idx) for idx in records_ids]
        else:
            records = [get_record_by_id(table_name, idx) for idx in records_ids]
        return records or list()
    return list()


def get_records_from_query(table_name,
                           fields, values=None,
                           record_ids_already_chosen=None,
                           conjunction='AND'):
    records_ids = get_records_ids_from_query(table_name,
                                             fields, values,
                                             record_ids_already_chosen,
                                             conjunction) or set()
    return get_records_from_their_ids(table_name, records_ids)


def get_distinct_entries(table_name, field_name):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT {} FROM {} WHERE {} IS NOT NULL".format(field_name, table_name, field_name))
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    lines = [line[0] for line in lines]
    lines.sort()
    return lines


def update_records_field(table_name, record_dict, field, value):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    conditions = ' AND '.join(str(k) + '="' + str(v) + '"' for k, v in record_dict.items() if v)
    cur.execute("UPDATE {} SET {} = (?) WHERE {}".format(table_name, field, conditions), (value,))
    conn.commit()
    cur.close()


def update_records_fields(table_name, record_dict, fields, values):
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    conditions = ' AND '.join(str(k) + ' = ' + (('"' + str(v) + '"')
                                                if isinstance(v, str) else str(v)) + ' '
                              for k, v in record_dict.items() if v)
    set_fields = ', '.join([field + ' = (?)' for field in fields])
    cur.execute("UPDATE {} SET {} WHERE {}".format(table_name, set_fields, conditions), (*values,))
    conn.commit()
    cur.close()


def get_records(table_name, fields, values=None, return_as_tuples=False):
    # now used only in adding new album, redundant later?
    if isinstance(fields, dict):
        fields_2 = list()
        values = list()
        for f, v in fields.items():
            fields_2.append(f)
            values.append(v)
    else:
        fields_2 = fields

    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    conditions = ' AND '.join(str(field) + ' = ' + (('"' + str(value) + '"')
                                                    if isinstance(value, str) else str(value)) + ' '
                              for field, value in zip(fields_2, values) if value)
    cur.execute("SELECT * FROM {} WHERE {}".format(table_name, conditions))
    records = cur.fetchall()
    conn.commit()
    cur.close()
    if return_as_tuples:
        return records or None
    dicts_list = list()
    table_columns = config.DB_COLUMNS[table_name]
    for record in records:
        record_dict = dict()
        for idx in range(len(table_columns)):
            field_value = record[idx]
            if field_value:
                record_dict[table_columns[idx]] = field_value
        dicts_list.append(record_dict)
    return dicts_list or None


def dummy():
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT")
    conn.commit()
    cur.close()


# METHODS FOR SAVING QUERIES DATABASE


def save_query(query_dict):
    keys = config.QUERY_COLUMNS_TO_DB
    conn = sqlite3.connect(config.DATABASE_QUERIES)
    cur = conn.cursor()
    for key, value in query_dict.items():
        query_dict[key] = str(value)
    conditions_without_name = ' AND '.join('{} = "{}"'.format(keys.get(key, key), value)
                                           if value else '{} IS NULL'.format(keys.get(key, key))
                                           for key, value in query_dict.items()
                                           if key != 'name'
                                           )
    cur.execute("SELECT * FROM queries WHERE {}".format(conditions_without_name))
    line = cur.fetchone()
    if line:
        return_message = 'This query is already saved as "{}".'.format(line[1])
    else:
        if 'name' not in query_dict or query_dict['name'] is None or query_dict['name'].strip() == '':
            cur.execute("SELECT COUNT(*) FROM queries")
            new_query_number = cur.fetchone()[0] + 1
            query_dict['name'] = 'query no.{}'.format(new_query_number)
        keys = config.QUERY_COLUMNS_TO_DB
        columns = [key for key, value in query_dict.items() if value]
        placeholder = ', '.join(['?'] * len(columns))
        values = tuple(query_dict[key] for key in columns)
        cur.execute("INSERT INTO queries ({columns}) VALUES ({placeholder})".format(
            columns=', '.join(keys.get(key, key) for key in columns),
            placeholder=placeholder),
                    values)
        return_message = "New query saved."
    conn.commit()
    cur.close()
    return return_message


def delete_query(query):
    if 'medium' in query:
        query['medium'] = eval(query['medium'])
    keys = config.QUERY_COLUMNS_TO_DB
    conditions = ' AND '.join('{}={}'.format(keys.get(k, k), v if isinstance(v, int) else '"{}"'.format(v))
                              for k, v in query.items() if v)
    conn = sqlite3.connect(config.DATABASE_QUERIES)
    cur = conn.cursor()
    cur.execute("SELECT * FROM queries WHERE {}".format(conditions))
    line = cur.fetchone()
    if line:
        cur.execute("DELETE FROM queries WHERE query_id={}".format(query['id']))
    conn.commit()
    cur.close()


def get_queries_from_database():
    conn = sqlite3.connect(config.DATABASE_QUERIES)
    cur = conn.cursor()
    cur.execute("SELECT * FROM queries")
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    query_dicts = list()
    keys = config.QUERY_COLUMNS
    for line in lines:
        query_dict = {key: value for key, value in zip(keys, line) if value}
        query_dicts.append(query_dict)
    return query_dicts


def initialize():
    conn = sqlite3.connect(config.DATABASE_QUERIES)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS queries
        (query_id INTEGER PRIMARY KEY, query_name TEXT, 
        artist_name TEXT, album_title TEXT, publisher TEXT, medium TEXT, 
        date_orig TEXT, date_publ TEXT, notes TEXT, genre TEXT)
        ''')
    conn.commit()
    cur.close()


def dummy_query():
    conn = sqlite3.connect(config.DATABASE_QUERIES)
    cur = conn.cursor()
    cur.execute("SELECT")
    conn.commit()
    cur.close()


if __name__ == '__main__':
    initialize()
    quit()
    print(get_db_columns())


# todo: remove redundant methods
# todo:
#   add tables:
#     albums_tracks with columns:
#       item_id, album_id, track_id, track_name, track_duration, notes
#     albums_tags with columns:  (change notes???)
#       item_id, album_id, tag
#       list of allowed tags: copy, missing, ...
# todo: CRUD
#  create:  DONE, but in terminal mode only
#    ::DONE:: api.add_album_to_table()
#    ::DONE:: api.add_artist_to_table()
#  read:
#    api.view_all()
#    api.view_albums()
#    api.view_artists()
#    api.query() - like all artists who played with...
#  update:
#    api.edit_album()
#      choice by album_title or artist_name
#    api.edit_artist(artist_name)
#    api.add_band_members(band_name)
#      this should be a part of adding artist if it is a band
#      this should update albums_artists, too
#      this should change adding album
#    api.add_artist_to_album(album_title)
#  delete:
#    delete_record_from_table_by_id(table, idx)
#    api.delete_artist_from_db(artist_name)
#      check similar
#      remove also from albums_artists and bands_members
#    api.delete_album_from_db(album_title)
#      remove also from albums_artists
#      what about other parts if parts > 1? (default: remove all, any other option?)
