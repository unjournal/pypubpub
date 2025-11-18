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



# Add "the Long-Run Effects of Psychotherapy on Depression, Beliefs, and Economic Outcomes" draft package
"""
evaluationPackage_bhat_et_al_psychotherapy = EvaluationPackage(
        doi="10.3386/w30011",
        evaluation_manager_author=None, #todo: put in test config
        evaluations=[
            {},
            {} #example of empty eval, where author not yet known
        ],
        email = email,
        password = password,
        community_url = community_url,
        community_id = community_id,
        config = config, # record_pub_conf(email, password, community_id, community_url),
        verbose=True,
        # autorun=True
    )

# Add "Universal Basic Income: Short-Term Results from a Long-Term Experiment in Kenya∗" draft package

evaluationPackage_banerjee_et_al_UBI = EvaluationPackage(
        doi = None,
        url = "https://www.bin-italia.org/wp-content/uploads/2024/01/Kenya-2023.pdf",
        evaluation_manager_author=None, #todo: put in test config
        evaluations=[
            {},
            {} #example of empty eval, where author not yet known
        ],
        email = email,
        password = password,
        community_url = community_url,
        community_id = community_id,
        config = config, # record_pub_conf(email, password, community_id, community_url),
        verbose=True,
        # autorun=True
    )

"""

# Add "Intergenerational Child Mortality Impacts of Deworming: Experimental Evidence from Two Decades of the Kenya Life Panel Survey" draft package -- premature

evaluationPackage_intergen_deworm = EvaluationPackage(
        doi = "10.3386/w31162",
        evaluation_manager_author=None, #todo: put in test config
        evaluations=[
            {},
            {} #example of empty eval, where author not yet known
        ],
        email = email,
        password = password,
        community_url = community_url,
        community_id = community_id,
        config = config, # record_pub_conf(email, password, community_id, community_url),
        verbose=True,
        # autorun=True
    )




#assert(h)
#print("h:", h)


# to run this in command line
# source .venv/bin/activat
# you need to have source installed that and some assoc. packages
# see `readme.md` in this folder
