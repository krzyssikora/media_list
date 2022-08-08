import sys
import sqlite3
import re

from music_flask import utils, config, api
# from music_flask.config import _logger


class DBError(Exception):
    def __init__(self, error_message=None):
        if error_message:
            print(error_message)
        sys.exit(1)


def get_similar_artists(artist_dict, similarity_level=0.8):
    """
    Args:
        artist_dict:  includes at least one of the following keys: artist_name, artist_surname, artist_firstname
        similarity_level: only artists for which at least one field is similar on at least this level will be returned

    Returns:
        a list of dicts with artists similar to the one in question
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM artists''')
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    similar_artists = list()
    fields = {'artist_name', 'artist_surname', 'artist_firstname'}.intersection(f for f in artist_dict.keys()
                                                                                if artist_dict.get(f, None))
    for row in lines:
        artist_id, artist_type, artist_name, artist_surname, artist_firstname, artist_role, sort_name = row
        current_dict = {
            'artist_id': artist_id,
            'artist_type': artist_type,
            'artist_name': artist_name,
            'artist_surname': artist_surname,
            'artist_firstname': artist_firstname,
            'artist_role': artist_role,
            'sort_name': sort_name
        }
        current_similarity_ratio = max(utils.similarity_ratio(str(artist_dict[field]).lower(),
                                                              str(current_dict[field]).lower())
                                       for field in fields)
        if current_similarity_ratio >= similarity_level:
            current_dict['similarity'] = current_similarity_ratio
            similar_artists.append(current_dict)
    return similar_artists or None


def get_similar_artists_ids(artist_dict, similarity_level=0.8):
    """
    Args:
        artist_dict:  includes at least one of the following keys: artist_name, artist_surname, artist_firstname
        similarity_level: only artists for which at least one field is similar on at least this level will be returned

    Returns:
        a set of ids of artists similar to the one in question
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute('''SELECT * FROM artists''')
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    similar_artists_ids = set()
    fields = {'artist_name', 'artist_surname', 'artist_firstname'}.intersection(f for f in artist_dict.keys()
                                                                                if artist_dict.get(f, None))
    for row in lines:
        artist_id, artist_type, artist_name, artist_surname, artist_firstname, artist_role, sort_name = row
        current_dict = {
            'artist_id': artist_id,
            'artist_name': artist_name,
            'artist_surname': artist_surname,
            'artist_firstname': artist_firstname
        }
        current_similarity_ratio = max(utils.similarity_ratio(str(artist_dict[field]).lower(),
                                                              str(current_dict[field]).lower())
                                       for field in fields)
        if current_similarity_ratio >= similarity_level:
            similar_artists_ids.add(artist_id)
    return similar_artists_ids or None


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
        print('There is no table "{}" in the database.'.format(table))
        return

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
                table_keys = list(similar_artists[0].keys())
                table_keys.remove('similarity')
                # table_keys.append('similarity')
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


def get_albums_ids_by_medium(media):
    if media:
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        conditions = ' OR '.join(['medium="{}"'.format(medium) for medium in media])
        cur.execute("SELECT album_id FROM albums WHERE " + conditions)
        lines = cur.fetchall()
        conn.commit()
        cur.close()
        return set(line[0] for line in lines) or None
    else:
        return None


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
        if table_name == 'albums':
            conn = sqlite3.connect(config.DATABASE)
            cur = conn.cursor()
            # todo collect artists roles / functions, too (like: guitar, composer, bass OR writer, translator)
            #  - it needs artist role / function to be in albums_artists table;
            #  they could be then displayed in the form 'Mike Patton (vocal, keyboard), Tomasz Mann (writer)'
            cur.execute("""
                        SELECT artists.artist_name 
                        FROM albums_artists JOIN artists
                        ON albums_artists.artist_id = artists.artist_id
                        WHERE albums_artists.publ_role LIKE 'title%'
                        AND albums_artists.album_id = {}
                        """.format(idx))
            lines = cur.fetchall()
            lines = [line[0] for line in lines]
            record_dict['artist_name'] = ', '.join(lines)
            conn.commit()
            cur.close()
        return record_dict or None

    return None


def get_artist_by_id(idx):
    return get_record_by_id('artists', idx)


def get_album_by_id(idx):
    return get_record_by_id('albums', idx)


def get_artists_ids_from_album_id(album_id):
    """
    Args:
        album_id:

    Returns:
        a set of artist_ids with connections to album_id (in albums_artists table)
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT artist_id FROM albums_artists WHERE album_id = (?)", (album_id, ))
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    return {line[0] for line in lines} or None


def get_albums_ids_by_artist_id(artist_id):
    """
        Args:
            artist_id:

        Returns:
            a set of album_ids with connections to artist_id (in albums_artists table)
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT album_id FROM albums_artists WHERE artist_id = (?)", (artist_id,))
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    return {line[0] for line in lines} or None


def get_album_ids_by_title(album_title, similarity_level=0.8):
    """
    Args:
        album_title (str): album's name or its approximation
        similarity_level (float between 0 and 1): only albums with name similar on at least this level will be returned

    Returns:
        a list of album ids with name similar to album_title
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT album_id, album_title FROM albums")
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    # collect albums_ids
    albums_ids = set()
    for line in lines:
        if line[1] and utils.similarity_ratio(album_title, line[1]) >= similarity_level:
            albums_ids.add(line[0])
    return albums_ids or None


def get_albums_ids_by_title_or_artist(album_title=None, artist_name=None):
    album_title = album_title.strip() or None
    artist_name = artist_name.strip() or None
    if album_title is None and artist_name is None:
        # all in
        conn = sqlite3.connect(config.DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT album_id FROM albums")
        lines = cur.fetchall()
        albums_ids_by_title_and_artist = [line[0] for line in lines]
        conn.commit()
        cur.close()
    else:
        if album_title:
            album_title = album_title.strip()
            albums_ids_by_title = get_album_ids_by_title(album_title)
        else:
            albums_ids_by_title = set()

        if artist_name:
            artist_name = artist_name.strip()
            similar_artists_ids = get_similar_artists_ids({'artist_name': artist_name})
            albums_ids_by_artist = set().union(*[get_albums_ids_by_artist_id(artist_id)
                                                 for artist_id in similar_artists_ids])
        else:
            albums_ids_by_artist = set()

        if len(albums_ids_by_title) == 0 or len(albums_ids_by_artist) == 0:
            albums_ids_by_title_and_artist = albums_ids_by_title.union(albums_ids_by_artist)
        else:
            albums_ids_by_title_and_artist = albums_ids_by_title.intersection(albums_ids_by_artist)

    return albums_ids_by_title_and_artist or None


def get_albums_by_title_or_artist(album_title=None, artist_name=None, table=None):
    # we will not need this one later, we will just perform consecutive queries joining them with 'AND'
    """
    Args:
        album_title (str): approximation of an album title
        artist_name (str): approximation of the artist's name
        table: table of album ids already filtered

    Returns:
    A list of album dicts with artists' names added.
    """
    # get albums ids from table
    albums_ids = set() if table is None else table
    albums_ids_by_title_and_artist = get_albums_ids_by_title_or_artist(album_title, artist_name)
    # get full albums
    # add artists that perform on the albums
    albums = list()
    for idx in albums_ids_by_title_and_artist:
        # if table is None or idx in albums_ids:
        if idx in albums_ids:
            album = get_album_by_id(idx)
            if album:
                albums.append(album)
    # todo sort by sortname?
    return albums or None


def get_records_ids_from_query(table_name,
                               fields, values=None,
                               record_ids_already_chosen=None,
                               conjunction='AND'):
    # split fields from their values if given together
    if isinstance(fields, dict):
        fields_2 = list()
        values = list()
        for f, v in fields.items():
            fields_2.append(f)
            values.append(v)
    else:
        fields_2 = fields

    idx_name = utils.get_primary_key_name(table_name)

    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    conditions = ' AND '.join(str(field) + ' = ' + (('"' + str(value) + '"')
                                                    if isinstance(value, str) else str(value)) + ' '
                              for field, value in zip(fields_2, values) if value)
    cur.execute("SELECT {} FROM {} WHERE {}".format(idx_name, table_name, conditions))
    record_ids = cur.fetchall()
    conn.commit()
    cur.close()

    record_ids = set(record_ids)
    if record_ids_already_chosen:
        if conjunction == 'AND':
            record_ids = record_ids.intersection(record_ids_already_chosen)
        elif conjunction == 'OR':
            record_ids = record_ids.union(record_ids_already_chosen)

    return record_ids or None


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


def get_artists_from_album_id(album_id):
    # old, redundant?
    """
    Args:
        album_id:

    Returns:
        a list of artists (full dicts) with connections to album_id (in albums_artists table)
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT artist_id FROM albums_artists WHERE album_id = (?)", (album_id, ))
    lines = cur.fetchall()
    artists = list()
    for line in lines:
        cur.execute("SELECT * FROM artists WHERE artist_id = (?)", (line[0],))
        artist_line = cur.fetchone()
        artist_dict = utils.turn_tuple_into_dict(artist_line, config.DB_ARTISTS_COLUMNS)
        artists.append(artist_dict)
    conn.commit()
    cur.close()
    return artists


def get_albums_by_artist_id(artist_id):
    # old, redundant?
    """
        Args:
            artist_id:

        Returns:
            a list of albums (full dicts) with connections to artist_id (in albums_artists table)
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT album_id FROM albums_artists WHERE artist_id = (?)", (artist_id,))
    lines = cur.fetchall()
    albums = list()
    for line in lines:
        cur.execute("SELECT * FROM albums WHERE album_id = (?)", (line[0],))
        album_line = cur.fetchone()
        album_dict = utils.turn_tuple_into_dict(album_line, config.DB_ALBUMS_COLUMNS)
        albums.append(album_dict)
    conn.commit()
    cur.close()
    return albums


def get_albums_by_title(album_title, similarity_level=0.8):
    # old. redundant?
    """
    Args:
        album_title (str): album's name or its approximation
        similarity_level (float between 0 and 1): only albums with name similar on at least this level will be returned

    Returns:
        a list of albums (full dicts) with name similar to album_title
    """
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT album_id, album_title FROM albums")
    lines = cur.fetchall()
    conn.commit()
    cur.close()
    # collect albums_ids
    albums_ids = list()
    for line in lines:
        if line[1] and utils.similarity_ratio(album_title, line[1]) >= similarity_level:
            albums_ids.append(line[0])
    # get full album data
    conn = sqlite3.connect(config.DATABASE)
    cur = conn.cursor()
    albums = list()
    for album_id in albums_ids:
        cur.execute("SELECT * FROM albums WHERE album_id = (?)", (album_id, ))
        album_line = cur.fetchone()
        album_dict = utils.turn_tuple_into_dict(album_line, config.DB_ALBUMS_COLUMNS)
        albums.append(album_dict)
    conn.commit()
    cur.close()
    return albums


if __name__ == '__main__':
    print(get_db_columns())

# todo:
#   add tables:
#     albums_tracks with columns:
#       item_id, album_id, track_id, track_name, track_duration, notes
#     albums_tags with columns:  (change notes???)
#       item_id, album_id, tag
# todo: CRUD
#  create:
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
#    api.add_artist_to_album(album_title)
#  delete:
#    delete_record_from_table_by_id(table, idx)
#    api.delete_artist_from_db(artist_name)
#      check similar
#      remove also from albums_artists and bands_members
#    api.delete_album_from_db(album_title)
#      remove also from albums_artists
#      what about other parts if parts > 1? (default: remove all, any other option?)
