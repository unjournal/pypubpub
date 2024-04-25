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

def delete_many_pubs(pub_helper, pub_list=[]):
    for p in pub_list:
        pub_helper.delete_pub(p["id"])


def test_simple():
    assert 5 == 5


def test_create_a_pub():
    pub_helper=Pubshelper_v6(
    community_url=community_url,
    community_id=community_id,
    password=password,
    email=email
    )
    slugTestId = "test-" + generate_random_number_string(10)
    print("slugTestId : ", slugTestId)
    pub_helper.login()
    pubNot = None
    pub00 = None
    try:
        pubNot = pub_helper.getPubByIdorSlug(slugTestId)
        print("pubNot exists already so delete it : ",pubNot["slug"], " : " , pubNot["id"])
        pubDelete = pub_helper.delete_pub(pubNot["id"])
        time.sleep(2)
    except requests.HTTPError as e:
        print("HTTPError code exception")
        assert e.response.status_code == 404
        print("need to create test pub")

    pub00 = pub_helper.create_pub(slugTestId,slugTestId,slugTestId )
    # takes time to find new pub
    pub01 = retry(sleep=2, retry=3)(pub_helper.getPubByIdorSlug)(slugTestId)
    assert pub01 != None or pubNot != {}
    assert pub01["slug"] == slugTestId
    assert pub01["title"] == slugTestId
    pub_helper.delete_pub(pub01["id"])
    time.sleep(1)
    pubNot = pub_helper.getPub(pub01["id"])
    assert pubNot == None or pubNot == {} or not pubNot['pubIds'] or  pubNot['pubIds'] is None 
    pub_helper.logout()



def test_create_batch_pubs(pubhelperv6,migratehelperv6):
    pubs_slugs=[]
    for i in range(3):
        slugger = "test-" + generate_random_number_string(10)
        pubs_slugs.append({"slug":slugger, "title":slugger, "description":slugger})
    pubs_batch = migratehelperv6.createPubs(pubs_slugs)
    time.sleep(5)
    pubs_check = pubhelperv6.get_many_pubs(pub_ids = pubs_batch["createdPubIds"] )
    assert len(pubs_check) == len(pubs_slugs)
    pubs_batch['createdPubIds'].sort()
    pubs_check["pubIds"].sort()
    assert pubs_batch['createdPubIds'] == pubs_check["pubIds"]



