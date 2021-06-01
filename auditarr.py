import sqlite3
import sys
import datetime
import argparse
import logging as log
from datetime import datetime


# Set up the arguments for the app
parser = argparse.ArgumentParser()
parser.add_argument(dest="radarrdb",
                    help="Run with desired config.yml file",
                    type=str)
parser.add_argument(dest="plexdb",
                    help="The radarr database path",
                    type=str)
parser.add_argument("-library", "--library", "--library-id",
                    dest="libraryid",
                    help="Sync mode, can be 'append' or 'sync'. Refer to PAC wiki for more details",
                    type=str,
                    default='1')
parser.add_argument("-v", "--verbose",
                    action = "store_true",
                    dest="verbose",
                    help="More detailed logs.")

args = parser.parse_args()

# Set up a logging format, allowing use of -v for debug mode
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Verbose output.")
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)

# Gets the difference between two lists provided as parameters
def Diff(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))

# Function to get the folders as seen by plex and radarr, compare them and report the difference
def auditPlex(radarrdb, plexdb, libraryid='1'):
    now = datetime.now().strftime("%H:%M:%S")
    log.info(now + " Auditarr: Starting new audit...")
    radarrFolders = getRadarrFolders(args.radarrdb)
    plexFolders = getPlexFolders(args.plexdb, libraryid)
    difference = Diff(radarrFolders, plexFolders)
    # Output difference to user
    if len(difference) is 0:
        log.info("No differences to report")    
    else:
        log.info("Difference:")
        for item in difference:
            if item in radarrFolders:
                log.info(item + " from Radarr database")
                continue;
            elif item in plexFolders:
                log.info(item + " from Plex database")
            else:
                log.info(item)

# Get the folders from the PlexDB
def getPlexFolders(plexdb, libraryid):
    plexFoldersAr = []
    plexDB = sqlite3.connect(plexdb)
    # Seacrh method: First, grab all the media in the library in 'media_items', 
    # then use this id to get the directory id from 'media_parts', 
    # finally use the directory id to get the folder path from 'directories'
    searchMethod = "SELECT path FROM directories WHERE id IN (SELECT directory_id FROM media_parts WHERE media_item_id IN (SELECT id FROM media_items WHERE library_section_id='{}'))".format(libraryid)
    plexFolders = plexDB.execute(searchMethod)
    log.debug(plexFolders)
    # Add the results to a list and then return that list.
    for row in plexFolders:
        log.debug(row[0])
        plexFoldersAr.append(str(row[0]))
    log.debug(plexFoldersAr)
    return plexFoldersAr

def getRadarrFolders(radarrdb):
    radarrFoldersAr = []
    radarrDB = sqlite3.connect(radarrdb)
    rootFolders = []
    # First, get all the root folders in use and add to list as we need to remove these from the strings later.
    for path in radarrDB.execute("SELECT path FROM RootFolders"):
        rootFolders.append(path[0])
    # Then get the folder paths for downloaded movies from the radarrDB
    radarrFolders = radarrDB.execute("SELECT path FROM Movies WHERE MovieFileId!='0'")
    log.debug(radarrFolders)
    # For each folder path remove the root folder and return list of movie folders.
    for row in radarrFolders:
        fullPath = str(row[0])
        # Remove the root folder path from the string to give us the directory name only
        for path in rootFolders:
            log.debug("Need to remove " + str(path))
            # Health check to ensure the root folder is part of the string. Allows for multiple root folders without breaking
            if path in fullPath:
                fullPath = fullPath.replace(path, "")
                log.debug(fullPath)
            radarrFoldersAr.append(fullPath)
    log.debug(radarrFoldersAr)
    # Return the radarr folder paths with root folders stripped.
    return radarrFoldersAr

auditPlex(args.radarrdb, args.plexdb, args.libraryid)


