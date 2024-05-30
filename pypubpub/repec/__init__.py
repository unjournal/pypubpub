""" Tools to populate RePEc.org metadata file with Pubs on Pubpub.org"""



import re
from pypubpub.utils import get_time_string
from .. import Pubshelper_v6, Migratehelper_v6


class RePEcPopulator:
    """ Class to populate RePEc.org metadata file with Pubs on Pubpub.org
        pubhelper is a Pubv6 instance
        inputdir contains already existing RePEc.org metadata files
        outputdir is where the new RePEc.org metadata files will be written
    """
    def __init__(
            self, 
            pubhelper:Pubshelper_v6, 
            inputdir, 
            outputdir, 
            blacklist, 
            format_suffix=".rdf", 
            file_options={"one_file":True }, 
            blacklist_templates=[],
            blacklist_match_fns=[],
            ): 
        """ Initialize a RePEcPopulator instance"""
        self.pubhelper = pubhelper

        self.inputdir = inputdir
        self.outputdir = outputdir
        self.blacklist_templates = blacklist_templates or RePEcPopulator.blacklist_templates_internal
        self.blacklist = blacklist + blacklist_templates
        self.blacklist_match_fns = blacklist_match_fns
        self.format_suffix = format_suffix
        self.file_options = file_options
        self.numbering_counter= {
            '2023':55,
            '2024':10,
            'blacklist':{
                '2023':[0,22],
                '2024':[0],
            }
        }

    blacklist_templates_internal = [{
        "slug":"templatesummary"
        },{
        "slug":"evalsummary"
        },{
            "titleKeyword":"[template]"
        },{
            "titleKeyword": r"(?i)\[template"
        }]

    def build_metadata_file(self):
        """ Build a RePEc.org metadata file for a Pub"""
        # get list of pubpub id, url, tite, description, authors
        self.pubs_all = self.pubhelper.get_many_pubs(limit=500, ordering={'field': 'creationDate', 'direction': 'ASC'}
                                                     
        )
        # todo: remove blacklisted items
        self.pubs_all = self.remove_blacklisted_pubs(self.pubs_all)
        # go thru list and make metadata object
        self.pubs_metadata=[]
        # write metadata object to file(s)
        with open(f"{self.outputdir}/evalX_{get_time_string()}.rdf", "w") as f:
            for pub in self.pubs_all['pubsById'].values():
                authors = self.parse_pub_authors(pub)
                m = self.buildMetadata(
                            id=pub['id'], 
                            url=f"""{self.pubhelper.community_url}/pub/{pub['slug']}""",
                            pdf_url=None,
                            pub=None,
                            title=pub['title'],
                            description=pub['description'],
                            authors=authors,
                            doi=pub['doi'],
                            creation_date=pub['createdAt'][:10],
                            jel_codes=None,
                            handle=self.build_handle(pub),
                            number=self.number_counter(pub['createdAt'][:4]),
                            abstract=pub['description'],
                            # publication_status=pub1['publicationStatus'],

                )
                self.pubs_metadata.append(m)
                f.write(m)
                f.write("\n\n")
        return self.pubs_metadata

    redif_paper_template = """Template-Type: ReDIF-Paper 1.0
Author-Name: Gavin Taylor
Title: Evaluation Summary and Metrics: "Long Term Cost-Effectiveness of Resilient Foods 
for Global Catastrophes Compared to Artificial General Intelligence Safety"
Abstract: Provides an overview and summary of the metrics for the evaluation of "Long Te
rm Cost-Effectiveness of Resilient Foods for Global Catastrophes Compared to Artificial 
General Intelligence Safety" for The Unjournal (Unjournal.org). 
DOI: https://doi.org/10.21428/d28e8e57.4c60aac3 
Publication-Status: Published in The Unjournal
File-URL: https://unjournal.pubpub.org/pub/y2a1lbzv/
File-Format: text/html
File-URL: https://s3.amazonaws.com/assets.pubpub.org/kpld5g714q0gws6h9oq0sb92v7ozhf2s.pd
f 
File-Format: Application/pdf
Creation-Date: 2023-05-12
Classification-JEL: Q18,O33,Q54,O38,H12
Handle: RePEc:bjn:evalua:foods2023
Number: 2023-50 
"""
    redif_paper_template_header=f"""Template-Type: ReDIF-Paper 1.0\n"""
    publication_status="Published in The Unjournal"

    def buildMetadata(self, id, url, pdf_url, pub, title, description, authors, doi, creation_date, jel_codes, handle, number, abstract, publication_status=publication_status, header=redif_paper_template_header ):
        """ Build a RePEc.org metadata object for a Pub"""
        m=f"{header}"
        author_section = self.build_author_section(authors) if authors else None
        if(author_section):
            m = m + author_section
        m = m + f"""Title: {title}
Abstract: {abstract}
DOI: {doi}
Publication-Status: {publication_status}
File-URL: {url}
File-Format: text/html
"""     
        if pdf_url:
            m = m + f"""File-URL: {pdf_url}\n"""
        m = m + f"""Creation-Date: {creation_date}\n"""
        if jel_codes:
            m = m + f"""Classification-JEL: {jel_codes}\n"""
        m = m + f"""Handle: {handle}\n"""
        m = m + f"""Number: {number}\n"""
        return m
    

    def remove_blacklisted_pubs(self, pubs):
        """ Remove blacklisted pubs from a list of pubs"""
        strings_blacklist = [b for b in self.blacklist if  type(b)==str]
        slug_blacklist = [b['slug'] for b in self.blacklist if 'slug' in b]
        title_blacklist = [b['title'] for b in self.blacklist if 'title' in b]
        title_keyword_blacklist = [b['titleKeyword'] for b in self.blacklist if 'titleKeyword' in b]
        id_blacklist = [b['id'] for b in self.blacklist if 'id' in b]
        doi_blacklist = [b['doi'] for b in self.blacklist if 'doi' in b]
        pubs2 = [p for p in pubs 
             if not ( 
                 (p['doi']  in doi_blacklist)
                 or (p['slug']  in slug_blacklist)
                 or (p['title']  in title_blacklist)
                 or (p['id']  in id_blacklist)
                 
                 or ( any([ re.match(k,p['title'] ) for k in title_keyword_blacklist]))
                 or ( any([k in [p[i] for i in ['id', 'slug', 'title', 'doi' ] ] for k in strings_blacklist]))
                 )]
        pubs2 = [p for p in pubs if not any([fn(p) for fn in self.blacklist_match_fns]) ] if self.blacklist_match_fns else pubs2
        return pubs2

    @staticmethod
    def parse_pub_authors( pub, blacklist=[], blacklist_0=["Unjournal Admin (NA)", "Unjournal Admin"]):
        """ Parse the authors of a Pub blacklist and blacklist_0=["Unjournal Admin (NA)", "Unjournal Admin"] get merged, set blacklist_0=[] to not merge"""
        blacklist = blacklist + blacklist_0
        authors = [a["name"] or a["user"]["fullName"]  for a in pub['attributions'] if((a["name"] or a["user"]["fullName"]) and (a["isAuthor"]))]
        authors = [a for a in authors if a not in  blacklist]
        authors = [a if(a!="Anonymous Anonymous") else "Anonymous" for a in authors]
        authors=[a for a in authors if (not a.startswith("Unjournal Admin") and not "(NA)" in a)]
        return authors
    
    @staticmethod
    def build_author_section(authors:list|str):
        """ Build the author section of a RePEc.org metadata object for a Pub"""
        authors = [authors] if isinstance(authors, str) else authors    
        a__ = [f"Author-Name: {a}\n" for a in authors]
        return "".join(a__)
    
    def write_metadata(self, id, metadata, outputdir, filename,  outputformat="file", format_suffix=".rdf", file_options={"one_file":True }):
        if(outputformat=="string"):
            pass

    @staticmethod
    def build_handle(pub,  ) -> str:
        handle = f"RePEc:bjn:evalua:{pub['slug']}"
        return handle

    def number_counter(self, year, mark_used=True):
        """ Build the number scheme for a RePEc.org metadata object for a Pub. Single digit is zero padded"""
        if year in self.numbering_counter:
            n = self.numbering_counter[year] 
        else: 
            n = self.numbering_counter[year] = 1
        if mark_used:
            self.numbering_counter[year] = self.numbering_counter[year] + 1
        return f"{str(year)}-{str(n).zfill(2)}"
    



