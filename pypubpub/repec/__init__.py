""" Tools to populate RePEc.org metadata file with Pubs on Pubpub.org"""



from .. import Pubshelper_v6, Migratehelper_v6


class RePEcPopulator:
    """ Class to populate RePEc.org metadata file with Pubs on Pubpub.org
        pubhelper is a Pubv6 instance
        inputdir contains already existing RePEc.org metadata files
        outputdir is where the new RePEc.org metadata files will be written
    """
    def __init__(self, pubhelper:Pubshelper_v6, inputdir, outputdir, blacklist, format_suffix=".rdf", file_options={"one_file":True }): 
        self.pubhelper = pubhelper

        self.inputdir = inputdir
        self.outputdir = outputdir
        self.blacklist = blacklist
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

    def build_metadata_file(self):
        """ Build a RePEc.org metadata file for a Pub"""
        # get list of pubpub id, url, tite, description, authors
        self.pubs_all = self.pubhelper.get_many_pubs()
        # todo: remove blacklisted items
        # go thru list and make metadata object
        self.pubs_metadata=[]
        # write metadata object to file(s)
        with open(f"{self.outputdir}/evalX.rdf", "w") as f:
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
    
    @staticmethod
    def parse_pub_authors( pub, blacklist=[]):
        """ Parse the authors of a Pub"""
        authors = [a["name"] or a["user"]["fullName"]  for a in pub['attributions'] if(a["name"] or a["user"]["fullName"])]
        authors = [a if(a!="Anonymous Anonymous") else "Anonymous" for a in authors if a not in  blacklist]
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
    


from datetime import datetime
def get_time_string() -> str:
    now = datetime.now()
    return now.strftime("%H_%M_%S")

