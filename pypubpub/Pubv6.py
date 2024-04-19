# from sys import ps1
"""Pubpub API helper for v6 """

import requests
import json
from Crypto.Hash import keccak #need hashed passwords for API

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
                raise Exception(
                    f'Request failed with status {response.status_code}: {response.text}'
                )

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


