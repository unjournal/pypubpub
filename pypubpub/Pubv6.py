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
import copy
from concurrent import futures 
import math
import warnings
from .utility import Titlemachine

from pypubpub.utils import generate_random_number_string, generate_slug, isMaybePubId, retry #need hashed passwords for API
utils_retry=retry

SlugTuple=namedtuple( 'evaluationslugtitle', 'slug title')
bibtex_tuple = namedtuple('BibTeX', 'author title year month')

@dataclass
class UserAttribution( ): #todo:   TypeDict with @dataclass  is   and counterproductive because they can clash
    userId: str
    roles: list[str] =None
    affiliation:str=None
    isAuthor:bool=True
    orcid: str = None
    name: str = None

class UserAttributeDict(TypedDict ):
    """Purely for typeing purposes to match UserAttribution dataclass"""
    userId: str
    roles: list[str] =None
    affiliation:str=None
    isAuthor:bool=True
    orcid: str = None
    name: str = None


class Pubshelper_v6:
    def __init__(self, community_url="https://unjournal.pubpub.org", community_id="d28e8e57-7f59-486b-9395-b548158a27d6", email='contact@unjournal.org',password = 'pasw0rt' ):
        self.community_url = community_url
        self.community_id = community_id
        self.cookieJar = None
        self.logged_in = False
        self.email = email
        self.password = password
        self.requests = requests.Session()


    def login(self):
        print("email ::", self.email)
        print("password ", self.password[:2], "..XX..", self.password[-2:])
        k = keccak.new(digest_bits=512)
        k.update(self.password.encode())
        response = self.requests.post(
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

    def authed_request(self, path, method='GET', body=None, options=None, additionalHeaders=None, format='json'):

            response = self.requests.request(
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
                print("authed_request error::", response.status_code, response.text)
                print("path::", path)
                print("method::", method)
                print("body::", body)
                response.raise_for_status()
            if(format=='json'): return response.json()
            if(format=='text'): return response.text
            if(format=='raw'): return response

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
        """connect 2 pubs. Intended for Pubs within PubPub and the same community.
            For connecting to an external resource, its suggested to use connect_pub_to_external
        """

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
    def connect_pub_to_external(self, 
                                srcPubId,
                                title=None,
                                url=None,
                                publicationDate=None,
                                description=None,
                                doi=None,
                                targetPubId=None,
                                avatar=None,
                                contributors=[],
                                relationType="review",
                     rank=None,
                     pubIsParent=False,
                     approvedByTarget=True
                     ):
        """
            ###
            # Note: To connect to an external article, you can first try the connect_pub method. Many external resources have a
            # Pubpub Id. So you can use the connect_pub method after looking up its Pubpub Id.
            #
            #  This method can be used when an external resource does not yet have a Pubpub Id. After using this method to connect
            # to an external resource, the external resource seems to get a Pubpub Id assigned to it, which could be used in the future.
            ###
        """
        #todo: possibly check if the doi already contains doi.org, or better follow the redirect to the actual url
        if (not url and doi and type(doi)==str):
            if( not doi.startswith('https://doi.org/') ):
                url = f'https://doi.org/{doi}'
            else:
                url = doi
        print("+connect_pub_to_external ::", srcPubId, title, url, publicationDate, description, doi, avatar, contributors, relationType)
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

    def set_attribution(self, pubId, userId, isAuthor=True, roles=None, affiliation=None)->dict:
        body = {
            "communityId" : self.community_id,
            "pubId": pubId,
            "userId":userId,
            # "roles": ["Writing – Review & Editing","Evaluation Manager",],
            "roles": roles,
            # "attribution": attribution,
            "isAuthor": isAuthor,
            "affiliation": affiliation,
        }
        print( "set_attribution ::", body)
        return self.authed_request(
            path = 'pubAttributions',
            method = "POST",
            body = body

        )

    def set_attributions_multiple(self, pubId:str, attributions:list[ UserAttributeDict|UserAttribution], isAuthor=True, roles=None, affiliation=None)->list[dict]:
        """
            set mulitple authors,editors,contributors at once
            attributions: list of UserAttribution or UserAttributeDict required
            pubId: str required
            isAuthor: bool optional
            roles: list[str] optional
            affilition: str optional
        """
        if( attributions and  type(attributions[0])!=dict): 
            attributions =  [a.__dict__ for a in attributions if a]
        print("set_attributions_multiple  attributions ::", attributions)
        print(pubId, self.community_id)
        return self.authed_request(
            path = 'pubAttributions/batch',
            method = "POST",
            body = {
                "communityId" : self.community_id,
                "pubId": pubId,
                # todo: move these fields into the attributions field
                # "roles": ["Writing – Review & Editing","Evaluation Manager",],
                # "roles": roles,
                "attributions": attributions,
                # "isAuthor": isAuthor,
                # "affiliation": affiliation,
            }

        )

    def update_attribution(self, pubId, userId, isAuthor=None, roles:list=None, affiliation:str=None, other_options:dict=None)->dict:
        body = {
            "communityId" : self.community_id,
            "pubId": pubId,
            "userId":userId,
        }
        if(isAuthor!=None):
            body['isAuthor'] = isAuthor
        if(roles):
            body['roles'] = roles
        if(affiliation):
            body["affiliation"] = affiliation
        if(other_options):
            body.update(other_options)
        print( "set_attribution ::", body)
        return self.authed_request(
            path = 'pubAttributions',
            method = "PUT",
            body = body
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


    def get_many_pubs(
            self, 
            limit = 200, 
            offset = 0, 
            ordering= {'field': 'updatedDate', 'direction': 'DESC'}, 
            collection_ids=None, 
            pub_ids=None, 
            pubOptions={}, 
            alreadyFetchedPubIds=[],
            isReleased=False,
            term:str = '',
            relatedUserIds:list = [],
            ):
        """Get many pubs, also sends a query to the Pubpub backend
            some but not all of the fields are described in the online documentation for options: https://www.pubpub.org/apiDocs#/paths/api-pubs-many/post
            Parameters
            ----------
            isReleased: bool, optional
                default is false which will return only unpublished drafts. true returns published pubs. None returns both drafts and published pubs.
            relatedUserIds: list[str], optional
                list of user ids connected to the Pub. Could be authors, contributors, editors, or other types of connections.
        """

        response = self.authed_request(
            'pubs/many',
            'POST',
            {
                'alreadyFetchedPubIds': alreadyFetchedPubIds,
                'pubOptions': {
                    'getCollections': True,
                    **pubOptions
                },
                'query': {
                    'communityId': self.community_id,
                    **( {'collectionIds': collection_ids} if collection_ids else {}),
                    **(   {'withinPubIds': pub_ids} if pub_ids else {}),
                    **( {'term':term} if term else {}),
                    **( {'isReleased':isReleased} if isReleased else {}),
                    **( {'relatedUserIds':relatedUserIds} if relatedUserIds else {}),
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
        print("+create_pub  slug::", slug)
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
    
    def track_delete_pub(self,pub_id, slug=None, title=None):
        """Helper delete method used by the batch_delete method. 
        """
        response = None
        try:
            response = self.delete_pub( pub_id=pub_id)
            return {"pub_id":pub_id,"title":title, "slug":slug, "response":response}
        except Exception as e:
            return {"pub_id":pub_id,"title":title, "slug":slug, "response":None, "error":e}
        
    def batch_delete(self, pub_ids:list[str], pubsById:dict=None):
        """delete a batch of pubs at once by repeatedly calling the Pubpub delete API
        """
        result_from_deletes = []
        chunks = (pub_ids[i*5:i*5+5] for i in range(math.ceil(len(pub_ids)/5)))
        

        for chunk in chunks:
            x = self.helper_delete_n( chunk, pubsById=pubsById)
            result_from_deletes.append(x)
        return result_from_deletes


    def helper_delete_n(self, pub_id_list:list, pubsById:dict=None):
        with futures.ThreadPoolExecutor() as executor:
            delete_results = []
            for pubId in pub_id_list:
                p =  pubsById and pubId in pubsById
                slug=p and pubsById[pubId]['slug']
                title=p and pubsById[pubId]['title']
                delete_results.append(
                    executor.submit(
                        self.track_delete_pub, pub_id=pubId, slug=slug, title=title
                    )
                )
            return [f.result() for f in futures.as_completed(delete_results)]

    def delete_many_pubs(self, pub_list=[], pubsById:dict=None):
        """Delete many pubs at once by repeatedly calling the Pubpub delete API
            Often errors out with a 500 error if called to delete more than 5 Pubs
            Also may be slower than the batch_delete method.
            Recommendation: Use batch_delete instead.
        """
        if(len(pub_list)>5):
            warnings.warn('Often errors out with a 500 error if called to delete more than 5 Pubs. Recommendation: Use batch_delete instead.')
        result_from_deletes = []
        for pubid in pub_list:
            x = self.track_delete_pub( pubid)
            self.delete_pub(pubid)
            result_from_deletes.append(x)
        return result_from_deletes


    def search_pubs(self, term:str='', limit=200, offset=0, ordering={'field': 'updatedDate', 'direction': 'DESC'}, isReleased=False, collection_ids=None, pub_ids=None, alreadyFetchedPubIds=[], relatedUserIds=[]):
        """Search for pubs using the method get which uses the Pubpub API which can search title and contributors such as author, editor"""
        return self.get_many_pubs(limit=limit,offset=offset,ordering=ordering,isReleased=isReleased,collection_ids=collection_ids,pub_ids=pub_ids,alreadyFetchedPubIds=alreadyFetchedPubIds,term=term,relatedUserIds=relatedUserIds)

    def search_text(self, term:str='', limit=200, offset=0, ordering={'field': 'updatedDate', 'direction': 'DESC'}, isReleased=False, collection_ids=None, pub_ids=None, alreadyFetchedPubIds=[], relatedUserIds=[]):
        """Search for Pubs using Algolia full text search
            NOT YET IMPLEMENTED.
        """
        return

    def batch_search_delete_text(self, term:str='', limit=200, offset=0, ordering={'field': 'updatedDate', 'direction': 'DESC'}, isReleased=False, collection_ids=None, pub_ids=None, alreadyFetchedPubIds=[], relatedUserIds=[]):
        """Search for Pubs using Algolia full text search, and then batch delete.
            NOT YET IMPLEMENTED.
        """
        return


    def batch_search_delete(
            self, 
            dontDelete=True,
            limit=200, 
            offset=0, 
            ordering={'field': 'updatedDate', 'direction': 'DESC'}, 
            isReleased=False, 
            collection_ids=None, 
            pub_ids=None, 
            alreadyFetchedPubIds=[], 
            term:str='', 
            relatedUserIds=[]):
        """Search for pubs and delete them in batches. 
            parameter `dontDelete`= True  by default. Set to False to actually delete the pubs.   
            The other parameters are the same as the method `get_many_pubs`
            Parameter `isReleased` defualts to `False`, which will return only unpublished drafts. `True` deletes only published Pubs. `None` deletes both drafts and published pubs.
            Returns a list of results from the delete operation.           
        """
        pubs00 = self.get_many_pubs(limit=limit,offset=offset,ordering=ordering,isReleased=isReleased,collection_ids=collection_ids,pub_ids=pub_ids,alreadyFetchedPubIds=alreadyFetchedPubIds,term=term,relatedUserIds=relatedUserIds)
        if(dontDelete):
            return pubs00
        return self.batch_delete(*pubs00)

    def getPub(self, pub_id):
        return self.get_many_pubs(pub_ids=[pub_id])
    
    def update_pub(self, body:dict, pub_id:str, community_id:str=None):
        """ Update a pub
            see: https://www.pubpub.org/apiDocs#/paths/api-pubs/put
            You can also update author attributions by setting the body to:
            ```
             { 
                "attributions": [ { "id": "string", "pubId":"string", "isAuthor": bool, "roles": [ "string" ], "affiliation": "string" } ],
                "pubId": "string",
                "communityId": "string"
            }
            ```
        """
        if(pub_id):
            body.update({"pubId":pub_id})
        body.update({"communityId":community_id} if community_id else {"communityId":self.community_id})
        return self.authed_request(
            path='pubs',
            method="PUT",
            body=body
        )
    
    def get_pub_as_resource(self, pubId):
        """Get pub as a resource
            see: https://www.pubpub.org/apiDocs#/paths/api-pubs-pubId--resource/get
        """
        return self.authed_request(
            f'pubs/{pubId}/resource',
            'GET'
        )
        
    def get_pub_text(self, pubId):
        """Get text of a pub
            see: https://www.pubpub.org/apiDocs#/paths/api-pubs-pubId--text/get
        """
        return self.authed_request(
            f'pubs/{pubId}/text',
            'GET'
            )

    def replace_pub_text(self, pubId, attributes:dict, content:list[dict]=[None], doc:dict=None, replace_method="replace", publishRelease=False):
        """Replace the text of a pub
            see: https://www.pubpub.org/apiDocs#/paths/api-pubs-pubId--text/put
        """        
        body={
                "doc": doc if doc else  {
                    "type": "doc",
                    "attrs": attributes,
                    "content": content
                },
                # "clientID": "api",
                "publishRelease": publishRelease,
                "method": replace_method
            }
        return self.authed_request(
            path=f'pubs/{pubId}/text',
            method='PUT',
            body=body
            )

    def downloadpubexport(self, pubId, format="plain", http_response_format= 'text'):
        """Download a pub export
            first initiate export,
            then poll worker task
            then GET file at the download url shown in the worker task json:
            ```
             {
                "id": "ff8e79dc-c12b-454e-a4fe-49460c9c3d88",
                "isProcessing": false,
                "error": null,
                "output": {
                    "url": "https://assets.pubpub.org/z3idtunr/eeddfc89-00e0-4e14-84b5-6290f9c6762f.txt"
                }
            }
            ```
        """
        response = self.export_initiate(pubId, format)
        url=None
        print('export respon :: ', response)
        if('url' in response):
            url = response['url']
        elif('taskId' in response):
            task_id = response['taskId']
            response = self.workertaskpoll(task_id, sleep=5, retry=15)
            url = response['output']['url']

        response = retry(5,15)(self.requests.request)(method='GET',url=url)
        if(http_response_format=='text'): return response.text
        if(http_response_format=='json'): return response.json()
        if(http_response_format=='raw'): return response.raw
        if(http_response_format=='content'): return response.content
        return response

    def export_initiate(self, pubId, format="plain"):
        """Initiate a pub export"""
        return self.authed_request(
            path='export',
            method= 'POST',
            body={ "pubId": pubId, "format": format , "communityId":self.community_id}
        )
    
    
    def workertaskpoll(self, task_id, sleep=1, retry=10):
        return utils_retry(1, 10)(self.workertask)(task_id)

    def workertask(self, task_id):
        """Get worker task status"""
        response = self.authed_request(path=f'workerTasks?workerTaskId={task_id}')
        if(response['isProcessing']==False and not response['error']):
            return response
        elif(response['error']):
            raise Exception(response['error'])
        else:
            raise Exception("worker task still processing")

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

    def search_pubpub_users(self, q:str):
        """search for pubpub user ids"""
        return self.authed_request(
            path=f'search/users?q={q}',
        )

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
                



class OrigPaperMetadata():
    # doi:str=None
    # url:str=None
    # title:str=None
    # description:str=None
    # bibtex_metadata:bibtex_tuple=None
    

    def __init__(self, doi:str = None, url:str=None,  title:str=None, description:str=None):
        self.doi=doi
        self.url=url
        self.title=title
        self.description=description
        self.bibtex_metadata = None
        self.crossref_data = None
        
    def lookup(self):
        if(self.doi):
            self.bibtex_metadata = self.doi2bib()

        if(self.doi and self.bibtex_metadata):
            print("doi response successs:", self.bibtex_metadata)
            self.title = self.bibtex_metadata.title
            self.author = self.bibtex_metadata.author
            self.year = self.bibtex_metadata.year
            self.month = self.bibtex_metadata.month
            return self.bibtex_metadata
        elif(self.doi):
            print("bad response from doi, trying crossref")
            self.crossref_data = self.check_crossref()
            if(self.crossref_data):
                self.title = self.crossref_data.title if 'title' in self.crossref_data else None
                self.author = self.crossref_data.author if 'author' in self.crossref_data else None                
                return self.crossref_data
            else:
                return None
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
                print("Unable to find doi : ", self.doi)
                print("trying `crossref` next")
                return None
            if response.status_code >= 200 or response.status_code <300:
                self.bibtex_metadata =  self.parse_bibtex_string( response.text )
                print("+doi2bib response.txt::", response.text)
                print("self.bibtex_metadata :: ",self.bibtex_metadata)
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
            return bibtex_tuple(author, title, year, month)
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
            print("crossref undable to find doi : ", self.doi)
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

NODOI = "NODOI"

class EvaluationPackage():
    """
     This class is high level wrapper to make or initialize a Pubpub evaluation package
     It can be used from commandline or in a notebook or script to create a new evaluation package.
     By default, once the arguments are passed, `autorun=True` and it will start making calls to Pubpub to look up the parent paper metadata and create the Pubs
     `autorun=False` can be set to delay the process_run() call until later.

     Example:
     ```
     EvaluationPackage(
        doi="10.1038/s41586-021-03402-5", 
        evaluation_manager_author="111-111111",
        evals=[
                "87999afb-d603-4871-947a-d8da5e6478de",
                {"author":{
                    "id": "87999afb-d603-4871-947a-d8da5e6478de",
                }},  
                {},
                {}
            ],
        autorun=False
    )
    ```
    This will look up metatadata for the doi, and then create 4 Pubs, one for the evaluation summary,
      and 4 for the evaluations. 
      The pubs will be linked to each other as supplement, and will be link as a review to the parent paper as external resource. In some cases it may be possible link to the parent paper as a Pubpub pub, but this is not yet implemented. 
      The evaluation summary will have multiple authers - the evaluators listed, and the evaluation manager.
      The evals array speciefies properties for each pub. In order:
        1. The first entry is just a string, and it will used as the author id for the first pub.
        2. The second entry only specifies the author id, and it will be used as the author id for the second pub.
        3 - 4. The third and fourth entries are empty dicts, and they will be used to create the third and fourth pubs, with no author. The author will need to be added later.

        Parameters
        ----------   
        doi : str, optional
            The doi of the parent paper
        url : str, optional
            The url of the parent paper. If doi is not provided, this will be used to 1) point to parent paper and 2)look up the parent paper metadata.
        evaluation_mananger_author : str, optional
            The author id of the evaluation manager. This will be used to create the evaluation summary pub.
        evaluations : list of dicts, optional
            A list evaluations to create. For each evaluation enter a dict, each specifying properties for a pub. To create a placeholder pub without author, use an empty dict. To create a pub with an author, use a dict with an `author` key. For `author` an id can be specified. If the author is not registered with pubpub a string of a name can be specified.
        config : record_pub_conf, optional
            contains login information for pubpub. email, password, community_id, community_url. if not pass as an argument then email, password, community_id, and community_url must be passed as arguments.
        email : str, optional
        password: str, optional
        community_id: str, optional
        community_url: str, optional
        title: str, optional
            title to use in case doi is not provided
        doi_primary_truth: bool, optional
        autrun: bool, optional
            default is True. When True, the process_run() method will be as part of initialization and instantiation immediately. If False, the process_run() method will not be called, and must be called later.
        verbose: bool, optional
            default is True. When True, some of the configuration will be printed to the console.
            
        """
    def __init__(
            self, 
            doi:str|dict, 
            url:str=None,
            title:str=None,
            evaluation_manager_author:str|dict|int = None, 
            evaluations:list = None,
            config:record_pub_conf=None,
            email:str=None, 
            password:str=None, 
            community_id:str=None, 
            community_url:str=None,
            doi_primary_truth=True,
            template_ev_summary_id="561e0e75-2be7-492d-b5f4-986b4acaae83",
            template_ev_summary_community_id="d28e8e57-7f59-486b-9395-b548158a27d6",
            template_ev_summary_url = "https://unjournal.pubpub.org/pub/7s6czeed",
            template_ev_summary_community_url = "https://unjournal.pubpub.org",
            template_ev_summary_text = None,
            template_evaluation_id="d630ba11-57a3-4ab3-a670-2ad5a621efbd",
            template_evaluation_community_id="d28e8e57-7f59-486b-9395-b548158a27d6",
            template_evaluation_community_url = "https://unjournal.pubpub.org",
            template_evaluation_url="https://unjournal.pubpub.org/pub/vag4d5h9",
            template_evaluation_text = None,
            title_method_init=Titlemachine.title_method,
            autorun=True,
            verbose=True
            ):
        self.doi = doi
        self.evaluation_manager_author = evaluation_manager_author
        self.evaluations_input = evaluations
        self.config = config
        self.email = email
        self.password = password
        self.community_id = community_id
        self.community_url = community_url 

        self.url=url
        self.title=title
        self.doi_primary_truth = doi_primary_truth

        self.title_method_init = title_method_init 

        self.template_ev_summary_id = template_ev_summary_id
        self.template_ev_summary_url = template_ev_summary_url
        self.template_ev_summary_community_id = template_ev_summary_community_id
        self.template_ev_summary_community_url =  template_ev_summary_community_url #template_ev_summary_url.split('/')[2]
        self.template_ev_summary_text = template_ev_summary_text


        self.template_evaluation_id = template_evaluation_id
        self.template_evaluation_url = template_evaluation_url
        self.template_evaluation_community_id = template_evaluation_community_id
        self.template_evaluation_community_url = template_evaluation_community_url #template_evaluation_url.split('/')[2]
        self.template_evaluation_text = template_evaluation_text
        self.template_evaluation_text = template_evaluation_text

        self.pubshelper = None
        self.migratehelper = None

        if((not doi or doi == "NODOI" ) and (not url or not title) ):
            raise Exception( "doi or url or title must be provided")
        if(doi == "NODOI"):
            self.doi = None

        self.parentMetadata = None
        # self.remainingPubs=[] # if managing activities use these 2 lists to manage completed and wip 
        self.eval_summ_pub:dict = None
        self.activePubs:tuple[str,dict]=[] #type is a tuple of the (pubId, dict of pub)
        # self.completedPubs=[]
        self.init_conf_setting()
        self.eval_mgr={}
        self.eval_authors=[]
        self.set_eval_mgr_author()
        self.set_eval_authors()
        self.authors_all = [a for a in [self.eval_mgr, *self.eval_authors] if a]

        if(verbose):
            self.print_conf()
        if(autorun):
            self.init_login()
            self.process_run()
        else:
            self.title_method = self.title_method_init(parent_title=self.title)

    def init_conf_setting(self):
        if(not self.config):
            self.config = record_pub_conf(self.email, self.password, self.community_id, self.community_url)
            # todo: remove workaround for D's machine
            self.config.email = self.email
            self.config.password = self.password
            self.config.community_id = self.community_id
            self.config.community_url = self.community_url
            return self.config
        
    def init_login(self):
        self.pubshelper = Pubshelper_v6(**self.config.__dict__)#//(community_url=self.community_url, community_id=self.community_id, email=self.config.email, password=self.config.password)
        self.pubshelper.login()
        self.migratehelper = Migratehelper_v6(self.pubshelper)

    def print_conf(self):
        print("configuration conf :: ______ ")
        g=[f"{k}:{v}" for k,v in self.config.__dict__.items() if k in ['email',  'community_id', 'community_url']]
        print(g)

    def connect_papers(self):
        pass
    
    def lookup_parent_paper(self):
        """lookup original parent paper in doi.org and crossref"""
        #lookup original
        # todo: look up original in pubpub, if not there, just link the first pub
        # doi, url = self.lookup_parent_paper
        self.parentMetadata  = OrigPaperMetadata(doi=self.doi, url=self.url, title=self.title)
        self.parentMetadata.lookup()
        bib_meta,crossr_data , title= self.parentMetadata.bibtex_metadata, self.parentMetadata.crossref_data, self.parentMetadata.title
        if(self.doi and not(bib_meta or crossr_data)):
            raise Exception("Unable to find by using doi")
        if(self.doi and not title):
            raise Exception("Unable to find title")
        return self.parentMetadata
        
    def activePubsMaintainList(self):
        pass

    def process_run(self):
        """Runs the process of initial original paper lookup, followed by pub creation, and then linking the pubs together."""
        self.parentMetadata = self.lookup_parent_paper()
        print("sel.parentMetadata : ", self.parentMetadata.__dict__) 
        
        #create evaluation manager Pub
        self.eval_summ_pub = self.create_base_pub(
            authors_ids=[UserAttributeDict(userId=a.get('userId'),  isAuthor=True) for a in self.authors_all if a],
            title_method=(lambda x: f"Evaluation Summary of {x}"),
        )

        self.create_evaluation_pubs(title_method=self.title_method_init(parent_title= self.parentMetadata.title))
        self.link_evaluation_pubs()
        self.associate_authors_to_eval_summary()
        self.put_template_doc(targetPubId=self.eval_summ_pub['id'], template_id=self.template_ev_summary_id, community_id=self.template_evaluation_community_id, community_url=self.template_ev_summary_community_url)
        for i, evaluation in self.activePubs:
            self.put_template_doc(targetPubId=evaluation['id'], template_id=self.template_evaluation_id, community_id=self.template_evaluation_community_id, community_url=self.template_evaluation_community_url)


        
        if(self.eval_summ_pub):
            print(f"done   :::  doi:{self.doi}, parent:{self.parentMetadata}")
            return
        else:
            print("error")
            return "error"

    def TODELETE_create_eval_summary_pub(self):
        """
        Creates the evaluation summary pub and links it to the original paper.
        author of evaluation summary 
        - evvaluators
        - evaluation manager (last) 
        """
        slug = generate_slug(title=self.parentMetadata.title)+generate_random_number_string(4)
        title = "Summary of Evaluations of " + self.parentMetadata.title
        mgr_pub =  self.pubshelper.create_pub(slug=slug, title=title, description=title)
        mgr_pub = retry(sleep=2, retry=6)(self.pubshelper.getPubByIdorSlug)(slug)
        self.pubshelper.set_attribution(pubId=mgr_pub['id'], userId=self.eval_mgr.get('userId'))
        self.pubshelper.connect_pub_to_external(srcPubId=mgr_pub['id'], title="Original Article", url=f"https://doi.org/{self.doi}", publicationDate=None, description="Original Article", doi=self.doi)


    def create_base_pub(self, authors_ids:str|UserAttribution|list[UserAttribution|UserAttributeDict]=None, title_method=lambda x: f"Evaluation of {x}")->dict: #todo : make more return types to properly check 
        """Generic Reusable Evaluation Creation Method: Creates a pub and links it to the parent pub, and author"""
        slug = self.slugtitle().slug
        title = title_method(self.parentMetadata.title or self.title)
        pub =  self.pubshelper.create_pub(slug=slug, title=title, description=title)
        pub = retry(sleep=2, retry=6)(self.pubshelper.getPubByIdorSlug)(pub['id'])
        pub = pub or retry(sleep=5, retry=6)(self.pubshelper.getPubByIdorSlug)(slug)

        print("pub : ", pub,pub['id'] )
        self.pubshelper.connect_pub_to_external(srcPubId=pub['id'],  doi=self.doi, title=self.parentMetadata.title or self.title, relationType="review", url=self.url)
        if(not authors_ids):
            return pub
        if( type(authors_ids)==str or type(authors_ids)!=list ):
            userId = authors_ids \
                if(type(authors_ids)==str) \
                else authors_ids['userId'] \
                    if('userId' in authors_ids) \
                    else authors_ids.userId
            self.pubshelper.set_attribution( pubId=pub["id"], userId=userId)
            return pub
        if( type(authors_ids)==list):
            helper_id_name= lambda n: UserAttributeDict(userId=n, isAuthor=True) #if(isMaybePubId(n)) else UserAttributeDict(name=n, isAuthor=True)
            helper_uas = lambda a: helper_id_name(a) if(type(a)==str) else a
            authors_list_1 = [helper_uas(a) for a in authors_ids if a  ]
            self.pubshelper.set_attributions_multiple(pubId=pub["id"], attributions=authors_list_1)
            return pub

    def slugtitle(self, title=None):
        print("+slugtitle self.parentMetadata.title:::", self.parentMetadata.title)
        print("+slugtitle title:::", title)
        title = title or self.parentMetadata.title or self.title
        title = title if(title) else generate_random_number_string(4)
        print('+2 slugtitle title:::', title)
        slug = generate_slug(title)+generate_random_number_string(4)
        print('+slugtitle slug:::', slug)
        return SlugTuple(slug=slug, title=title)

    def create_evaluation_pubs(self, set_author=True, title_method=None):
        """Creates the evaluation pubs and links them to the original paper.
           By default the author is added to the Pub. This can be turned of by setting `set_author=False` 
        """
        for i, evaluation in enumerate(self.evaluations_input):
            auth = self.author_id_from_eval(evaluation=evaluation, dict_output=True)
            eval_temp = self.create_base_pub(
                authors_ids = auth.get('userId') if auth else None, #UserAttributeDict(userId=auth.get('userId'),  isAuthor=True),
                title_method = title_method or self.title_method,
            )
            self.activePubs.append((eval_temp['id'] , eval_temp))
        return self.activePubs

    def link_evaluation_pubs(self):
        """Links the evaluation pubs to the evaluation summary pub, and each other."""
        for i, evaluation in self.activePubs:
            self.pubshelper.connect_pub( 
                srcPubId=evaluation['id'], 
                targetPubId=self.eval_summ_pub['id'],  
                relationType="supplement", 
                pubIsParent=False, 
                approvedByTarget=True
            )

    def associate_authors_to_eval_summary(self):
        """Associates the authors of the evaluation pubs to the evaluation summary pub."""
        attributions=[
            UserAttributeDict(userId=a.get('userId'), isAuthor=True)
             for a in 
             self.authors_all
             if a
        ]
        author_attrib = self.pubshelper.set_attributions_multiple(pubId=self.eval_summ_pub["id"], attributions=attributions)
        return author_attrib
    
    def set_eval_mgr_author(self):
        """Sets the evaluation manager author id,name from the input."""
        mgr = {"author": self.evaluation_manager_author}
        self.eval_mgr = self.author_id_from_eval( evaluation=mgr, dict_output=True)
        return self.eval_mgr

    def set_eval_authors(self):
        """Sets the evaluation authors internal property from the initial input."""
        self.eval_authors = self.authors_for_only_evals(dict_output=True)
        pass

    def authors_for_only_evals(self, dict_output=False)->list[str]:
        """returns a list of author ids for only the evals, not the evaluation manager"""
        eval_authors = []
        for evaluation in  self.evaluations_input:
            eval_authors.append(self.author_id_from_eval(evaluation=evaluation, dict_output=dict_output))
        return eval_authors

    def TODELETE_author_id_for_eval_mgr(self)->str: #todo: make a property
        """
        returns the author id for the evaluation manager from the internal state of an EvaluationPackage instance
        currently just returns the field without processing
        """
        if( type(self.evaluation_manager_author)==str and isMaybePubId(self.evaluation_manager_author)):
            return self.evaluation_manager_author
        else:
            return self.evaluation_manager_author #todo: i


    def TODO_remove_author(id: str = None, edgeId = None):
        """Remove an author from a pub"""
        pass



    
    @staticmethod
    def author_id_from_eval(evaluation:dict|str, dict_output=False):
        """
        returns the author id or string of name from an evaluation dict in the evaluations list
        does not yet support name lookup
        if the author is a string, it is assumed to be a pubpub id or a name
        examples of evaluation dict parsing
        1. evaluation is not a dict but is a string, then check if the string is a udid or a name
            `"87999afb-d603-4871-947a-d8da5e6478de"`
        2. {"author": "87999afb-d603-4871-947a-d8da5e6478de"}
        3. {"author": {"id": "87999afb-d603-4871-947a-d8da5e6478de", "name": "Jim Smith"}} 
        4X. NOT SUPPORTED YET {"author": "Jim Smith"} 

        Parameters
        ----------
        evaluation : dict|str
            The evaluation dict to parse
        dict_output : bool, optional
            If True, the output will be a dict with the keys `id` and `name`. If False, the output will be a string of the id. The default is False.
        """
        def helper_extract_id_name(evaluation):
            if(not evaluation):
                return None, None
            if(type(evaluation)==str):
                if( isMaybePubId(evaluation)):
                    return evaluation, None
                else:
                    return None, evaluation
            if(type(evaluation)==dict ):
                if("author" not in evaluation or not evaluation["author"]):
                    print("AUTHOR-ID-NOT-FOUND-OR_DO-LOOK-UP")
                    return None, None
                if(type(evaluation["author"])==str):
                    return helper_extract_id_name(evaluation["author"])
                if(type(evaluation["author"])==dict):
                    return evaluation["author"].get('id'), evaluation["author"].get('name')
            else:
                return None, None
        if(not evaluation):
            return None
        userId, name = helper_extract_id_name(evaluation)
        if(dict_output==False):
            return userId
        a={'userId':userId, 'name':name }
        a = {k:v for k,v in a.items() if v is not None}
        return a

    def put_template_doc(self, targetPubId, template_id, community_id, community_url, template_text=None):
        """Puts a template document into a pub."""
        templatepubpub = copy.deepcopy(self.pubshelper)
        templatepubpub.community_id = community_id
        templatepubpub.community_url = community_url
        template = template_text if template_text else  templatepubpub.get_pub_text( pubId=template_id)
        print('template :::: :: ::', template)
        self.pubshelper.replace_pub_text( pubId=targetPubId, doc =template, attributes=None)



"""
Example usage:


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
    evaluations=[
        {"author":{
            "name": "anonymous",
        }}, #title and Evaluation - follow template - Evaluation of <title>
        {"author":{
            "name": "Jim Smith",
        }},
        {}
    ],
    autorun=False

)


 
EvaluationPackage(
    doi="10.1038/s41586-021-03402-5", #todo: for default doi put in a base Unjournal Pubpub doi such as the template 
    evaluation_manager_author="111-111111",
    # evaluation_manager_author=D_REINSTEIN,

    # evaluation_manager_author={
    #     "id": "",
    #     "name": "Jim Smith",
    # },
    evaluations=[
        {"author":{
            "name": "anonymous",
        }}, #title and Evaluation - follow template - Evaluation of <title>
        {"author":{
            "name": "Jim Smith",
        }},
        {}
    ],
    autorun=False
)
""" 
