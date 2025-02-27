import os
import sys

sys.path.append('../')
sys.path.append('./')

import pypubpub
from pypubpub.utils import generate_random_number_string, get_time_string

p1 = pypubpub.Pubv6.Pubshelper_v6
from unjournalpubpub_production.conf import (email, password, community_id, community_url)

pubhelper = p1(password=password)

def backupV6(pubhelper:p1, output_dir="./", format='plain', one_file=True,  pubs=[None], ):
    """backup v6 Pubs to files
    :param output_dir: directory to write files to
    :param format: 'plain' or 'html' or 'pdf' or 'docx' or 'markdown' or 'epub' or 'odt' or 'jats' or 'tex' or 'json'
    :param one_file: True or False - Set to True in case of 'plain' (text) to to concatenate all the text of pubs into 1 text output file `combined.txt`

    uses the Pubpub api: https://www.pubpub.org/apiDocs#/paths/api-export/post
    """
    pubhelper.login()
    pubs00 = pubhelper.get_many_pubs(limit=9999)

    if one_file==True:
        pub_filepath = os.path.normpath(os.path.expanduser(f'{output_dir}/pubs-{get_time_string()}-{generate_random_number_string(4)}.txt'))
        with(open(pub_filepath, 'w')) as f:
            for p in pubs00['pubIds']:
                pub_slug= pubs00['pubsById'][p]['slug']
                f.write(f'pubId: {p}\n')
                f.write(f'pub slug: {pub_slug}\n')
                print(f'pubId: {p}\n')
                print(f'pub slug: {pub_slug}\n')
                try:
                    d = pubhelper.downloadpubexport(p)
                    f.write(d)
                except Exception as e:
                    print("ERROR: unable to download export : pub id :", p, "slug::", pub_slug, e)
                    f.write("ERROR: unable to download export")
                    f.write(str(e))
                f.write("\n\n")
    else:
        for p in pubs00['pubIds']:
            pub_slug= pubs00['pubsById'][p]['slug']
            pub_filepath = os.path.normpath(os.path.expanduser(f'{output_dir}/pub-{p}.{format}'))
            with(open(pub_filepath, 'w')) as f:
                print(f'pubId: {p}\n')
                print(f'pub slug: {pubs00['pubsById'][p]['slug']}\n')
                try:
                    d = pubhelper.downloadpubexport(p)
                    f.write(d)
                    print('success writing to file')
                except Exception as e:
                    print("ERROR: unable to download export : pub id :", p, "slug::", pubs00['pubsById'][p]['slug'], e)
                    f.write("ERROR: unable to download export")
                    f.write(str(e))
                


    print("COMPLETE")


import argparse
if __name__ == "__main__":
    print("Hello, World!")
    # backupV6(pubhelper=pubhelper, output_dir=None, format='plain', one_file=True,  pubs=[None], )



