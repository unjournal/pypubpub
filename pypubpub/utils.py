import random
import string
import time


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


#https://www.phind.com/search?cache=dreok6n9yhkai8qqg18mpvbe
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from slugify import slugify  #python-slugify

# Download stop words if not already downloaded
# nltk.download('stopwords')

def generate_slug(title, keep_stop_words=False,slug_length=1):
    """ Generate a slug from a title """
    if(keep_stop_words):
        return slugify(title)
    # Tokenize the title into words
    words = word_tokenize(title)
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.casefold() not in stop_words]
    return slugify(filtered_words)
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