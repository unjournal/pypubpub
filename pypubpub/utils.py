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
