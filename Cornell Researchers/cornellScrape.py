import pandas as pd
from bs4 import *
import urllib

url = 'https://research.cornell.edu/featured-researchers-page'
fh = urllib.urlopen(url)
soup = BeautifulSoup(fh,'lxml')
personContent = soup.find_all('div','person-content')
alpha = [x.string for x in soup.find('ul','views-summary').find_all('a')] #First initial of last names from banner

data = []
for letter in alpha:
    url = 'https://research.cornell.edu/featured-researchers/%s'%letter
    fh = urllib.urlopen(url)
    soup = BeautifulSoup(fh, 'lxml')
    personContent = soup.find_all('div', 'person-content')
    for person in personContent:
        lilSoup = BeautifulSoup(str(person),'lxml')
        last,first = [x.strip(',').strip() for x in lilSoup.a.string.strip().encode('ascii','ignore').split('\n')]
        try: dept = lilSoup.span.string.strip().encode('ascii','ignore')
        except: dept = None
        try: email = lilSoup.find('a','offsite-link').string.encode('ascii','ignore')
        except: email = None
        try: phone = lilSoup.find('p','person-phone').string.strip()
        except: phone = None
        data.append([last,first,dept,email,phone])

df = pd.DataFrame(data=data,columns=['Last','First','Dept','Email','Phone'])
df.to_csv('CornellResearchers.csv',index=False)