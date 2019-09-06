def urls_reader():
    with open ('url_list.csv', 'r') as infile:
        urls = infile.readlines()
        del urls[0]
      
        clean = [url.strip() for url in urls]
        return clean


        