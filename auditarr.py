import sqlite3
import sys
import datetime
import argparse
import logging as log

parser = argparse.ArgumentParser()
parser.add_argument(dest="radarrdb",
                    help="Run with desired config.yml file",
                    type=str)
parser.add_argument(dest="plexdb",
                    help="The radarr database path",
                    type=str)
parser.add_argument("-library", "--library", "--library-id",
                    dest="libraryid",
                    choices=['append', 'sync'],
                    help="Sync mode, can be 'append' or 'sync'. Refer to PAC wiki for more details",
                    type=str)
parser.add_argument("-v", "--verbose",
                    action = "store_true",
                    dest="verbose",
                    help="More detailed logs.")

args = parser.parse_args()

if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Verbose output.")
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)


def Diff(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))


def auditPlex(radarrdb, plexdb, libraryid):
    radarrFolders = getRadarrFolders(args.radarrdb)
    plexFolders = getPlexFolders(args.plexdb)
    difference = Diff(radarrFolders, plexFolders)
    log.info("Difference:")
    for item in difference:
        if item in radarrFolders:
            log.info(item + "from Radarr")
        if item in plexFolders:
            log.info(item + "from Plex")
        else:
            log.info(item)

def getPlexFolders(plexdb):
    plexFoldersAr = []
    plexDB = sqlite3.connect(plexdb)
    plexFolders = plexDB.execute("SELECT path FROM directories WHERE id IN (SELECT directory_id FROM media_parts WHERE media_item_id IN (SELECT id FROM media_items WHERE library_section_id='1'))")
    log.debug(plexFolders)
    for row in plexFolders:
        log.debug(row[0])
        plexFoldersAr.append(str(row[0]))
    log.debug(plexFoldersAr)
    return plexFoldersAr

def getRadarrFolders(radarrdb):
    radarrFoldersAr = []
    radarrDB = sqlite3.connect(radarrdb)
    radarrFolders = radarrDB.execute("SELECT path FROM Movies WHERE MovieFileId!='0'")
    rootFolders = []
    for path in radarrDB.execute("SELECT path FROM RootFolders"):
        rootFolders.append(path[0])
    log.debug(radarrFolders)
    for row in radarrFolders:
        fullPath = str(row[0])
        for path in rootFolders:
            log.debug("Need to remove " + str(path))
            newPath = fullPath.replace(path, "")
            log.debug(newPath)
            radarrFoldersAr.append(newPath)
    log.debug(radarrFoldersAr)
    return radarrFoldersAr



auditPlex(args.radarrdb, args.plexdb, args.libraryid)


