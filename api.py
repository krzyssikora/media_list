import os
import config
import database
from prettytable import PrettyTable


def clear_screen():
    """Clears the terminal screen."""
    if os.name == 'posix':
        # mac, linux
        _ = os.system('clear')
    else:
        # for windows
        _ = os.system('cls')


def get_user_input(message="Please enter", default='', intro=''):
    """Collects a string from a user.

    Args:
        message (str): A message to be printed when a user is asked for the input.
        default (str): Default value of the input, printed for user's verification.
        intro (str): Introduction message to display
    """
    clear_screen()
    if intro:
        print(intro)
    return_string = input(message + ": {}".format(default) + chr(8)*len(str(default)))
    if not return_string:
        return_string = '' if default == 'YYYY/MM/DD' else default
    return return_string


def get_choice_from_list(choices, intro=''):
    """
    Prompts user to choose a value from a list until a choice is made.
    Args:
        choices (list):  items to choose from.
        intro (str): a message displayed

    Returns:
        the choice made by the user, whatever type of object it was
    """
    while True:
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


def remove_component_from_list_of_tuples(the_list, components, single=True):
    """
    Args:
        the_list (list): a list of tuples
        components:     it is supposed to be the first coordinate of a certain tuple in the list,
                        it may be also an iterable of such first coordinates
        single (bool):  True if component is just a single coordinates,
                        False if it is an iterable of such first coordinates
    Returns:
        the_list with elements pointed by component removed
    """
    if single:
        components = [components]
    items_to_be_removed = set()

    # find elements to be removed
    for component in components:
        for elt in the_list:
            if elt[0] == component:
                items_to_be_removed.add(elt)
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
                sort_name = artist_name[len(prefix) + 1] + ' ' + artist_name[:len(prefix)]
                break
    record['artist_name'] = artist_name
    record['artist_firstname'] = artist_firstname
    record['artist_surname'] = artist_surname
    record['sort_name'] = sort_name
    return record


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
        new_value = get_choice_from_list(field_third, intro_message)
        if field_name == 'artist_type':
            if new_value == 'person':
                # remove artist_name from the 'fields' list
                fields = remove_component_from_list_of_tuples(fields, 'artist\'s name')
            elif new_value == 'band':
                # remove firstname and surname from the 'fields' list
                fields = remove_component_from_list_of_tuples(fields,
                                                              ['artist\'s firstname', 'artist\'s surname'],
                                                              single=False)
        elif field_name == 'artist_name' and \
                (new_record.get('main_artist_type', None) in {'other', ''} or
                 new_record.get('artist_type', None) in {'other', ''}):
            # remove firstname and surname from the 'fields' list
            fields = remove_component_from_list_of_tuples(fields,
                                                          ['artist\'s firstname', 'artist\'s surname'],
                                                          single=False)
            # add sort_name to the 'fields' list
            fields.append(('sort name', 'sort_name', str, ''))
        elif field_name == 'type' and new_value == 'classical':
            print('I am not ready for it yet')
            # todo: get ready for classical
            quit()
    elif field_type == set:
        # allow many choices,
        # the value in new_record will be a set which will be later put into a separate db table
        new_value = set()
        extra_message = ''
        number_of_choices = 0
        while True:
            info_for_user = '\nYou can choose multiple values. Choose empty to finish.'
            new_element = get_choice_from_list(field_third, intro_message + extra_message + info_for_user)
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
    new_record[field_name] = new_value

    return new_record, intro_message, fields


def get_artist_for_album(new_record, intro_message):
    intro_message += '\n' + 'artist\'s name'
    users_artist = get_user_input(intro=intro_message)

    if users_artist:
        similar_artists_in_database = database.find_similar_artist(artist_dict={'artist_name': users_artist.strip()})
    else:
        similar_artists_in_database = list()
    number_of_artists_in_database = len(similar_artists_in_database)

    artist_chosen = None

    if number_of_artists_in_database > 0:
        table_keys = list(similar_artists_in_database[0].keys())
        table_keys.remove('similarity')
        if number_of_artists_in_database == 1:
            print('The following artist was found in the database.')
            print(pretty_table_from_dicts(similar_artists_in_database, table_keys))
            decision = input('Is it the artist (y/n)? ')
            if decision in {'y', 'Y'}:
                artist_chosen = similar_artists_in_database[0]
        else:
            similar_artists_in_database.sort(key=lambda x: x['similarity'], reverse=True)
            for idx, art in enumerate(similar_artists_in_database):
                art['ord'] = idx + 1
            table_keys.insert(0, 'ord')
            print('The following artists were found in the database.')
            print(pretty_table_from_dicts(similar_artists_in_database, table_keys))
            decision = ''
            while True:
                decision = input('Choose the correct artist (1-{}) '
                                 'or 0 if it is not on the list. '.format(number_of_artists_in_database))
                if decision.isdigit():
                    decision = int(decision)
                    if 1 <= decision <= number_of_artists_in_database:
                        artist_chosen = similar_artists_in_database[decision - 1]
                    elif decision == 0:
                        break
    if artist_chosen is None:
        while True:
            artist_chosen = add_artist_to_table()
            if artist_chosen is not None:
                break
    artist_name = artist_chosen['artist_name']
    intro_message += ': {}'.format(artist_name)
    new_record['artist_name'] = artist_name
    new_record['main_artist_id'] = artist_chosen['artist_id']

    return new_record, intro_message


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

    for field in fields:
        # todo: multiple parts
        if field[1] == 'artist_name':
            new_record, intro_message = get_artist_for_album(new_record, intro_message)
        else:
            new_record, intro_message, fields = get_record_field_from_user(field, new_record, intro_message, fields)

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
    print('*' * 50)
    print(new_record)
    _ = input()
    new_record = clear_artist_names(new_record['artist_type'], new_record)
    print('*' * 50)
    print(new_record)
    _ = input()
    return new_record


def add_artist_to_table():
    new_artist = get_artist_data_from_user(fields=config.NEW_ARTIST_FIELDS)
    artist_id = database.add_record_to_table(record=new_artist, table='artists')
    if artist_id:
        new_artist['artist_id'] = artist_id
        print('The following artist was added to the "artists" table.')
        print(pretty_table_from_dicts(new_artist, database.get_db_columns()['artists']))
        return new_artist
    else:
        print('The artist was not added to the database.')
        return None


def pretty_table_from_dicts(dicts, column_names):
    """
    creates a nice table with values from each dict displayed in a separate row
    Args:
        dicts: a single dict or a list of dicts
        column_names (list): keys from the dicts, may be a subset or a superset
    Returns:
        a string with a nice table
    """
    if isinstance(dicts, dict):
        dicts = [dicts]

    table = PrettyTable()
    table.align = 'l'
    if column_names is None:
        column_names = set()
        for row_dict in dicts:
            column_names = column_names.union(set(row_dict.keys()))
    non_empty_columns = [column for column in column_names if any(row.get(column, None) for row in dicts)]
    table.field_names = non_empty_columns
    for row_dict in dicts:
        row = [row_dict.get(column, '') or '' for column in non_empty_columns]
        table.add_row(row)
    return table


def pretty_table_from_tuples(tuples, column_names=None):
    """
    creates a nice table with values from each tuple displayed in a separate row
    Args:
        tuples: a single tuple or a list of tuples
        column_names (list): keys from the dicts, may be a subset or a superset
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
        table.add_row(row)
    return table


def main():
    # add_artist_to_table()
    album = get_album_data_from_user(config.NEW_ALBUM_FIELDS)
    print(album)
    print()
    print(pretty_table_from_dicts(album, database.get_db_columns()['albums']))



if __name__ == "__main__":
    main()

# todo: display records with filters
