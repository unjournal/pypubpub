import random
import re
import string
import time
from datetime import datetime
import traceback

import nltk
nltk.download('punkt') #don't worry: download check if previously downloaded into the environment
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from slugify import slugify  #python-slugify package


def retry(sleep=2, retry=3):
    """ Decorator to retry a function a number of times before giving up"""
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

def generate_random_number_string(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

def get_time_string() -> str:
    now = datetime.now()
    return now.strftime("%H_%M_%S")

def isMaybePubId(t:str):
    if(not t): return False
    t2 = re.sub(r"\s+|-","", t )
    if(not len(t2)==32):
        return False
    t3 = re.sub(r"[a-f0-9]", "", t2.casefold())
    if(len(t3)==0):
        return True
    else:
        return False


# Download stop words if not already downloaded
# nltk.download('stopwords')
#https://www.phind.com/search?cache=dreok6n9yhkai8qqg18mpvbe
def generate_slug(title, keep_stop_words=False,slug_length=0):
    """ Generate a slug from a title """
    if(keep_stop_words):
        return slugify(title)
    else:
        return generate_slug_without_stop_words(title,slug_length)

def generate_slug_without_stop_words(title,slug_length=0, word_min_length=3):    
    # Tokenize the title into words
    words:list[str] = None
    try:
        words = word_tokenize(title)
    except LookupError as e: #if not downloaded
        print("Downloading NLTK stopwords")
        import nltk
        nltk.download('punkt')
    except Exception as e:
        print("other error ::: ")
        print(" : ",e)
        print(traceback.print_exception(e))
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if (len(word)>=word_min_length and(word.casefold() not in stop_words))]
    return slugify("".join(filtered_words))
    # len_f = len(filtered_words) - slug_length
    # if(slug_length==1):
    #     return random.choice(filtered_words)
    # if(slug_length==0 or len_f<=0):
    #     return slugify(filtered_words)
    # if(len_f==0):
    #     pass
    # elif(len_f==1):
    #     filtered_words = filtered_words[0:1]

    # if(len(filtered_words) >= slug_length):
    #     pass
    # else:
        
    # # if(len(filtered_words)=<slug_length):
    #     # return slugify(filtered_words)
    # # Join the filtered words back into a string
    # filtered_title = ' '.join(filtered_words)
    
    # # Convert the filtered title into a slug
    # slug = slugify(filtered_title)
    
    # return slug


def get_domain(s:str):
    """" Get the domain from a URL 
        for example 
        s = "https://testabcd123456789.pubpub.org/pub/nudgesincreasewelfare2286/draft"
        returns 
    """
    smatches = re.match(r"https://(\w|\.)+", s)
    if(smatches and smatches.group()): 
        return smatches.group()


