import random
import string
import time
import pytest
import requests
from pypubpub import Pubshelper_v6, Migratehelper_v6

from pypubpub.Pubv6 import EvaluationPackage
from pypubpub.utils import generate_random_number_string, retry
from tests.conf_settings import email, password, community_id, community_url




@pytest.fixture
def pubhelperv6():
    pub_helper=Pubshelper_v6(
    community_url=community_url,
    community_id=community_id,
    password=password,
    email=email
    )
    pub_helper.login()
    yield pub_helper
    pub_helper.logout()

@pytest.fixture
def migratehelperv6(pubhelperv6):
    migratehelprv6 = Migratehelper_v6(pubhelperv6)
    return migratehelprv6

def delete_many_pubs(pubhelperv6, pub_list=[], autouse=True):
    for pubid in pub_list:
        pubhelperv6.delete_pub(pubid)

@pytest.fixture
def setUpandDeletePubs(pubhelperv6, migratehelperv6, create_pub_slugs, autouse=True):
    # migratehelperv6.createPubs(create_pub_slugs)
    pubs_batch = migratehelperv6.createPubs(create_pub_slugs)
    yield pubs_batch
    delete_many_pubs(pubhelperv6, pubs_batch['createdPubIds'] )

def test_create_eval_package():
    evaluationPackage_001 = EvaluationPackage(
        # doi="10.1038/s41586-021-03402-5", #todo: for default doi put in a base Unjournal Pubpub doi such as the template 
        doi="10.3386/w30740", #todo: for default doi put in a base Unjournal Pubpub doi such as the template 
        evaluation_manager_author="1da15791-f488-4371-bcdb-009e054881f3", #todo: put in test config
        # evaluation_manager_author=D_REINSTEIN,

        # evaluation_manager_author={
        #     "id": "",
        #     "name": "Jim Smith",
        # },ww
        evals=[
            {"author":{
                "name": "anonymous",
            }}, #title and Evaluation - follow template - Evaluation of <title>
            {"author":{
                "name": "Jim Smith",
            }},
            {}
        ],
        verbose=True,
        # autorun=True
    )
    assert(h)
    print("h:", h)


@pytest.fixture
def create_pub_slugs(autouse=True, number_of_pubs=3):
    pubs_slugs=[]
    for i in range(number_of_pubs):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
    yield pubs_slugs
    return pubs_slugs

def test_simple():
    assert 5 == 5


# def test_create_a_pub():
#     pub_helper=Pubshelper_v6(
#     community_url=community_url,
#     community_id=community_id,
#     password=password,
#     email=email
#     )
#     slugTestId = "test-" + generate_random_number_string(10)
#     print("slugTestId : ", slugTestId)
#     pub_helper.login()
#     pubNot = None
#     pub00 = None
#     try:
#         pubNot = pub_helper.getPubByIdorSlug(slugTestId)
#         print("pubNot exists already so delete it : ",pubNot["slug"], " : " , pubNot["id"])
#         pubDelete = pub_helper.delete_pub(pubNot["id"])
#         time.sleep(2)
#     except requests.HTTPError as e:
#         print("HTTPError code exception")
#         assert e.response.status_code == 404
#         print("need to create test pub")

#     pub00 = pub_helper.create_pub(slugTestId,slugTestId,slugTestId )
#     # takes time to find new pub
#     pub01 = retry(sleep=2, retry=3)(pub_helper.getPubByIdorSlug)(slugTestId)
#     assert pub01 != None or pubNot != {}
#     assert pub01["slug"] == slugTestId
#     assert pub01["title"] == slugTestId
#     pub_helper.delete_pub(pub01["id"])
#     time.sleep(1)
#     pubNot = pub_helper.getPub(pub01["id"])
#     assert pubNot == None or pubNot == {} or not pubNot['pubIds'] or  pubNot['pubIds'] is None 
#     pub_helper.logout()



# def test_create_batch_pubs(pubhelperv6,migratehelperv6):
#     """ test to create a batch of 3 pubs and then do cleanup and delete the batch of pubs"""
#     pubs_slugs=[]
#     for i in range(3):
#         slugger = "test-" + generate_random_number_string(10)
#         pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
#     pubs_batch = migratehelperv6.createPubs(pubs_slugs)
#     time.sleep(5)
#     pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
#     assert len(pubs_check) == len(pubs_slugs)
#     pubs_batch['createdPubIds'].sort()
#     pubs_check["pubIds"].sort()
#     assert pubs_batch['createdPubIds'] == pubs_check["pubIds"]
#     delete_many_pubs(pubhelperv6, pubs_batch['createdPubIds'] )

# def test_create_empty_title_batch_pubs(pubhelperv6,migratehelperv6):
#     """ system should fail to create a pub with empty title, 
#         since all evaluations are based on the parent paper title
#     """
#     pubs_slugs=[{},{},{}]
#     check_missing_args = False
#     # for i in range(3):
#     #     slugger = "test-" + generate_random_number_string(10)
#     #     pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
#     try:
#         pubs_batch = migratehelperv6.createPubs(evals=pubs_slugs)
#     except TypeError as e:
#         check_missing_args = all(word in e.__str__() for word in ["missing", "positional", "argument"])
#         # assert( all(word in e.__str__() for word in ["missing", "positional", "argument"]) )
#         assert(check_missing_args)
#     assert(check_missing_args)
#     # time.sleep(3)
#     # pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
#     # assert len(pubs_check) == len(pubs_slugs)
#     # pubs_batch['createdPubIds'].sort()
#     # pubs_check["pubIds"].sort()
#     # assert pubs_batch['createdPubIds'] == pubs_check["pubIds"]
#     # delete_many_pubs(pubhelperv6, pubs_batch['createdPubIds'] )


