from __future__ import print_function
from PyOpenWorm.datasource import DataTranslator
from PyOpenWorm.context import Context
from PyOpenWorm.data_trans.connections import ConnectomeCSVDataSource
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

class DT(DataTranslator):
    def translate(self, source):
        pass


def pow_data(ns):
    ns.context.add_import(ConnectomeCSVDataSource.definition_context)
    ns.context(ConnectomeCSVDataSource)(
    key = 'Mark_Arnab_2000_connections',
    csv_file_name = 'connectome.csv',
    torrent_file_name = 'd9da5ce947c6f1c127dfcdc2ede63320.torrent'
    )


__yarom_mapped_classes__ = (DT,)