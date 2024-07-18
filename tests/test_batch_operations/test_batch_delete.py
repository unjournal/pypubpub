import random
import string
import time
import pytest
import requests
from pypubpub import Pubshelper_v6, Migratehelper_v6

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



@pytest.fixture
def create_pub_slugs(autouse=True, number_of_pubs=3):
    pubs_slugs=[]
    for i in range(number_of_pubs):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
    yield pubs_slugs
    return pubs_slugs

def test_the_test():
    assert 5 == 5


def test_delete_many_pubs(pubhelperv6,migratehelperv6):
    """ test to create a batch of pubs and then do cleanup and delete the pubs"""
    pubs_slugs=[]
    for i in range(3+2):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
    pubs_batch = migratehelperv6.createPubs(pubs_slugs)
    time.sleep(5)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check["pubIds"]) == len(pubs_slugs)
    pubs_batch['createdPubIds'].sort()
    pubs_check["pubIds"].sort()
    assert pubs_batch['createdPubIds'] == pubs_check["pubIds"]
    deleted_pubs = pubhelperv6.delete_many_pubs(pubs_batch['createdPubIds'] )
    print( "deleted_pubs", deleted_pubs)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check["pubIds"]) == 0



def test_delete_batch_pubs(pubhelperv6,migratehelperv6):
    """ test to create a batch of 3 pubs and then do cleanup and delete the pubs"""
    pubs_slugs=[]
    for i in range(12):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
    pubs_batch = migratehelperv6.createPubs(pubs_slugs)
    time.sleep(5)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check["pubIds"]) == len(pubs_slugs)
    pubs_batch['createdPubIds'].sort()
    pubs_check["pubIds"].sort()
    assert pubs_batch['createdPubIds'] == pubs_check["pubIds"]
    deleted_pubs = pubhelperv6.batch_delete(pub_ids=pubs_batch['createdPubIds'], pubsById=pubs_check["pubsById"] )
    print( "deleted_pubs", deleted_pubs)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check["pubIds"]) == 0

def test_search_delete_preview_batch_pubs(pubhelperv6,migratehelperv6):
    """ test to create and then search for a batch of pubs and then do a preview (dontdelete=True) batch delete"""
    pubs_slugs=[]
    title_prefix = f"{generate_random_number_string(3)}: Created to be searched, found, and preview (NOT) deleted"
    for i in range(12):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":f"{title_prefix}", "description":"{slugger}"})
    pubs_batch = migratehelperv6.createPubs(pubs_slugs)
    time.sleep(5)
    preview_deletions = pubhelperv6.batch_search_delete(term=title_prefix)
    assert len(preview_deletions["pubIds"]) == len(pubs_slugs)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check["pubIds"]) == len(pubs_slugs)


def test_search_delete_batch_pubs(pubhelperv6,migratehelperv6):
    """ test to create and then search for a batch of pubs and then do a  (dontdelete=False) batch delete"""
    pubs_slugs=[]
    title_prefix = f"{generate_random_number_string(3)}: Created to be searched, found, and preview (NOT) deleted"
    for i in range(12):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":f"{title_prefix}", "description":"{slugger}"})
    pubs_batch = migratehelperv6.createPubs(pubs_slugs)
    time.sleep(5)
    hard_deletions = pubhelperv6.batch_search_delete(dontDelete=False, term=title_prefix)
    assert len(hard_deletions) == len(pubs_slugs)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check["pubIds"]) == 0


def XXtest_search_delete_batch_pubs(pubhelperv6,migratehelperv6):
    """ test to create and then search for a batch of pubs and then do a (dontdelete=False) batch delete"""
    pubs_slugs=[]
    for i in range(12):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
    pubs_batch = migratehelperv6.createPubs(pubs_slugs)
    time.sleep(5)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check) == len(pubs_slugs)
    pubs_batch['createdPubIds'].sort()
    pubs_check["pubIds"].sort()
    assert pubs_batch['createdPubIds'] == pubs_check["pubIds"]
    pubhelperv6.batch_delete(pub_ids=pubs_batch['createdPubIds'] )
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check) == 0

