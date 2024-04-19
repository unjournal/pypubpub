import random
import string
import time
import pytest
import requests
from pypubpub import Pubshelper_v6

from tests.conf_settings import email, password, community_id, community_url

def test_simple():
    assert 5 == 5


def test_create_a_pub():
    pub_helper=Pubshelper_v6(
    community_url=community_url,
    community_id=community_id,
    password=password,
    email=email
    )
    slugTestId = "test-" + generate_random_number_string(10);
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
    pub01 = sleep(sleep=2, retry=3)(pub_helper.getPubByIdorSlug)(slugTestId)
    assert pub01 != None or pubNot != {}
    assert pub01["slug"] == slugTestId
    assert pub01["title"] == slugTestId
    pub_helper.delete_pub(pub01["id"])
    time.sleep(1)
    pubNot = pub_helper.getPub(pub01["id"])
    assert pubNot == None or pubNot == {} or not pubNot['pubIds'] or  pubNot['pubIds'] is None 
    pub_helper.logout()




def generate_random_number_string(length):
    return ''.join(random.choice(string.digits) for _ in range(length))


def sleep(sleep=2, retry=3):
    def the_real_decorator(function):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < retry:
                try:
                    value = function(*args, **kwargs)
                    return value
                except Exception as e:
                    print("RETRY LOOP")
                    print(f'Exception {e} occurred')
                    print(f'{retries} of {retry} retries: Sleeping for {sleep} seconds before next retry')
                    time.sleep(sleep)
                    retries += 1
        return wrapper
    return the_real_decorator