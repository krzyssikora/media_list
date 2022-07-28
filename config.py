import logging

# DATABASE = "database/records_list.sqlite"
DATABASE = "database/records_list_tmp.sqlite"

DB_TABLES = {'artists', 'albums'}  # tables that can be accessed by a user

# 0. descriptions of database fields
# 1. db field name
# 2. type of field
# 3. list of possible values or placeholder (default input) or empty string if the value is to be entered

NEW_ALBUM_FIELDS = [('type of music', 'type', list, ('various', 'jazz', 'OSTR', 'classics')),
                    ('number of parts', 'parts', int, 1),
                    # ('type of an artist', 'main_artist_type', list, ['person', 'band', 'other', '']),
                    ('artist\'s name', 'artist_name', str, ''),
                    # 'sort name': 'sort_name',
                    ('album title', 'album_title', str, ''),
                    ('content', 'content', str, ''),
                    ('publisher', 'publisher', str, ''),
                    ('medium', 'medium', list, ['CD', 'vinyl', 'DVD', 'blu-ray', '']),
                    ('recording date', 'date_orig', str, 'YYYY/MM/DD'),
                    ('publication date', 'date_publ', str, 'YYYY/MM/DD'),
                    ('notes', 'notes', str, ''),
                    # https://en.wikipedia.org/wiki/List_of_music_genres_and_styles
                    ('genre', 'genre', set, ('', 'classics', 'jazz', 'blues', 'country',
                                             'rock', 'metal', 'techno', 'electronic',
                                             'easy', 'experimental', 'folk', 'hip hop',
                                             'pop', 'r&b, soul', 'punk', 'World'))
                    ]

NEW_ARTIST_FIELDS = [('type of the artist', 'artist_type', list, ['person', 'band', 'other', '']),
                     ('artist\'s name', 'artist_name', str, ''),
                     ('artist\'s surname', 'artist_surname', str, ''),
                     ('artist\'s firstname', 'artist_firstname', str, ''),
                     ('artist\'s role (what do they do)', 'artist_role', str, '')
                     ]

DB_ARTISTS_COLUMNS = [
    'artist_id',
    'artist_type',
    'artist_name',
    'artist_surname',
    'artist_firstname',
    'artist_role',
    'sort_name'
]

DB_ALBUMS_COLUMNS = [
    'album_id',
    'parts',
    'part_id',
    'first_part_id',
    'artist_name',
    'sort_name',
    'album_title',
    'content',
    'publisher',
    'medium',
    'date_orig',
    'date_publ',
    'notes',
    'type',
    'genre',
    'main_artist_id'
]

DB_COLUMNS = {'albums': DB_ALBUMS_COLUMNS,
              'artists': DB_ARTISTS_COLUMNS}

# todo: do we need this? only to compare album being added to existing ones?
MATCH_NEW_ALBUM_FIELDS = [('artist\'s name', 'artist_name', str, ''),
                          # ('artist\'s firstname', 'artist_firstname', str, ''),
                          # ('artist\'s surname', 'artist_surname', str, ''),
                          ('artist\'s role', 'artist_role', str, ''),
                          # 'sort name': 'sort_name',
                          ('album title', 'album_title', str, ''),
                          ('content', 'content', str, ''),
                          ('publisher', 'publisher', str, ''),
                          ('medium', 'medium', list, ['CD', 'vinyl', 'DVD', 'blu-ray', '']),
                          ('recording date', 'date_orig', str, 'YYYY/MM/DD'),
                          ('publication date', 'date_publ', str, 'YYYY/MM/DD'),
                          ('notes', 'notes', str, ''),
                          # https://en.wikipedia.org/wiki/List_of_music_genres_and_styles
                          ('genre', 'genre', set, ['', 'classical', 'jazz', 'blues', 'country',
                                                   'rock', 'metal', 'techno', 'electronic',
                                                   'easy', 'experimental', 'folk', 'hip hop',
                                                   'pop', 'r&b, soul', 'punk', 'World'])
                          ]

# create logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
_logger.addHandler(ch)
