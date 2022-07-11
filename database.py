import csv
import sqlite3
from difflib import SequenceMatcher


def get_similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_similar_artist(artist_dict):
    pass



def old_records_from_csv(my_file, albums_list):
    with open(my_file, encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        mapping = {"kto":       "artist_name",
                   "co":        "album_title",
                   # "data":    "date_orig",
                   "data":      "date_publ",
                   "ord":       "sort_name",
                   "część":     "part_id",
                   "uwagi":     "notes",
                   "wytwórnia": "publisher",
                   "genre":     "type"
                   }
        if albums_list is None:
            count = 1
        else:
            count = len(albums_list) + 1
        one_of_many = False
        first_of_many_id = None
        for row in reader:
            if count >= 11:
                pass
            new_album = dict()
            albums_list.append(new_album)
            new_album["item_id"] = count
            for key, value in row.items():
                if key == "medium":
                    if value != "":
                        new_album["medium"] = value
                    else:
                        new_album["medium"] = "CD"
                elif key in mapping.keys() and value != "":
                    if key == "część":
                        new_album["part_id"] = int(float(value))
                        if not one_of_many:
                            one_of_many = True
                            first_of_many_id = count
                        new_album["first_part_id"] = first_of_many_id
                    new_key = mapping.get(key, "error")
                    if new_key not in new_album:
                        new_album[new_key] = value
                elif key == "część" and value == "":
                    one_of_many = False
                    first_of_many_id = None
            count += 1
    return albums_list


def old_records_from_csv_classics(my_file, albums_list):
    with open(my_file, encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        mapping = {"kto":           "artist_name",
                   "co":            "album_title",
                   "data nagrania": "date_orig",
                   "data wydania":  "date_publ",
                   "ord":           "sort_name",
                   "część":         "part_id",
                   "uwagi":         "notes",
                   "wytwórnia":     "publisher",
                   "typ":           "type",
                   "genre":         "genre"
                   }
        artist_mapping = {
            "kompozytor":    "artist_name",
            "dyrygent":      "artist_name",
            "orkiestra":     "artist_name",
            "soliści":       "artist_name"
        }
        artists_list = list()

        count = 1303
        one_of_many = False
        first_of_many_id = None
        for row in reader:
            new_album = dict()
            albums_list.append(new_album)
            new_album["item_id"] = count
            for key, value in row.items():
                if key == "medium":
                    if value != "":
                        new_album["medium"] = value
                    else:
                        new_album["medium"] = "CD"
                elif key in mapping.keys() and value != "":
                    if key == "część":
                        new_album["part_id"] = int(float(value))
                        if not one_of_many:
                            one_of_many = True
                            first_of_many_id = count
                        new_album["first_part_id"] = first_of_many_id
                    new_key = mapping.get(key, "error")
                    if new_key not in new_album:
                        new_album[new_key] = value
                elif key == "część" and value == "":
                    one_of_many = False
                    first_of_many_id = None
                elif key == "orkiestra" and value != "":
                    artists_list.append({"artist_type": "band", "artist_name": value})
                elif key in artist_mapping.keys() and value != "":
                    artists_list.append({"artist_type": "person",  "artist_name": value})
            count += 1
    return albums_list, artists_list


def old_database_from_list(my_list, artists=None):
    conn = sqlite3.connect("database/records_list.sqlite")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS albums
    (item_id INTEGER PRIMARY KEY, parts INTEGER, part_id INTEGER, first_part_id INTEGER, 
    artist_type TEXT, artist_name TEXT, artist_surname TEXT, artist_firstname TEXT, artist_role TEXT, 
    sort_name TEXT, album_title TEXT, content TEXT, publisher TEXT, medium TEXT, 
    date_orig TEXT, date_publ TEXT, notes TEXT, type TEXT, genre TEXT)
    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS artists
    (artist_id INTEGER PRIMARY KEY AUTOINCREMENT, artist_type TEXT, 
    artist_name TEXT, artist_surname TEXT, artist_firstname TEXT, artist_role TEXT)
    ''')
    for record in my_list:
        if "item_id" not in record:
            raise ValueError("item_id missing in the record: ", record)
        else:
            # check if item_id is in the database, add record
            rows_with_id = \
                cur.execute("SELECT COUNT(*) FROM albums WHERE item_id = ?", (record.get("item_id"),)).fetchone()[0]
            if rows_with_id == 0:
                # add record
                placeholder = ", ".join(["?"] * len(record))
                stmt = "INSERT INTO albums ({columns}) VALUES ({values});".format(columns=",".join(record.keys()),
                                                                                  values=placeholder)
                cur.execute(stmt, list(record.values()))
            # add artist
            rows_with_artist = \
                cur.execute("SELECT COUNT(*) FROM artists WHERE artist_name = ?",
                            (record.get("artist_name"),)).fetchone()[0]
            if rows_with_artist == 0:
                # add artist
                cur.execute("INSERT INTO artists (artist_name) VALUES (?)", (record.get("artist_name"),))
            else:
                # more complicated - same artist, new role?, or delete artist_role and pass here
                pass
    for record in artists:
        rows_with_artist = \
            cur.execute("SELECT COUNT(*) FROM artists WHERE artist_name = ?",
                        (record.get("artist_name"),)).fetchone()[0]
        if rows_with_artist == 0:
            # add artist
            cur.execute("INSERT INTO artists (artist_name, artist_type) VALUES (?, ?)",
                        (record.get("artist_name"), record.get("artist_type")))
        else:
            # more complicated - same artist, new role?, or delete artist_role and pass here
            pass
    conn.commit()
    cur.close()


def tmp_artist_types():
    conn = sqlite3.connect("database/records_list.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM artists")
    cur.execute("SELECT * FROM artists")
    lines = cur.fetchall()
    for row in lines:
        if row[1] is None:
            artist_types_dict = {1: "person", 2: "band", 3: "other", 0: 'break', "": "leave empty"}
            print(artist_types_dict)
            artist_type = input(row[2] + ": ")
            if artist_type == "":
                continue
            if artist_type == "0":
                break
            artist_id = row[0]
            cur.execute("UPDATE artists SET artist_type = (?) WHERE artist_id = (?)",
                        (artist_types_dict.get(int(artist_type)), artist_id))
    conn.commit()
    cur.close()


if __name__ == '__main__':
    tmp_artist_types()