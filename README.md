# music list

## content of db tables:

The database contains 2 main tables and a few auxiliary ones:

**main tables**
1. albums
2. artists

**auxiliary tables**
3. albums_artists
4. bands_members
###  albums_artists

| table column | item_id | album_id | artist_id | publ_role |
| --- | --- | --- | --- | --- |
| example      | 1  | 215       | 123      | title |
| example      | 2  | 215       | 678      | other |
| description  | primary key <br/> for this table | primary key <br/> from `albums` table | primary key <br/> from `artists` table | either "**title**" (if the artist appears in publication's title page) <br/> or "**other**" (otherwise) |

Each album may have many artists. Each artist has one publication role.

###  bands_members
| table column | item_id | band_id | artist_id | artist_roles | active_from | active_to | 
| --- | --- | --- | --- | --- | --- | --- |
| example | 1 | 123 | 415 | singer / lead guitar | 1980 | 1982 | 
| example | 2 | 123 | 632 | bass guitar | 1980 | 1987 |

Each band may have many artists. Each artist will have all its roles given as a single string (`artist_roles`), the roles will be separated by slashes.

