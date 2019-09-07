## Steps to test the code 
**Clone this repo:** `git clone https://github.com/TheSteelGuy/data_engineering-.git`

**change directory to data_engineering-**
## $python3 main_file.py
# url_read.py
```def urls_reader():
    with open ('url_list.csv', 'r') as infile:
        urls = infile.readlines()
        del urls[0]
      
        clean = [url.strip() for url in urls]
        return clean
```
## For Testing purpose since the code is running a single instance you may have
## the function above returning an array of say 20 repos as such

```def urls_reader():
    with open ('url_list.csv', 'r') as infile:
        urls = infile.readlines()
        del urls[0]
      
        clean = [url.strip() for url in urls]
        return clean[:20]
```

