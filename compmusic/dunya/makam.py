import os
import requests
import logging
logger = logging.getLogger("dunya")

import conn
import docserver

def get_recordings():
    """ Get a list of makam recordings in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing recording information::

        {"mbid": Musicbrainz recording id,
         "title": Title of the recording
        }

    For additional information about each recording use :func:`get_recording`.

    """
    return conn._get_paged_json("api/makam/recording")

def get_recording(rmbid):
    """ Get specific information about a recording.

    :param rmbid: A recording mbid

    :returns: mbid, title, artists, raaga, taala, work.

         ``artists`` includes performance relationships
         attached to the recording, the release, and the release artists.

    """
    return conn._dunya_query_json("api/makam/recording/%s" % rmbid)

def get_artists():
    """ Get a list of makam artists in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing artist information::

        {"mbid": Musicbrainz artist id,
        "name": Name of the artist}

    For additional information about each artist use :func:`get_artist`

    """
    return conn._get_paged_json("api/makam/artist")

def get_artist(ambid):
    """ Get specific information about an artist.

    :param ambid: An artist mbid
    :returns: mbid, name, releases, instruments, recordings.

         ``releases``, ``instruments`` and ``recordings`` include
         information from recording- and release-level
         relationships, as well as release artists

    """
    return conn._dunya_query_json("api/makam/artist/%s" % ambid)

def get_releases():
    """ Get a list of makam releases in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing release information::

        {"mbid": Musicbrainz release id,
         "title": title of the release
        }

    For additional information about each release use :func:`get_release`

    """
    return conn._get_paged_json("api/makam/release")

def get_release(cmbid):
    """ Get specific information about a release.

    :param cmbid: A release mbid
    :returns: mbid, title, artists, tracks.

         ``artists`` includes performance relationships attached
         to the recordings, the release, and the release artists.

    """
    return conn._dunya_query_json("api/makam/release/%s" % cmbid)

def get_works():
    """ Get a list of makam works in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing work information::

        {"mbid": Musicbrainz work id,
         "name": work name
        }

    For additional information about each work use :func:`get_work`.

    """
    return conn._get_paged_json("api/makam/work")

def get_work(wmbid):
    """ Get specific information about a work.

    :param wmbid: A work mbid
    :returns: mbid, title, composer, raagas, taalas, recordings

    """
    return conn._dunya_query_json("api/makam/work/%s" % wmbid)

def get_instruments():
    """ Get a list of makam instruments in the database.
    This function will automatically page through API results.

    returns: A list of dictionaries containing instrument information::

        {"id": instrument id,
         "name": Name of the instrument
        }

    For additional information about each instrument use :func:`get_instrument`

    """
    return conn._get_paged_json("api/makam/instrument")

def get_instrument(iid):
    """ Get specific information about an instrument.

    :param iid: An instrument id
    :returns: id, name, artists.

         ``artists`` includes artists with recording- and release-
         level performance relationships of this instrument.

    """
    return conn._dunya_query_json("api/makam/instrument/%s" % str(iid))

def download_mp3(recordingid, location):
    """Download the mp3 of a document and save it to the specificed directory.

    :param recordingid: The MBID of the recording
    :param location: Where to save the mp3 to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    recording = get_recording(recordingid)
    release = get_release(recording["release"]["mbid"])
    title = recording["title"]
    artists = " and ".join([a["name"] for a in release["release_artists"]])
    contents = docserver.get_mp3(recordingid)
    name = "%s - %s.mp3" % (artists, title)
    path = os.path.join(location, name)
    open(path, "wb").write(contents)

def download_release(releaseid, location):
    """Download the mp3s of all recordings in a release and save
    them to the specificed directory.

    :param release: The MBID of the release
    :param location: Where to save the mp3s to

    """
    if not os.path.exists(location):
        raise Exception("Location %s doesn't exist; can't save" % location)

    release = get_release(release_id)
    artists = " and ".join([a["name"] for a in release["release_artists"]])
    releasename = release["title"]
    releasedir = os.path.join(location, "%s - %s" % (artists, releasename))
    for r in release["tracks"]:
        rid = r["mbid"]
        title = r["title"]
        contents = docserver.get_mp3(rid)
        name = "%s - %s.mp3" % (artists, title)
        path = os.path.join(releasedir, name)
        open(path, "wb").write(contents)