.. _bittorrent:


2 parts of Framework:
=====================

1. **Download** your contents:

   
* 'LocalFileDataSource' created and stored within the local graph store contains an Informational, torrent_file_name, this stores the name of the torrent containing the location of the desired contents on the Bit-Torrent distributed file system.

>>> pow source show ConnectomeCSVDataSource:2000_connections
ConnectomeCSVDataSource
   CSV file name: 'connectome.csv' 
   File name: 'connectome.csv' 
   Torrent file name: 'd9da5ce947c6f1c127dfcdc2ede63320.torrent' 
 
- The ``load`` method implemented in a subclass of ``DataSourceDirLoader`` gets the torrent file referred to in ``torrent_file_name`` that is stored on Google Drives. Then it is added into the BitTorrent client.

- This BitTorrent client is PyPI packaged and included in the PyOpenWorm setup.

 | To install separately:

>>> pip install torrent-client

 | For usage information:

>>> torrent_cli.py -h

- Within the '.pow/temp' directory we have the ``credentials.json`` and ``token.pickle`` - these are for authentication of the google drive.

	
- Both the torrent and its contents are downloaded into a temporary directory, progress can be viewed as:


>>> watch torrent_cli.py status

- When the download is at 100%, users can run the *data integrity* check to ensure that the contents are unaltered.

>>> python3 integrity.py 'd9da5ce947c6f1c127dfcdc2ede63320.torrent' 'Merged_Nuclei_Stained_Worm.zip'
DATA INTEGRITY CLEARED!

- As ``PyOpenWorm`` would like to *restrict access* to contents, a ``client_secret`` would need to be obtained from the maintainer inorder to access the torrents hosted on Google Drives!

2. **Upload** your contents:

- On an AWS EC2 instance is running a Flask server to accept .zip content file uploads. Visit the Public DNS name (IPv4) :

>>> ping ec2-13-233-119-221.ap-south-1.compute.amazonaws.com


- This will create a torrent and seed the contents that you have uploaded, after this we can download as described above.

Testing:
========


- Unit and Integration tests are included in the ``tests/BitTorrentTest.py`` and can be run as:

    For example:

>>> python setup.py test --addopts "-k test_torrent_download"
