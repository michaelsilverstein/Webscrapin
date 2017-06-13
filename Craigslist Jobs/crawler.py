import urllib,re,json,xlsxwriter
from bs4 import *
from collections import OrderedDict

def page_scraper(link_ext,home):
    #Main
    page_prefix = 'http://rochester.craigslist.org/%s.html'
    full_link = page_prefix%link_ext
    page = urllib.urlopen(full_link)
    soup = BeautifulSoup(page,'html.parser')
    map_tag = map_tag_gen(full_link)
    try:    #Check to see if address is listed
        distance = google_distance_calc(home,str(map_tag))
    except:
        distance='N/A'
    if distance < float(5) or distance == 'N/A': #Else: RETURN NONE
        job_title = soup.title.string
        try:
            email = email_fetcher(soup)
        except:
            email = 'N/A'
        job_data_list = [job_title,str(distance),email,full_link]
        return job_data_list

def page_counter(soup):
    #Find total number of pages
    num_tag = soup.find("span","totalcount")
    tot_num_jobs = re.findall('[0-9]+',str(num_tag))
    if not tot_num_jobs:
        return None
    tot_num_jobs = tot_num_jobs[0]
    num_pages = int(tot_num_jobs)/100
    #Create list of page extensions
    page_ext = []
    for num in range(num_pages+1):
        if num != 0:
            page_ext.append('&s='+str(num*100))
        else:
            page_ext.append('')
    return page_ext

def job_page_gen(page_ext):
    #Creates list of job page links
    job_list_page_prefix = 'http://rochester.craigslist.org/search/jjj?employment_type=2%s'
    job_list_pages = []
    for ext in page_ext:
        job_list_pages.append(job_list_page_prefix%ext)
    return job_list_pages

def job_list_soup_gen(job_list_page):
    #Creates soup for a given job list page
    job_list_open = urllib.urlopen(job_list_page)
    soup = BeautifulSoup(job_list_open,'html.parser')
    return soup

def link_gen(soup):
    #Compile list of links
    links_soup = soup('a')
    link_ext = re.findall('href="[/]([a-z]{3}[/][0-9]+).html"',str(links_soup))
    link_ext = set(link_ext)
    return link_ext

def map_tag_gen(link):
    #Find map for calculating distance
    url = urllib.urlopen(link)
    soup = BeautifulSoup(url,'html.parser')
    map_tag = soup.find(id='map')
    return map_tag

# def distance_calc(home,map_tag):
#     #Checks if distance is within threshold
#     lat = re.findall('data-latitude="([0-9.-]+)"',str(map_tag))
#     long = re.findall('data-longitude="([0-9.-]+)"',str(map_tag))
#     dest_coord = (lat[0],long[0])
#     orig_coord = home
#     d = vincenty(orig_coord,dest_coord).miles
#     return d

def google_distance_calc(home,map_tag):
    #API Key
    service_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    key = 'AIzaSyAWitPENCuvw67RgJuCc4J203gH_x4yVis' #Browser
    lat = re.findall('data-latitude="([0-9.-]+)"',str(map_tag))
    lat = lat[0]
    long = re.findall('data-longitude="([0-9.-]+)"',str(map_tag))
    long = long[0]
    mode = 'bicycling'
    encode_dict = OrderedDict()
    encode_dict['origins'] = home
    encode_dict['destinations'] = lat+','+long
    encode_dict['mode'] = mode
    encode_dict['key'] = key
    full_url = service_url+urllib.urlencode(encode_dict)
    url_handle = urllib.urlopen(full_url)
    data = url_handle.read()
    js = json.loads(data)
    if 'status' not in js or js['status'] != 'OK':
        return None
    meters =  js['rows'][0]['elements'][0]['distance']['value']
    miles = float(meters/1609.34) #Convert meters to miles
    return miles



def email_fetcher(soup):
    #Fetches email for job
    email_link = soup.find(id='replylink')
    page_prefix = 'http://rochester.craigslist.org/reply/%s'
    page_link = re.findall('reply[/]([a-z0-9/]+)',str(email_link))
    page_link = page_link[0]
    #Opens page containing email
    email_page = urllib.urlopen(page_prefix%page_link)
    soup_email = BeautifulSoup(email_page,'html.parser')
    email_text = soup_email('div','anonemail')
    email = re.findall('">([a-zA-Z0-9-@.]+)',str(email_text[0]))
    email = email[0]
    return email

def xls_doc_gen(data):
    #Creates an excel doc from data
    workbook = xlsxwriter.Workbook('CraigslistJobData2.xlsx')
    worksheet = workbook.add_worksheet()
    titles = ['Job Title','Distance (miles)','Email','Link']
    col = 0
    for title in titles:
        worksheet.write(0,col,title)
        col += 1
    row = 1
    col = 0
    for job_title,distance,email,link in data:
        worksheet.write(row,col,job_title)
        worksheet.write(row,col+1,distance)
        worksheet.write(row,col+2,email)
        worksheet.write(row,col+3,link)
        row += 1
    workbook.close()
def blocked_error(soup):
    text = 'Blocked from Craigslist :/'
    print '* '*(len(text)/2)
    print text
    print '* '*(len(text)/2)
    print ''
    print 'Message from Craigslist:'
    print soup

"""###*************RUN SCRIPT***************###"""
job_list_1 = urllib.urlopen('http://rochester.craigslist.org/search/jjj?employment_type=2')
soup = BeautifulSoup(job_list_1,'html.parser')


#Home longitude: 43.132560
#Home latitude: -77.636223

home = '897 Genesee St, Rochester, NY'

page_ext = page_counter(soup) #Counts number of pages

if not page_ext:
    blocked_error(soup)

else:
    job_list_pages = job_page_gen(page_ext) #Creates list of web pages to access all jobs
    job_data = []
    i = 1
    for job_list_page in job_list_pages:
        #Retrieves list of jobs
        print '* * * N E W  P A G E * * *'
        print 'Retreiving data from: %s'%job_list_page
        job_list_soup = job_list_soup_gen(job_list_page)
        if not job_list_soup:
            blocked_error(job_list_soup)
            continue
        links = link_gen(job_list_soup)
        for link in links:
            data = page_scraper(link,home)
            if data: #If job meets distance criteria, add to job list
                print 'Job data:'
                print i,data
                i+=1
                job_data.append(data)
            else:
                continue
    print job_data
    file = open('CraigslistJobData.txt','w')
    file.write(str(job_data))
    file.close()
    workbook_name = 'CraigslistJobData2.xlsx'
    end_text = 'Saving to Excel file: %s...'%workbook_name
    print '* ' * (len(end_text)/2)
    print '%d jobs found.'%len(job_data)
    print end_text
    print '* ' * (len(end_text)/2)
    xls_doc_gen(job_data)
