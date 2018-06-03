import requests
import json
import copy
import time
import os

def main():
    files = []
    files.append("https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_339187295.jpg")
    files.append("https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_2_339187295.jpg")
    files.append("https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_3_339187295.jpg")
    files.append("https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_4_339187295.jpg")
    files.append("https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_5_339187295.jpg")

    dealer = 12345

    optimizeFiles(dealer=dealer,files=files)

def optimizeFiles(dealer=0,files=None,passwrd=None,user=None,opt=0):
    url = "https://photoai.lotlinx.com"
    POST = "/images/optimize"
    OUTPUT = "./temp"
    #Make the dictionary for submitting the files
    #Can be submitted as one POST or multiple POST
    dicts = makeSubmissionDictionaries(dealer=dealer,files=files,opt=opt)

    #submit photos to the optimizer
   
    req = submitDictionaries(dicts=dicts,user='testaccount3', passwrd='bbf979ab9188',url=url+POST)
    
    #Parse token and status
    #handle error on submit
    tokens,status = checkAndParseSubmit(req)
    
    #Poll server until all jobs have finished or timeout occurs
    #Poll every X sec.  Sum up status when finished to know when to jump out
    finished = False
    inittime = time.clock()
    timeout = 60
    while finished==False and (time.clock() - inittime) < timeout:
        urls = getStatusUrl(tokens=tokens,url=url)
        jobstatus = checkOptimiseStatus(tokens=tokens,user='testaccount3', passwrd='bbf979ab9188',urls=urls)
        queued,complete,failed = countFinishedFailed(jobstatus)
        if(complete == len(jobstatus)):
            #finished with all well
            finished = True
        elif(complete+failed == len(jobstatus)):
            #finished with failures
            finished = True
        #Download those that have finished
        time.sleep(10)

    #if finished and not timed out download files    
    if(finished==True):
        urls = getDownloadUrl(tokens=tokens,url=url)
        downloadFiles(path=OUTPUT,tokens=tokens,user='testaccount3',passwrd='bbf979ab9188',urls=urls)

def downloadFiles(path="./",tokens=[],user=None,passwrd=None,urls=[]):
    for token,url in zip(tokens,urls):
        #download dicts containing file urls
        req = requests.get(url,auth=(user, passwrd))
        images = req.json()["data"][0]["vehicles"][0]["images"]
        for image in images:
            req2 = requests.get(image["modifiedUrl"], allow_redirects=True)
            try: 
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise
            open(path+"/"+image["modifiedUrl"].rsplit('/', 1)[1], 'wb').write(req2.content)
            
            
def countFinishedFailed(statuses=[]):
    queued = 0
    complete = 0
    failed = 0
    for status in statuses:
        if status == "queued":
            queued=queued+1
        elif status == "complete":
            complete=complete+1
        else:
            failed=failed+1

    return queued,complete,failed
        
def getStatusUrl(tokens=[],url=None):
    #url format <baseurl>/images/<token>/status
    urls = []
    for token in tokens:
        urls.append(url+"/images/"+token+"/status")
    return urls


def getDownloadUrl(tokens=[],url=None):
    #url format <baseurl>/images/<token>/status
    urls = []
    for token in tokens:
        urls.append(url+"/images/"+token)
    return urls

def checkOptimiseStatus(tokens=[],passwrd=None,user=None,urls=[]):
    status = []
    for token,url in zip(tokens,urls):
        req = requests.get(url,auth=(user, passwrd))
        status.append(req.json()["data"][0]["status"])
    return status

def checkAndParseSubmit(request=None):
    #check status_code = 200
    tokens = []
    status = []
    for req in request:
        if(req.status_code != 200):
            print "error!"
        else:
            if 'meta' in req.json():
                #error
                print "error"
            else:
                tokens.append(req.json()["data"][0]["token"])
                status.append(req.json()["data"][0]["status"])
                
    return tokens,status

def submitDictionaries(passwrd=None,user=None,dicts=None,url=None):
    req = []
    for sub in dicts:
        req.append(requests.post(url,json=sub,auth=(user, passwrd)))
    return req
    
def makeSubmissionDictionaries(dealer=0,files=None,opt=0):
    outputdict = []
    subdict = {
        "dealerId": dealer,
        "vehicles": [
            {"id": 0,
             "images" : []
            }
        ]
    }

    filecounter=1
    if(opt==0):
        #All files we be submitted in one go
        for idx,filename in enumerate(files):
            subdict["vehicles"][0]["images"].append({"imageId": idx,"imageUrl":filename})
        subdict["vehicles"][0]["id"]=filecounter
        outputdict.append(copy.deepcopy(subdict))
    else:
        #Files re inserted in individual submits
        for filename in files:
            subdict["vehicles"][0]["images"].append({"imageId": 0,"imageUrl":filename})
            outputdict.append(copy.deepcopy(subdict))
            #reset
            del subdict["vehicles"][0]["images"][:]

    #reset the subdict dictionary
    #set vehicles id to 0, clear list of urls
    subdict["vehicles"][0]["id"]=0
    del subdict["vehicles"][0]["images"][:]

    return outputdict;


    

if __name__=='__main__':
    main()
