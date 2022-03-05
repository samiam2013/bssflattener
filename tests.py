
import shutil
import requests
from export import *

def tests():
    """
    this function tests every function and returns `false` if one or more functions failed, and returns `true` if all functions passed
    pretend theres a 25 line long docstring here
    """
    if not test_is_URL():
        return False
    if not test_path_from_URL():
        return False
    if not test_cache_and_replace():
        return False
    if not test_flatten():
        return False
    
    return True  # who needs tests anyway i know my code will always work :troll:

def test_is_URL(): 
    assert is_URL('http://example.com') is True
    assert is_URL('data:0awne;vkjanwe[rihfan') is False
    assert is_URL('/path/to/a/file.ext?key=val') is False
    assert is_URL('/path/to/a/file.ext') is False
    assert is_URL('path/to/a/file.ext') is False

def test_path_from_URL():
    assert path_from_URL('https://example.com/path/file.css?key=value') == '/ext/example.com.file.key-Wyd2YWx1ZSdd.css'
    assert path_from_URL('https://example.com/path/file.css') == '/ext/example.com.file.css'
    assert path_from_URL('https://example.com/path/file') == '/ext/example.com.file'

def test_cache_and_replace():
    new_path = cache_and_replace('https://myres.realty/assets/css/customized.css') 
    print('new path', new_path)
    assert new_path == '/ext/myres.realty.customized.css'
    full_path = '/home/sam/Code/myres.realty/bss_export'+new_path
    assert os.path.exists(full_path)
    with open(full_path) as fh:
        content_len = len(fh.read())
        response = requests.head('https://myres.realty/assets/css/customized.css')
        reported = response.headers['content-length']
        assert content_len == int(reported)
    os.remove(full_path)

def test_flatten():
    bss_export = "/home/sam/Code/myres.realty/bss_export/"
    flatten('/ext/test.html')
    flatten('/ext/test.css')
    assert os.path.exists(bss_export + 'ext/myres.realty.Rentals.js')
    with open(bss_export+'ext/test.css', 'r') as fh:
        content = fh.read()
        assert '/ext/myres.realty.canal_st.h-WycxODc3ZWQyMGIzMzQzYzYyOThiZDg5NjNjMGM2NzBlMCdd.jpg' in content
    for filename in os.listdir(bss_export + 'ext/'):
        os.remove(bss_export + 'ext/'+filename)
    shutil.copy(bss_export + 'test_cases/test.css', bss_export + 'ext/')
    shutil.copy(bss_export + 'test_cases/test.html', bss_export + 'ext/')
