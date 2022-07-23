DATABASE="database/records_list.sqlite"
# DATABASE="database/records_list_tmp.sqlite"

# 0. descriptions of database fields
# 1. db field name
# 2. type of field
# 3. list of possible values or placeholder (default input) or empty string if the value is to be entered

NEW_ALBUM_FIELDS = [('type of record', 'type', list, ['various', 'jazz', 'OSTR', 'classics']),
                    ('number of parts', 'parts', int, 1),
                    ('type of an artist', 'main_artist_type', list, ['person', 'band', 'other', '']),
                    ('artist name', 'artist_name', str, ''),
                    ('artist firstname', 'artist_firstname', str, ''),
                    ('artist surname', 'artist_surname', str, ''),
                    ('artist role', 'artist_role', str, ''),
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

NEW_ARTIST_FIELDS = [('type of the artist', 'artist_type', list, ['person', 'band', 'other', '']),
                     ('name of the artist', 'artist_name', str, ''),
                     ('artist\'s surname', 'artist_surname', str, ''),
                     ('artist\'s firstname', 'artist_firstname', str, ''),
                     ('artist\'s role (what do they do)', 'artist_role', str, '')
                     ]

# ALBUM_FIELDS = [x[1] for x in NEW_ALBUM_FIELDS]

MATCH_NEW_ALBUM_FIELDS = [('artist name', 'artist_name', str, ''),
                    ('artist firstname', 'artist_firstname', str, ''),
                    ('artist surname', 'artist_surname', str, ''),
                    ('artist role', 'artist_role', str, ''),
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

