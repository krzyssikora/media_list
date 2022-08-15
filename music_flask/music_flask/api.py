import os
import msvcrt as m

from music_flask import config, utils, database
from music_flask.config import _logger


def take_char():
    # works on win only
    a = ord(m.getch())
    if a == 224:
        b = ord(m.getch())
    elif a == 0:
        b = ord(m.getch())
    else:
        b = -1
    return a, b


def clear_screen():
    """Clears the terminal screen."""
    # return
    if os.name == 'posix':
        # mac, linux
        _ = os.system('clear')
    else:
        # for windows
        _ = os.system('cls')


def get_user_input(message="Please enter", default='', intro='', do_clear_screen=True):
    """Collects a string from a user.

    Args:
        message (str): A message to be printed when a user is asked for the input.
        default (str): Default value of the input, printed for user's verification.
        intro (str): Introduction message to display
        do_clear_screen (bool): if True, screen is cleared when the method starts

    """
    if do_clear_screen:
        clear_screen()
    if intro:
        print(intro)
    return_string = input(message + ": {}".format(default) + chr(8)*len(str(default)))
    if not return_string:
        return_string = '' if default == 'YYYY/MM/DD' else default
    return return_string


def get_single_choice_from_list(choices, intro='', do_clear_screen=True):
    """
    Prompts user to choose a value from a list until a choice is made.
    Args:
        choices (list):  items to choose from.
        intro (str): a message displayed
        do_clear_screen (bool): if True, screen is cleared when the method starts

    Returns:
        the choice made by the user, whatever type of object it was
    """
    while True:
        if do_clear_screen:
            clear_screen()
        if intro:
            print(intro)
        for idx, choice in enumerate(choices):
            print(str(idx + 1).rjust(len(str(len(choices))) + 1) + ': ' + str(choice))
        users_choice = input('your choice: ')
        if users_choice.isdigit():
            users_choice = int(users_choice)
            if 1 <= users_choice <= len(choices):
                return choices[users_choice - 1]


def get_single_choice_from_db_list(choices, noun_singular, noun_plural=None, sort_column=None):
    if noun_plural is None:
        noun_plural = noun_singular + 's'
    number_of_choices = len(choices)
    table_keys = list(choices[0].keys())
    if sort_column:
        table_keys.remove(sort_column)
    object_chosen = None
    if number_of_choices == 1:
        print('The following {} was found in the database.'.format(noun_singular))
        print(utils.pretty_table_from_dicts(choices, table_keys))
        decision = input('Is it the {} (y/n)? '.format(noun_singular))
        if decision in {'y', 'Y'}:
            object_chosen = choices[0]
    else:
        if sort_column:
            choices.sort(key=lambda x: x[sort_column], reverse=True)
        for idx, art in enumerate(choices):
            art['ord'] = idx + 1
        table_keys.insert(0, 'ord')
        print('The following {} were found in the database.'.format(noun_plural))
        print(utils.pretty_table_from_dicts(choices, table_keys))
        while True:
            decision = input('Choose the correct {} (1-{}) '
                             'or 0 if it is not on the list. '.format(noun_singular, number_of_choices))
            if decision.isdigit():
                decision = int(decision)
                if 1 <= decision <= number_of_choices:
                    object_chosen = choices[decision - 1]
                    break
                elif decision == 0:
                    break
    return object_chosen


def get_record_field_from_user(field_data, new_record, intro_message, fields):
    """
    Args:
        field_data (tuple): one of the tuples from config.NEW_ALBUM_FIELDS
        new_record (dict): a dict in which key is field_name (field_data[1]) and value is an input from a user
        intro_message (str): a message displayed with info about fields already added
        fields (list): a list of fields that a user will be asked about.
            The list may be changed e.g. on the basis of the artist type (person / band)

    Returns:
        new_record, intro_message, fields - changed accordingly to the user's input
    """
    field_description, field_name, field_type, field_third = field_data
    intro_message += '\n' + field_description

    if field_type == list:
        new_value = get_single_choice_from_list(field_third, intro_message)
        if field_name == 'artist_type':  # when adding an artist
            if new_value == 'person':
                # remove artist_name from the 'fields' list
                fields = remove_component_from_list_of_tuples(fields, 'artist\'s name')
            elif new_value == 'band':
                # remove firstname and surname from the 'fields' list
                fields = remove_component_from_list_of_tuples(fields,
                                                              ['artist\'s firstname', 'artist\'s surname'],
                                                              single=False)
                # todo: add band members
        elif field_name == 'artist_name' and \
                new_record.get('artist_type', None) in {'other', ''}:
            # remove firstname and surname from the 'fields' list
            fields = remove_component_from_list_of_tuples(fields,
                                                          ['artist\'s firstname', 'artist\'s surname'],
                                                          single=False)
            # add sort_name to the 'fields' list
            fields.append(('sort name', 'sort_name', str, ''))
        # elif field_name == 'type' and new_value == 'classical':
        #     print('I am not ready for it yet')
        #     # todo: get ready for classical
        #     quit()
    elif field_type == set:
        # allow many choices,
        # the value in new_record will be a set which will be later put into a separate db table
        new_value = set()
        extra_message = ''
        number_of_choices = 0
        while True:
            info_for_user = '\nYou can choose multiple values. Choose empty to finish.'
            new_element = get_single_choice_from_list(field_third, intro_message + extra_message + info_for_user)
            if new_element:
                number_of_choices += 1
                extra_message += ' {}: {}'.format(number_of_choices, new_element) + '\n' + field_description
                new_value.add(new_element)
            else:
                break
    else:
        new_value = get_user_input(default=field_third, intro=intro_message)
        if field_type == int:
            while not (isinstance(new_value, int) or isinstance(new_value, float) or new_value.isdigit()):
                new_value = get_user_input(default=field_third, intro=intro_message)
            new_value = int(new_value)

    intro_message += ': {}'.format(new_value)
    if isinstance(new_value, set):
        new_record[field_name] = ' / '.join(sorted(list(new_value)))
    else:
        new_record[field_name] = new_value

    return new_record, intro_message, fields


def get_artist_for_album(new_record, intro_message, do_clear_screen=True):
    intro_message += '\n' + 'artist\'s name'
    # user inputs their artist
    users_artist = get_user_input(intro=intro_message, do_clear_screen=do_clear_screen)

    if users_artist:
        # is there the artist in db?
        similar_artists_in_database = database.get_similar_artists(artist_dict={'artist_name': users_artist.strip()})
    else:
        similar_artists_in_database = list()
    number_of_artists_in_database = len(similar_artists_in_database)

    artist_chosen = None

    if number_of_artists_in_database > 0:
        artist_chosen = get_single_choice_from_db_list(choices=similar_artists_in_database,
                                                       noun_singular='artist',
                                                       sort_column='similarity')
    if artist_chosen is None:
        while True:
            artist_chosen = add_artist_to_table(from_album=True)
            break
    publ_role = get_single_choice_from_list(['title', 'other'],
                                            'artist\'s this publication role?',
                                            do_clear_screen=False)
    artist_name = artist_chosen['artist_name']
    intro_message += ': {}'.format(artist_name)

    artists_already_added = new_record.get('artist_name', None)
    if artists_already_added:
        new_record['artist_name'].append((artist_chosen['artist_id'], publ_role))
    else:
        new_record['artist_name'] = [(artist_chosen['artist_id'], publ_role)]

    return new_record, intro_message


def get_artists_for_album(new_record, intro_message, do_clear_screen=True):
    while True:
        new_record, intro_message = get_artist_for_album(new_record, intro_message, do_clear_screen)
        stop_adding = get_single_choice_from_list(['YES', 'NO'],
                                                  'Do you want to add another artist to this album?',
                                                  do_clear_screen=False
                                                  ) == 'NO'
        if stop_adding:
            break
    return new_record, intro_message


def get_the_fields_for_album(new_record, intro_message, fields):
    """
    Repeated part of code in album.
    Args:
        new_record: dictionary with fields collected so far
        intro_message: Information for a user about fields collected so far
        fields: fields to be entered / chosen by a user

    Returns:
        changed input + number of parts of the record entered by a user
    """
    parts = 0
    for field in fields:
        if field[1] == 'artist_name':
            new_record, intro_message = get_artists_for_album(new_record, intro_message)
        else:
            new_record, intro_message, fields = get_record_field_from_user(field, new_record, intro_message, fields)
            if field[1] == 'parts':
                parts = new_record['parts']
                if parts > 1:
                    intro_message += '\n\n' + 'part 1 out of {}'.format(parts)
    return new_record, intro_message, fields, parts


def choose_fields_to_edit(fields, part):
    options = [str(field[0]) for field in fields]
    choices = ['>> '] + ['   '] * len(options)
    longest_option = max(len(max(options, key=len)) + 1, 10)
    options.insert(0, '[' + 'confirm'.center(longest_option - 2) + ']')
    marked = {i: False for i in range(len(options))}
    choice = 0
    while True:
        clear_screen()
        print('Which db fields for part {} will be different from part 1?'.format(part))
        print()
        for idx in range(len(choices)):
            print(choices[idx] + ' ' + options[idx].ljust(longest_option, '.' if idx > 0 else ' ') + '*' * marked[idx])
        print()
        print('Use Up and DOWN arrows and confirm with ENTER.')
        ch1, ch2 = take_char()
        if ch1 == 224:
            if ch2 == 72 and choice > 0:  # UP arrow
                choices[choice] = "   "
                choice -= 1
                choices[choice] = ">> "
            elif ch2 == 80 and choice < len(options) - 1:  # DOWN arrow
                choices[choice] = "   "
                choice += 1
                choices[choice] = ">> "
        elif ch1 == 13:  # ENTER
            if choice == 0:
                break
            else:
                marked[choice] = not marked[choice]
    chosen_options = [options[idx] for idx in range(len(choices)) if marked[idx]]
    chosen_fields = [field for field in fields if field[0] in chosen_options]
    return chosen_fields


def get_album_data_from_user(fields):
    """
    Collects data about a new album
    Args:
        fields: a list of tuples like config.NEW_ALBUM_FIELDS

    Returns:
        new_record - a dict where key = field and value = user's input
    """
    new_record = dict()
    intro_message = 'Adding new album'

    new_record, intro_message, fields, parts = get_the_fields_for_album(new_record, intro_message, fields)

    if parts > 1:
        # part 1 already done
        new_record['part_id'] = 1
        new_record = [new_record]
        for part in range(2, parts + 1):
            intro_message += '\n\n' + 'part {} out of {}'.format(part, parts)
            fields = config.NEW_ALBUM_FIELDS
            fields = remove_component_from_list_of_tuples(fields, 'number of parts')
            fields = remove_component_from_list_of_tuples(fields, 'type of music')
            fields_to_edit = choose_fields_to_edit(fields, part)
            fields_to_copy = [field for field in fields if field not in fields_to_edit]

            this_parts_record = dict()
            this_parts_record, intro_message, fields, phantom_parts \
                = get_the_fields_for_album(this_parts_record, intro_message, fields_to_edit)
            fields_to_copy_db_names = [field[1] for field in fields_to_copy]
            for field_name in fields_to_copy_db_names:
                this_parts_record[field_name] = new_record[0][field_name]
            this_parts_record['parts'] = new_record[0]['parts']
            this_parts_record['type'] = new_record[0]['type']
            this_parts_record['part_id'] = part
            new_record.append(this_parts_record)

    return new_record


def get_artist_data_from_user(fields):
    """
        Collects data about a new artist
        Args:
            fields: a list of tuples like config.NEW_ARTIST_FIELDS

        Returns:
            new_record - a dict where key = field and value = user's input
        """

    new_record = dict()
    intro_message = 'Adding new artist'

    for field in fields:
        new_record, intro_message, fields = get_record_field_from_user(field, new_record, intro_message, fields)
    new_record = clear_artist_names(new_record['artist_type'], new_record)
    return new_record


def remove_component_from_list_of_tuples(the_list, components, single=True):
    """
    Args:
        the_list (list): a list of tuples
        components:     it is supposed to be the first coordinate of a certain tuple in the list,
                        it may be also an iterable of such first coordinates
        single (bool):  True if component is just a single first coordinate,
                        False if it is an iterable of such first coordinates
    Returns:
        the_list with elements pointed by component removed
    """
    print()
    if single:
        components = [components]
    items_to_be_removed = set()

    # find elements to be removed
    for component in components:
        for elt in the_list:
            if elt[0] == component:
                try:
                    items_to_be_removed.add(elt)
                except TypeError:
                    print(items_to_be_removed)
                    print(elt)
                    quit()
    # remove the elements
    for item in items_to_be_removed:
        the_list.remove(item)

    return the_list


def clear_artist_names(artist_type, record):
    """
    The following exemplary data:
    +--+-------------+--------------+------------------+----------------+--------------+
    |  | artist_type | artist_name  | artist_firstname | artist_surname | sort_name    |
    +--+-------------+--------------+------------------+----------------+--------------+
    |1.| person      | Mike Patton  | None             | None           | None         |
    |2.| band        | the Kills    | None             | None           | None         |
    |3.| band        | Led Zeppelin | None             | None           | None         |
    |4.| band        | Los Lobos    | None             | None           | None         |
    +--+-------------+--------------+------------------+----------------+--------------+
    will be changed into:
    +--+-------------+--------------+------------------+----------------+--------------+
    |  | artist_type | artist_name  | artist_firstname | artist_surname | sort_name    |
    +--+-------------+--------------+------------------+----------------+--------------+
    |1.| person      | Mike Patton  | Mike             | Patton         | Patton Mike  |
    |2.| band        | the Kills    | None             | None           | Kills the    |
    |3.| band        | Led Zeppelin | None             | None           | Led Zeppelin |
    |4.| band        | Los Lobos    | None             | None           | Lobos Los    |
    +--+-------------+--------------+------------------+----------------+--------------+
    Args:
        artist_type: person or different (band, other)
        record: the whole record
    Returns:
        record with names cleared
    """
    artist_name = record.get('artist_name', None)
    artist_firstname = record.get('artist_firstname', None)
    artist_surname = record.get('artist_surname', None)
    if artist_type == 'person':
        if artist_name is None:
            artist_name = ((artist_firstname or ' ') + ' ' + (artist_surname or ' ')).strip()
        sort_name = (artist_surname + ' ' + artist_firstname).strip()
    else:
        sort_name = artist_name
        prefixes_irrelevant_for_sort = ['the', 'los', 'las']
        for prefix in prefixes_irrelevant_for_sort:
            if artist_name.lower().startswith(prefix + ' '):
                sort_name = artist_name[len(prefix) + 1:] + ' ' + artist_name[:len(prefix)]
                break
    record['artist_name'] = artist_name
    record['artist_firstname'] = artist_firstname
    record['artist_surname'] = artist_surname
    record['sort_name'] = sort_name
    return record


def add_album_to_table():
    new_album = get_album_data_from_user(fields=config.NEW_ALBUM_FIELDS.copy())
    if isinstance(new_album, dict):
        new_album = [new_album]
    added_albums = list()
    first_part_id = None
    for album_part in new_album:
        album_artists_ids = album_part.pop('artist_name')
        album_id = database.add_record_to_table(record=album_part, table='albums')
        if first_part_id is None:
            first_part_id = album_id
        if album_id:
            album_part['album_id'] = album_id
            for new_artist_id, new_publ_role in album_artists_ids:
                album_artist_records = database.get_records(table_name='albums_artists',
                                                            fields=['album_id', 'artist_id'],
                                                            values=[album_id, new_artist_id])
                if album_artist_records is None or len(album_artist_records) == 0:
                    database.add_record_to_table(record={'album_id': album_id,
                                                         'artist_id': new_artist_id,
                                                         'publ_role': new_publ_role},
                                                 table='albums_artists')
            added_albums.append(album_part)
    if added_albums:
        if len(added_albums) > 1:
            for album in added_albums:
                database.update_records_field(table_name='albums',
                                              record_dict=album,
                                              field='first_part_id',
                                              value=first_part_id)
                album['first_part_id'] = first_part_id
        print('The following album was added to the "albums" table.')
        print(utils.pretty_table_from_dicts(added_albums, database.get_db_columns()['albums']))
    else:
        print('The album was not added to the database.')


def add_artist_to_table(from_album=False):
    new_artist = get_artist_data_from_user(fields=config.NEW_ARTIST_FIELDS.copy())
    artist_id = database.add_record_to_table(record=new_artist, table='artists', artist_from_album=from_album)
    if from_album:
        new_artist = database.get_artist_by_id(artist_id)
        return new_artist
    if artist_id:
        new_artist['artist_id'] = artist_id
        print('The following artist was added to the "artists" table.')
        print(utils.pretty_table_from_dicts(new_artist, database.get_db_columns()['artists']))
        return new_artist
    else:
        print('The artist was not added to the database.')
        return None


def get_queries_table():
    query_dicts = database.get_queries_from_database()
    table_header, table = utils.get_html_for_queries_from_table(query_dicts)
    return table_header, table, query_dicts


def get_simple_query(artist_name, album_title, media, publisher):
    # get the data
    fields = dict()
    table = set()
    if media:
        fields['medium'] = media
        if artist_name:
            artist_name = artist_name.strip()
            fields['artist_name'] = artist_name
        if album_title:
            album_title = album_title.strip()
            fields['album_title'] = album_title
        if publisher:
            fields['publisher'] = publisher
        table = database.get_records_from_query(table_name='albums',
                                                fields=fields)

    # table = utils.turn_dicts_into_list_of_tuples_for_html(table, config.ALL_COLUMNS)
    table_header, table_content, html_dom_ids = utils.get_html_from_table(table, config.ALL_COLUMNS)
    # get the query dict and string
    query_dict = {
        'medium': media,
        'title': album_title,
        'artist': artist_name,
        'publisher': publisher,
    }
    query = ', '.join(['{}: {}'.format(k, ', '.join(v) if isinstance(v, list) else v)
                       for k, v in query_dict.items() if v])
    if query == '':
        query = '---'
    many = len(table_content)
    query += ' ({} item{} found)'.format(many, '' if many == 1 else 's')
    return query, query_dict, table_header, table_content, html_dom_ids


def main():
    # add_artist_to_table()
    add_album_to_table()


if __name__ == "__main__":
    main()
