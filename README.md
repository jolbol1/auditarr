# Auditarr
---
A simple script that compares a plex library to a radarr library and reports where the differences are. 

## Usage
---
`pyhton3 auditarr.py [-h] [-library LIBRARYID] [-v] radarrdb plexdb`

Where:
* `radarrdb` is the path to the radarr database (usually found in the /radarr)

* `plexdb` is the path to the plex databse, (usually `/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db` )

* `LIBRARYID` is the library id in plex. 
  - If none is given the script will use 1. 
  - You can usually find the id of your library in the url on the plex web app. For example, when on the 'Movies' library, my url shows `source=1`


### Example Usage with Library ID and Paths
`pyhton3 auditarr.py -library 1 /opt/radarr/radarr.db '/opt/plex/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'`


## Why?
---
From time to time a file got corrupted on my server and radarr wouldnt care but plex would. This meant that the Movie Files figure reported by radarr was different to the amount of movies on plex. I created this to easily locate the file that was causing the issue.

Further, I have also found it useful to run periodically as sometimes my plex scanner has not picked up a new media item.


