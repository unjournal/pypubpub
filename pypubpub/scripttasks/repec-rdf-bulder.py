#!python
import os
import sys
import argparse

sys.path.append('../')
sys.path.append('./')


# import pypubpub
from pypubpub import Pubshelper_v6, Migratehelper_v6
import pypubpub.repec as repec

print("using Python: ", sys.version)


def repecBuild(community_url=None, community_id=None, password=None, email=None, output_dir="./"):
    """Build up .rdf metadata file for RePeC
                                     the default is to only build the file for published Pubs
                                     in which case login authentication is not needed. 
    """
    pub_helper = Pubshelper_v6()
    if community_url is not None:
        pub_helper.community_url = community_url
    if community_id is not None:
        pub_helper.community_id = community_id  
    if password is not None:
        pub_helper.password = password
    if email is not None:
        pub_helper.email = email
    repec_helper = repec.RePEcPopulator(pubhelper=pub_helper, inputdir=None, outputdir=os.path.realpath(output_dir))
    metadata=repec_helper.build_metadata_file()

    print("metadata len: \n")
    print(len(metadata))
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Build up .rdf metadata file for RePeC
                                     the default is to only build the file for published Pubs
                                     in which case login authentication is not needed. 
                                     """)

    # parser.add_argument("--multiple", action="store_true", default=False,
    #                 help="for the plain text format download to multiple files; 1 plain text file per pub. Not recommended for the other file formats")
    # parser.add_argument("--format", default='plain' , help="format to download. Default is `plain` (text). Other options are `html` or `pdf` or `docx` or `markdown` or `epub` or `odt` or `jats` or `tex` or `json`")
    parser.add_argument("--directory", type=str, action="store", default='./', 
                        help="directory to write files to. Default is the current directory")
    args = parser.parse_args()
    # exportV6(pubhelper=pubhelper, format=args.format , one_file=(not args.multiple), output_dir=args.directory)
    repecBuild(output_dir=args.directory)
