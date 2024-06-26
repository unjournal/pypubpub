import sys
sys.path.append('../')
sys.path.append('./')
# sys.path.append('../../')
# from .. import Pubshelper_v6
import pypubpub
# from pypubpub.Pubv6.Pubshelper_v6 
# import Pubshelper_v6
# from Pubv6 import Pubshelper_v6

p1 = pypubpub.Pubv6.Pubshelper_v6
from unjournalpubpub_production.conf import (email, password, community_id, community_url)

pubhelper = p1(password=password)

def backupV6(pubhelper:p1, output_dir=None, format='plain', one_file=True,  pubs=[None], ):
    """backup v6 Pubs to files
    :param output_dir: directory to write files to
    :param format: 'plain' or 'html' or 'pdf' or 'docx' or 'markdown' or 'epub' or 'odt' or 'jats' or 'tex' or 'json'
    :param one_file: True or False - Set to True in case of 'plain' (text) to to concatenate all the text of pubs into 1 text output file `combined.txt`

    uses the Pubpub api: https://www.pubpub.org/apiDocs#/paths/api-export/post
    """
    pubhelper.login()
    pubs00 = pubhelper.get_many_pubs(limit=9999)
    # kl=lambda x: print(len(x), x[0:4]) 
    # kl( pubs00['pubIds'] )

    with(open('pubs00.text', 'w')) as f:
        for p in pubs00['pubIds']:
            d = pubhelper.downloadpubexport(p)
            print(d)
            f.write(f'pubId: {p}\n')
            f.write(f'pub slug: {pubs00['pubsById'][p]['slug']}\n')
            f.write(d)
            f.write("\n\n")
    print("COMPLETE")



    

backupV6(pubhelper=pubhelper, output_dir=None, format='plain', one_file=True,  pubs=[None], )
