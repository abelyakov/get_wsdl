#!/usr/bin/env python3
import sys
import re
import pycurl
from io import BytesIO

""" download file and save to byte buffer """
def get_file(url):
    print('downloading ' + url)
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer) 
    c.perform()
    c.close()
    return  buffer.getvalue()


""" extract file name from url string """
def get_file_name_from_url(url):
    last_slash = url.rfind('/')
    filename = url[last_slash + 1:]
    wsdl_ends = '?wsdl'
    #?wsdl
    if filename.endswith(wsdl_ends):
        return filename[:-5] + '.wsdl'
    xsd_param = filename.rfind('?xsd=')
    #xsd=...
    if xsd_param > 0:
        return filename[xsd_param+5:]
    wsdl_param = filename.rfind('?wsdl=')
    #wsdl=..
    if wsdl_param > 0:
        return filename[wsdl_param+6:]
    return filename


""" save downloaded file to hard disk """
def save_file(url, content):
    filename = get_file_name_from_url(url)
    with open(filename, 'w') as f:
        f.write(content)
        
    

""" 
extract additional *.xsd files 
match all inside schemaLocation=" ... " 
"""
def extract_schema_files(content):
    p = re.compile('schemaLocation="(.*?)"');
    return p.findall(content)

"""
extract additional *.xsd files from <import location="..."> tag 
"""
def extract_import_files(content):
    p = re.compile('import.location="(.*?)"');
    return p.findall(content)

""" replace remote schema locations with local names """
def replace_remote_schema_locations(content, locations):
    for url in locations:
        file_name = get_file_name_from_url(url)
        content = content.replace(url, file_name)
    return content
        
    

#script starts here
if len(sys.argv) != 2: 
    print('You must specify wsdl url!\n Usage:\n\t ' + sys.argv[0] + ' <wsdl_url>')
    sys.exit(1) 

files_to_process = set()
processed_files = set()
files_to_process.add(sys.argv[1])

while files_to_process:
    url = files_to_process.pop()
    if url in processed_files:
        continue
    content = get_file(url).decode('UTF-8')
    #get schemaLocation urls
    urls = extract_schema_files(content)
    import_urls = extract_import_files(content)
    if import_urls:
        urls.extend(import_urls)
    #replace remote locations with local file names
    content = replace_remote_schema_locations(content, urls)
    #put urls in process queue
    files_to_process.update(urls)
    #save downloaded file
    save_file(url, content)
    #add current url to processed queue
    processed_files.add(url)
    

