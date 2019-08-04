from __future__ import print_function
from rdflib.term import URIRef
from PyOpenWorm.data_trans.csv_ds import CSVDataSource
from PyOpenWorm.data_trans.connections import ConnectomeCSVDataSource
from PyOpenWorm.context import Context
from PyOpenWorm.datasource import DataTranslator, DataSource
from PyOpenWorm import connect
from PyOpenWorm.datasource_loader import DataSourceDirLoader
import pickle
import os.path
from os.path import join as p
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def download_torrent(torrent_name, powdir='.pow', tempdir='.'):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(p(powdir, 'temp', 'token.pickle')):
        with open(p(powdir, 'temp', 'token.pickle'), 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                p(powdir, tempdir, 'credentials.json'), SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(p(powdir, tempdir, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name, description)").execute()
    items = results.get('files', [])

    selected_file_name = None
    selected_file_id   = None
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            name = item['name']
            ids = item['id']
            dex = item['description']
            #Added this .torrent to Google Drives - It contains Merged_Nuclei_Stained_Worm(300MB)
            if name == torrent_name:
                selected_file_id = ids
                selected_file_name = name


    request = service.files().get_media(fileId=selected_file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    stri = p(tempdir, selected_file_name)
    with io.open(stri, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

    return p(tempdir, selected_file_name)


class BitTorrentDataSourceDirLoader(DataSourceDirLoader):

    def __init__(self, *args, powdir, tempdir, **kwargs):
        super(BitTorrentDataSourceDirLoader, self).__init__(*args, **kwargs)
        self.tempdir = tempdir
        self.powdir = powdir

    def load(self, *data_source):
        for d in data_source:
            x = list(d.torrent_file_name())
            downloaded_torrent_name = download_torrent(x[0], powdir=self.powdir, tempdir=self.tempdir)
            print('downloaded torrent', downloaded_torrent_name)

        os.system("torrent_cli.py start &")
        os.system("torrent_cli.py add " + downloaded_torrent_name)
