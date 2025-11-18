import json
import random
import string
import time
#import pytest
import requests
from pypubpub import Pubshelper_v6, Migratehelper_v6

from pypubpub.Pubv6 import EvaluationPackage, record_pub_conf
from pypubpub.utils import generate_random_number_string, retry
from conf import email, password, community_id, community_url

config = record_pub_conf(email, password, community_id, community_url)
print('config:::', config)
print("email conf ... ", email, password, community_id, community_url)


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

#assert(h)
#print("h:", h)


