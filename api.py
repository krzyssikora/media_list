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
        return_string = default
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
        if field_name in {'main_artist_type', 'artist_type'}:
            if new_value == 'person':
                # remove artist_name from the 'fields' list
                fields = remove_component_from_list_of_tuples(fields, 'artist\'s name')
            elif new_value == 'band':
                # remove firstname and surname from the 'fields' list
                fields = remove_component_from_list_of_tuples(fields, ['artist\'s firstname', 'artist\'s surname'])
        elif field_name == 'artist_name' and new_record['main_artist_type'] in {'other', ''}:
            # remove firstname and surname from the 'fields' list
            fields = remove_component_from_list_of_tuples(fields, ['artist firstname', 'artist surname'])
            # add sort_name to the 'fields' list
            fields.append(('sort name', 'sort_name', str, ''))
        elif field_name == 'type' and new_value == 'classical':
            print('I am not ready for it yet')
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
            artist_name = (artist_firstname + ' ' + artist_surname).strip()
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
        new_record, intro_message, fields = get_record_field_from_user(field, new_record, intro_message, fields)

    # todo: multiple parts

    new_record = clear_artist_names(new_record['main_artist_type'], new_record)

    return new_record

    # INSERT INTO albums (artist_name, sort_name, album_title, publisher, medium, date_orig, date_publ, type)
    # VALUES ('Mike Patton, Jean-Claude Vennier', 'Patton Mike',
    # 'Corpse Flower', 'Ipecac', 'CD', '2019', '2019', 'various');


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


def add_artist_to_table():
    new_artist = get_artist_data_from_user(fields=config.NEW_ARTIST_FIELDS)
    artist_id = database.add_record_to_table(record=new_artist, table='artists')
    if artist_id:
        new_artist['artist_id'] = artist_id
        print('The following artist was added to the "artists" table.')
        print(pretty_table_from_dicts(new_artist, database.get_db_columns()['artists']))
    else:
        print('The artist was not added to the database.')


def pretty_table_from_dicts(dicts, column_names):
    """
    creates a nice table with values from each dict displayed in a separate row
    Args:
        dicts: a single dict or a list of dicts
        column_names (list): keys from the dicts, may be a subset or a superset
    Returns:
        a string with a nice table
    """
    table = PrettyTable()
    table.field_names = column_names
    if isinstance(dicts, dict):
        dicts = [dicts]
    for row_dict in dicts:
        row = [row_dict.get(column, '') or '' for column in column_names]
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
    table = PrettyTable()
    if column_names:
        table.field_names = column_names
    else:
        table.field_names = [i for i in range(len(tuples[0]))]
    if isinstance(tuples, tuple):
        tuples = [tuples]
    for row in tuples:
        table.add_row(row)
    return table


def main():
    add_artist_to_table()
    


if __name__ == "__main__":
    main()

# todo: display records with filters
