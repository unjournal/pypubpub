# from sys import ps1
"""Pubpub API helper for v6 """

from collections import namedtuple
from dataclasses import dataclass
from operator import __not__
import re
from time import sleep
from typing import TypedDict
import requests
import json
from Crypto.Hash import keccak
import bibtexparser


from pypubpub.utils import generate_random_number_string, generate_slug, retry #need hashed passwords for API

class Pubshelper_v6:
    def __init__(self, community_url="https://unjournal.pubpub.org", community_id="d28e8e57-7f59-486b-9395-b548158a27d6", email='contact@unjournal.org',password = 'pasw0rt' ):
        self.community_url = community_url
        self.community_id = community_id
        self.cookieJar = None
        self.logged_in = False
        self.email = email
        self.password = password


    def login(self):
        k = keccak.new(digest_bits=512)
        k.update(self.password.encode())
        response = requests.post(
            url=f'{self.community_url}/api/login',
            headers={ "accept": "application/json",
                      "cache-control": "no-cache",
                      "content-type": "application/json",
                      "pragma": "no-cache"
                     },
            data=json.dumps({
                'email': self.email,
                'password': k.hexdigest(),

            }),
        )

        self.cookieJar=response.cookies


        if not self.cookieJar:
            raise Exception(f'Login failed, with status {response.status_code}: {response.text}')

        self.logged_in = True

    def authed_request(self, path, method='GET', body=None, options=None, additionalHeaders=None):

            response = requests.request(
                method,
                f'{self.community_url}/api/{path}',
                data=json.dumps(body) if body else None,
                cookies=self.cookieJar,
                headers={ "accept": "application/json",
                      "cache-control": "no-cache",
                      "content-type": "application/json",
                      "pragma": "no-cache",
                      "origin": self.community_url,
                      **(additionalHeaders if additionalHeaders else {})
                     },
                **options if options else {},
            )

            if response.status_code < 200 or response.status_code >= 300:
                response.raise_for_status()

            return response.json()

    def logout(self):
        response =  self.authed_request('logout', 'GET')
        self.cookieJar = None
        self.logged_in = False

    def getPubByIdorSlug(self, slugOrId, attributes=None, include=None ):

        response = self.authed_request(
            f'pubs/{slugOrId}',
            # todo add url query params for `attribute` and `include` - see https://www.pubpub.org/apiDocs#/paths/api-pubs-slugOrId/get
            'GET'
            )

        return response


    def connect_pub(self, srcPubId, targetPubId,
                    relationType="supplement",
                     pubIsParent=False,
                     approvedByTarget=True,
                     rank=None
                     ):

        response = self.authed_request(
            'pubEdges',
            'POST',
            {
                "pubId": srcPubId,
                "relationType": relationType,
                "pubIsParent": pubIsParent,
                "approvedByTarget": approvedByTarget,
                "targetPubId": targetPubId,
                **( {'rank': rank} if rank else {}),
                #"externalPublication": null
            },
        )
        return response

    ###
    # Note: To connect to an external article, you can first try the connect_pub method. Many external resources have a
    # Pubpub Id. So you can use the connect_pub method after looking up its Pubpub Id.
    #
    #  This method can be used when an external resource does not yet have a Pubpub Id. After using this method to connect
    # to an external resource, the external resource seems to get a Pubpub Id assigned to it, which could be used in the future.
    ###
    def connect_pub_to_external(self, srcPubId,
                                title,
                                url,
                                publicationDate,
                                description,
                                doi=None,
                                avatar=None,
                                contributors=[],
                                relationType="review",
                     rank=None,
                     pubIsParent=False,
                     approvedByTarget=True
                     ):

        response = self.authed_request(
            'pubEdges',
            'POST',
            {
                "pubId": srcPubId,
                "relationType": relationType,
                "pubIsParent": pubIsParent,
                "approvedByTarget": approvedByTarget,
                # "targetPubId": targetPubId,
                **( {'rank': rank} if rank else {}),
                "externalPublication": {
                    "avatar": avatar,
                    "contributors": contributors,
                    "doi": doi,
                    "url": url,
                    "publicationDate": publicationDate, #"2024-04-01T00:00:00.000Z",
                    "title": title,
                    "description": description
                    },
            }
        )
        return response

    def setAttribution(self, pubId, attribution):
        return self.authed_request(
            path = 'pubAttributions',
            method = "POST",
            body = {
                "communityId" : self.community_id,
                "pubId": pubId,
                "roles": ["Writing – Review & Editing","Evaluation Manager",],
            }

        )
    ###
    # To disconnnect 2 pubs, this might be done before deleting them as part of cleanup
    #
    # question: do we need other helper methods to remove connections? such as deleteAllEdgesforPubId?
    ###
    def disconnect_pub(self, edgeId=None, srcPubId=None, targetPubId=None ):
        if edgeId:
          pass
        elif srcPubId and targetPubId:
          # edgeId = self.getTheEdgeIdbyPubIds(srcPubId, targetPubId)
          pass
        else:
          raise Exception('Bad arguments. Either pass in the edgeId to delete, or pass in src and target Pub Ids')

        response = self.authed_request(
            'pubEdges',
            'DELETE',
             {
                 "pubEdgeId": edgeId
              },
        )
        return response


    def get_many_pubs(self, limit = 50, offset = 0, ordering= {'field': 'updatedDate', 'direction': 'DESC'}, collection_ids=None, pub_ids=None):

        response = self.authed_request(
            'pubs/many',
            'POST',
            {
                'alreadyFetchedPubIds': [],
                'pubOptions': {
                    'getCollections': True,
                },
                'query': {
                    'communityId': self.community_id,
                    **( {'collectionIds': collection_ids} if collection_ids else {}),
                    **(   {'withinPubIds': pub_ids} if pub_ids else {}),
                    'limit': limit,
                    'offset': offset,
                    'ordering': ordering,
                },
            },
        )

        return response

    def get_byreleased_pubs(self,
                            limit = 50,
                            offset = 0,
                            ordering= {'field': 'updatedDate', 'direction': 'DESC'} ,
                            isReleased=False,
                            collection_ids=None ,
                            pub_ids=None,
                            alreadyFetchedPubIds=[],
                            relatedUserIds =[]
                            ):

        response = self.authed_request(
            'pubs/many',
            'POST',
            {
                'alreadyFetchedPubIds': alreadyFetchedPubIds,
                'pubOptions': {
                    'getCollections': True,
                },
                'query': {
                    'communityId': self.community_id,
                    isReleased: isReleased,
                    **( {'collectionIds': collection_ids} if collection_ids else {}),
                    **(   {'withinPubIds': pub_ids} if pub_ids else {}),
                    'limit': limit,
                    'offset': offset,
                    'ordering': ordering,
                    **(   {'relatedUserIds': relatedUserIds} if relatedUserIds else {}),
                },
            },
        )

        return response

    def create_pub(self, slug,title , description):
        response =  self.authed_request(
            path='pubs',
            method='POST',
            body={
                # 'pubId': pub_id,
                "slug":slug,
                "title": title,
                "description" : description,
                'communityId': self.community_id,
            },
        )
        return response


    def create_pub_02(self, slug,title , description):
        response =  self.authed_request(
            path='pubs',
            method='POST',
            body={
                # 'pubId': pub_id,
                # "slug":slug,
                # "title": title,
                # "description" : description,
                'communityId': self.community_id,
            },
        )
        return response

    def delete_pub(self, pub_id):
        response =  self.authed_request(
            path='pubs',
            method='DELETE',
            body={
                'pubId': pub_id,
                'communityId': self.community_id,
            },
        )
        return response

    def getPub(self, pub_id):
        return self.get_many_pubs(pub_ids=[pub_id])

    def print_authors_table(self, limit=100, page=1)->list:
        """assumes all members could be authors"""
        authors= self.get_members(limit=limit)
        return authors

    def get_members(self, limit=500):
        """get members of community"""
        response = self.authed_request(
            'members',
            'GET'
            )
        return response

    def sync_authors(self, limit=None, return_list=True):
        """WIP NOT YET:sync the local sqlite table with members of community
            optional default is to also return list of refreshed members
        """
        members =self.get_members()
        if return_list:
            return members
        return
    



class Migratehelper_v6:
    """This class is high level to make and manipulate v6 Pubs"""
    def __init__(self, pubhelperv6) -> None:
        self.pubhelperv6=pubhelperv6
        pass
    def init_check(self):
        if(not self.pubhelperv6.logged_in):
            self.pubhelperv6.login()

    @classmethod
    def factory(
        cls, 
        community_url="https://unjournal.pubpub.org", 
        community_id="d28e8e57-7f59-486b-9395-b548158a27d6", 
        email='contact@unjournal.org',
        password = 'pasw0rt' ):
        if(not pub_helper):
            pub_helper = Pubshelper_v6(community_url=community_url, community_id=community_id, email=email, password=password)
            pub_helper.login()
        return cls(pub_helper)


    @staticmethod
    def isMaybePubId(t:str):
        t2 = re.sub(r"\s+|-","", t )
        if(not len(t2)==32):
            return False
        t3 = re.sub(r"[a-f0-9]", "", t2.casefold())
        if(len(t3)==0):
            return True
        else:
            return False

    def resolve_external_original(
            self, o_id:str, 
            parent_url:str, 
            blank_pub="blank_pub"
            ):
        """
            check if external paper has an existing Pubpub id
            if not create one by making a link from a Pubpub pub to the external resource
        """
        if self.isMaybePubId(o_id):
            pubgotten = self.pubhelperv6.getPubByIdorSlug(o_id)
            if pubgotten:
                return o_id
        return
        # blank_pub_dict = retry()(self.pubhelperv6.getPubByIdorSlug)(blank_pub)
        # if(not blank_pub_dict):
        #     blank_pub_dict = self.pubhelperv6.create_pub(slug=blank_pub, title="blank pub", description="blank pub")
        #     sleep(2)
        # self.pubhelperv6.connect_pub_to_external(blank_pub_dict['id'], title="external original", url=parent_url, publicationDate="2024-04-01T00:00:00.000Z", description="external original")
        # blank_pub_dict


    class createPubsReturn(TypedDict):
        createdPubIds: list
        createdPubs: list
        createPubErrors: list

    def createPubs( 
            self,
            evals=[
                {"slug":"eval01","title":"titel", "description":"description"},
                {"slug":"eval02","title":"title2", "description":"description2"}
            ])->createPubsReturn:
        # first create pubs
        createdPubIds = []
        createdPubs = []
        createPubErrors = []
        for e in evals:
            # pubArgs = self.buildArgs(**e, isValidPubId =isValidPubId, origPaperPubID=origPaperPubID)
            pubNew = self.pubhelperv6.create_pub(**e)
            if pubNew:
                createdPubIds.append(pubNew["id"])
                createdPubs.append(pubNew)
            else:
                createPubErrors.append({"data": e.copy(), "error":"Unable to create pub"})
        return {"createdPubIds":createdPubIds, "createdPubs":createdPubs, "createPubErrors":createPubErrors}



    def validateOrigPaperPubId(self):
        pass

    def prep_create_related_pubs(
        self,
        original_paper_pub_id=None,
        # g ={},
        original_paper_object={
            "doi":None,
            "url": None,
            "publicationDate": None,
            "title": None,
            "description": None,
            "contributors": [], #probably will not be 
        },
        original_paper="pubid or external url or doi",
        evals=[
            {"slug":"eval01","tite":"titel", "description":"description" , "author":"anonymous"},
            {"slug":"eval02","tite":"title2", "description":"description2" , "author": "pubIDXX"}
        ]
    ):
        #link
        # original_paper_res = resolve_original(original_paper)
        isValidPubId = False
        if self.isMaybePubId(original_paper):
            (isValidPubId, origPaperPubID ) = self.validateOrigPaperPubId(original_paper)
        return
    
    def link_related_pubs(self,
                  pubs_list=[],
                  original_paper_pub_id=None,
                  # g ={},
                  original_paper_object={
                        "doi":None,
                        "url": None,
                        "publicationDate": None,
                        "title": None,
                        "description": None,
                        "contributors": [],
                        },
                evals=[
            {"id":"x--x","slug":"eval01","tite":"titel", "description":"description" , "author":"anonymous"},
            {"id":"x--x","slug":"eval02","tite":"title2", "description":"description2" , "author": "pubIDXX"}
        ]




                  ):
        """ connect them, all the pubs are related to each other"""
        for i,p in enumerate(pubs_list):
            if(original_paper_pub_id):
                connector=self.pubhelperv6.connect_pub(

                )
            else:
                connector= self.pubhelperv6.connect_pub_to_external

            connector(
                srcPubId=pubs_list[0], 
                targetPubId=pubs_list[1], 
                relationType="supplement", 
                pubIsParent=False, 
                approvedByTarget=True
                )
                



@dataclass
class OrigPaperMetadata():
    doi:str=None
    url:str=None
    title:str=None
    description:str=None
    bibtex_tuple = namedtuple('BibTeX', 'author title year month')

    def __init__(self, doi:str, url:str=None,  title:str=None, description:str=None):
        self.doi=doi
        self.bibtex_metadata = None
        self.crossref_data = None
        
    def lookup(self):
        if(self.doi):
            self.bibtex_metadata = self.doi2bib(self.doi)

        if( self.bibtex_metadata):
            self.title = self.bibtex_metadata.title
            self.author = self.bibtex_metadata.author
            self.year = self.bibtex_metadata.year
            self.month = self.bibtex_metadata.month
            return self
        else:
            self.crossref_data = self.check_crossref(self.doi)
            if(self.crossref_data):
                self.title = self.crossref_data.title if 'title' in self.crossref_data else None
                self.author = self.crossref_data.author if 'author' in self.crossref_data else None
                
            return self.crossref_data
        # if(self.url):
        #     pass


    @staticmethod
    def doi2bib_options(doi):
        return {
            'url': f'https://doi.org/{doi}',
            'headers': {
                'Accept': 'application/x-bibtex; charset=utf-8'
            }
        }
    
    def doi2bib(self):
        try:
            response = requests.get(**self.doi2bib_options(self.doi))
            if response.status_code == 404:
                return None
            if response.status_code >= 200 or response.status_code <300:
                self.bibtex_metadata =  self.parse_bibtex_string( response.text )
                # self.title = self.bibtex_metadata[1]
                return self.bibtex_metadata

            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            return None



    def XX_check_doi(self):
        response = requests.request(
            "GET",
            f'https://api.crossref.org/works/{self.doi}',
            headers={'accept': 'application/x-bibtex; charset=utf-8'}
        )
        if response.status_code == 404:
            return None
        if response.status_code >= 200 or response.status_code <300:
            self.bibtex_metadata =  self.parse_bibtex_string( response.text )
            self.title = self.bibtex_metadata[1]
            return self.bibtex_metadata
        return


    @staticmethod
    def parse_bibtex_string(bibtex_str):
        # Parse the BibTeX string
        bib_database = bibtexparser.loads(bibtex_str)
        # bibtex_tuple = namedtuple('BibTeX', 'author title year month')
        # Extract the author and title from the first entry
        # Assuming there's at least one entry in the BibTeX string
        if bib_database.entries:
            entry = bib_database.entries[0]
            author = entry.get('author', 'No author found')
            title = entry.get('title', 'No title found')
            year = entry.get('year=', 'No year found')
            month = entry.get('month', 'No month found')
            return OrigPaperMetadata.bibtex_tuple(author, title, year, month)
        else:
            return

    def check_crossref(self):
        if(not self.doi):
            return
        response = requests.request(
            "GET",
            f'https://api.crossref.org/works/{self.doi}',
            headers={ "accept": "application/json",
                    "cache-control": "no-cache",
                    "content-type": "application/json",
                    "pragma": "no-cache",
                    },
        )
        if response.status_code == 404:
            return
        if response.status_code < 200 or response.status_code >= 300:
            response.raise_for_status()
        self.crossref_data = response.json()
        return self.crossref_data


@dataclass
class record_pub_conf():
    email:str
    password:str
    community_id:str
    community_url:str

from tests.conf_settings import email, password, community_id, community_url

class EvaluationPackage():
    def __init__(
            self, 
            doi:str|dict, 
            evaluation_manager_author:str|dict|int, 
            evals:list,
            config:record_pub_conf=None,
            url:str=None,
            title:str=None,
            doi_primary_truth=True,
            autorun=True,
            verbose=True
            ):
        self.doi = doi
        self.evaluation_manager_author = evaluation_manager_author
        self.evals = evals
        self.config = config
        self.url=url
        self.title=title
        self.doi_primary_truth = doi_primary_truth

        self.pubshelper = None
        self.migratehelper = None

        self.parentMetadata = None
        self.remainingPubs=[] # if managing activities use these 2 lists to manage completed and wip 
        self.activePubs=[]
        self.completedPubs=[]
        self.init_conf_setting()
        if(verbose):
            self.print_conf()
        if(autorun):
            self.process_run()

    def init_conf_setting(self):
        if(not self.config):
            # from collections import namedtuple
            
            self.config = record_pub_conf(email, password, community_id, community_url)
            self.config.email = email
            self.config.password = password
            self.community_id = community_id
            self.community_url = community_url
    def init_login(self):
        self.pubshelper = Pubshelper_v6(community_url=self.community_url, community_id=self.community_id, email=self.config.email, password=self.config.password)
        self.migratehelper = Migratehelper_v6(self.pubshelper)

    def print_conf(self):
        g=[f"{k}:{v}" for k,v in self.config.__dict__.items() if k in ['email',  'community_id', 'community_url']]
        print(self.config)

    def connect_papers(self):
        pass
    
    def lookup_parent_paper(self):
        #lookup original
        # doi, url = self.lookup_parent_paper
        self.parentMetadata  = OrigPaperMetadata(doi=self.doi, url=self.url)
        metadata = self.parentMetadata.lookup()
        # look up original in pubpub, if not there, just link the first pub
        # create pubs
        #link pubs
        return self.parentMetadata

    def activePubsMaintainList(self):
        pass

    def process_run(
            self, 
            # doi, 
            # url,
            # evaluation_manager_author_id, 
            # evals
            ):
        """Runs the process of initial original paper lookup, followed by pub creation, and then linking the pubs together."""
        doi = self.doi
        evaluation_manager_author_id = self.evaluation_manager_author_id
        evals = self.evals
        # self.pubshelper = Pubshelper_v6(community_url="https://unjournal.pubpub.org", community_id="d28e8e57-7f59-486b-9395-b548158a27d6", email='contact@unjournal.org', password='pasw0rt')
        # self.pubshelper.login()
        self.parentMetadata = self.lookup_parent_paper()
        #create evaluation manager Pub
        create_eval_mgr_pub = self.create_eval_mgr_pub()
        self.pubshelper.connect_pub_to_external
        # retry()(self.pubshelper.connect_pub)(srcPubId=self.original_pub_id, targetPubId=eval_pub_id, relationType="review", pubIsParent=True, approvedByTarget=True)

        self.original_pub_id = self.pubshelper.connect_pub_to_external(srcPubId=self.evaluation_manager_author_id, title="Original Article", url=f"https://doi.org/{self.doi}", publicationDate=None, description="Original Article", doi=self.doi)
        self.evaluation_pub_ids = []
        pub00 = self.pubshelper.create_pub(slugTestId,slugTestId,slugTestId )

        for i, eval in enumerate(self.evals):
            author_name = eval.get('author', {}).get('name', f"anonymous{i}")
            eval_title = f"Evaluation of {author_name}"
            eval_pub_id = self.pubshelper.create_pub(slug=f"eval-{i}", title=eval_title, description=f"Evaluation by {author_name}")
            self.evaluation_pub_ids.append(eval_pub_id)
            self.pubshelper.connect_pub(srcPubId=self.original_pub_id, targetPubId=eval_pub_id, relationType="review", pubIsParent=True, approvedByTarget=True)
            for linked_pub_id in self.evaluation_pub_ids[:-1]: # Link to all previous evaluations
                self.pubshelper.connect_pub(srcPubId=eval_pub_id, targetPubId=linked_pub_id, relationType="supplement", pubIsParent=False, approvedByTarget=True)
        self.pubshelper.logout()

    def create_eval_mgr_pub(self):
        """Creates the evaluation manager pub and links it to the original paper."""
        slug = generate_slug(title=self.parentMetadata.title)+generate_random_number_string(4)
        title = "Summary of Evaluations of " + self.parentMetadata.title
        mgr_pub =  self.pubshelper.create_pub(slug=slug, title=title, description=title)
        mgr_pub = retry(sleep=2, retry=3)(self.pubshelper.getPubByIdorSlug)(slug)
        self.pubshelper.authed_request()

    def create_first_eval_pub(self, eval_date=None):
        """Creates the first evaluation pub and links it to the original paper."""
        pass

    def create_eval_pub(self, eval_date=None):
        pass

    def create_eval_title(self):
        title = self.parentMetadata.title
        slug = generate_slug()+generate_random_number_string(4)
        pass


    @staticmethod
    def possible_people(fullname, firstName, lastName):
        """returns a list of possible pubpub members"""
        # first get list of all members
            


    
   
# time saver:
#  
# has to also make summary metrics
EvaluationPackage(
    # can lookup metadata with crossref : https://api.crossref.org/works/10.3386/w31762
    doi="10.1038/s41586-021-03402-5", #todo: for default doi put in a base Unjournal Pubpub doi such as the template 
    # { "doi":"10.1038/s41586-021-03402-5", 
    #             "url":"https://www.nature.com/articles/s41586-021-03402-5"
    #             },
    url=None,#"https://www.nature.com/articles/s41586-021-03402-5"->str,
    # evaluation_manager_author_01="str", # can be id such as "111", name "Joe Doe", or enum Joe_Doe or dict id:"111", name:"Joe Doe"
    # evaluation_manager_author_id="str", # put in anonymous as defulat
    # evaluation_manager_author_name="unknown",
    # evaluation_manager_author_name=None,
    # evaluation_manager_author_name=None,
    
    evaluation_manager_author={
        "id": "",
        "name": "Jim Smith",
    },
    evals=[
        {"author":{
            "name": "anonymous",
        }}, #title and Evaluation - follow template - Evaluation of <title>
        {"author":{
            "name": "Jim Smith",
        }},
        {}
    ],

)