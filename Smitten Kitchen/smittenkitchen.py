import pandas as pd
from bs4 import *
import urllib
import sys

try:
    url = sys.argv[1]
except:
    url = 'https://smittenkitchen.com/2017/06/crispy-spiced-lamb-and-lentils/'

fh = urllib.urlopen(url)
soup = BeautifulSoup(fh,'lxml')
recipe = soup.title.string.encode('ascii','ignore')
print recipe
print url
try:
    ingredients = [x.string.encode('ascii','ignore') for x in soup.find('div','jetpack-recipe-ingredients').find_all('li')]
except:
    ingredients = ['Error: read manually from %s'%url]
for x in ingredients:
    print x