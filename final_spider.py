from urllib import request
import json
import csv
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# processing the netlocs and removing www / wwww / web and so on...
def netloc_processing(net):
    netloc = net
    if net.startswith('www.'):
        netloc = net[4:]
    if net.startswith('wwww.'):
        netloc = net[5:]
    if net.startswith('web.'):
        netloc = net[4:]
    return netloc

# initialized list
your_list = []
with open('nets2.csv', 'r') as f:
    reader = csv.reader(f)
    your_list = list(reader)

urllist = []
for i in your_list:
    for key in i:
        urllist.append("http://www.%s" % key)

print(urllist)
for i in urllist:
    print(i)

# clear list with netloc_processing urls (the urls of the starting list)
p_clear = []

# initialize the clear list ti p_clear
for link in urllist:
    url_parse = urlparse(link) #return 5 elements
    url_netloc = url_parse.netloc #getting the netloc ( is the second element of url parse )
    new_url = netloc_processing(url_netloc) #process the netloc to discard all the extra from the link
    p_clear.append(netloc_processing(new_url)) #append the list

#our main dictionary
p = {}

# create the dictionary with the urls loaded with http
for url in urllist:
    d = {}
    try:
        resource = request.urlopen(url, timeout=1)
        raw = resource.read().decode('utf-8')
        soup = BeautifulSoup(raw, 'lxml')
        netlocs = [] #list to appent in p['netlocs'] = [list with clear urls]
        links = soup.find_all('a')
        for link in links:
            this_link = link.get('href')
            if this_link is not None:
                this_parse = urlparse(this_link)
                if len(this_parse.netloc) > 5:
                    netlocs.append(this_parse.netloc)
                    print("parsing_netlocs of ", url, this_parse.netloc)
        # print(netlocs)
        set_netlocs = list(set(netlocs))
        # print(set_netlocs)
        new_netlocs = [netloc_processing(net) for net in set_netlocs]
        print("processed netlocs", new_netlocs)
        d['netlocs'] = new_netlocs
        d['pr'] = 1/(len(urllist))
        url_parse = urlparse(url)
        url_netloc = url_parse.netloc
        new_url = netloc_processing(url_netloc)
        d['url'] = new_url
        p[new_url] = d

    except:
        pass

# discard urls which are not in the starting set
urls_discarted = []
# discard all the links that has no relationship
try:
    for key in p.keys():
        netlocs_rel = []
        for link in p[key]['netlocs']:
            if link not in p_clear:
                urls_discarted.append(link)
                print("url discarted from ", key, "link")
            else:
                if link != p[key]['url']:
                    netlocs_rel.append(link)
        p[key]['netlocs'] = netlocs_rel
        print("discarting links not in first list ... ")
except:
    pass

for i in range(52):
    for key in p.keys():
        k = len(p[key]['netlocs'])
        try:
            for link in p[key]['netlocs']:
                p[link]['pr'] += ((p[key]['pr']) / k )
        except:
            pass
        print("calculating pagerank on")

print(p)
s = 0
for key in p.keys():
    s = p[key]['pr'] + s

for key in p.keys():
    p[key]['pr'] = (p[key]['pr']) / s
    print(p[key]['url'], " : ", p[key]['pr'])

with open('outgoing_spider2.json', 'w') as json_file:
    json.dump(p, json_file)