try:
    import requests
except:
    print "module: \"requests\" not found\nPlease install module\nInstructions for installation at http://docs.python-requests.org/en/master/user/install/"
import json
import copy
import time
import os
import sys
import pprint

def optimizeFiles(dealer=1,files=None,passwrd=None,user=None,path="./",opt=0,timeout=100,logfile=None):
    URL = "https://photoai.lotlinx.com"
    POST = "/images/optimize"
    
    #Make the dictionary for submitting the files
    #Can be submitted as one POST or multiple POST
    dicts = makeSubmissionDictionaries(dealer=dealer,files=files,opt=opt)
    
    #submit photos to the optimizer
    if logfile is not None:
        logfile.write("Submitting URLs to the PhotoAI optimizer\n\n")
        for url in files:
            logfile.write(url+"\n")
            
    req = submitDictionaries(dicts=dicts,user=user, passwrd=passwrd,url=URL+POST,logfile=logfile)
    
    #Parse token and status
    #handle error on submit
    tokens,status = checkAndParseSubmit(req)
    
    #Poll server until all jobs have finished or timeout occurs
    #Poll every X sec.  Sum up status when finished to know when to jump out
    finished = False
    inittime = time.time()
    queued=0
    complete=0
    failed=0

    if logfile is not None:
        logfile.write("Polling PhotoAI for statuses to check when submission is finished\n\n")
        
    while finished==False and (time.time() - inittime) < timeout:
        if logfile is not None:
            logfile.write("Polling...\n")
        urls = getStatusUrl(tokens=tokens,url=URL)
        jobstatus = checkOptimiseStatus(tokens=tokens,user=user, passwrd=passwrd,urls=urls,logfile=logfile)
        queued,complete,failed = countFinishedFailed(jobstatus)
        if(complete == len(jobstatus)):
            #finished with all well
            finished = True
        elif(complete+failed == len(jobstatus)):
            #finished with failures
            finished = True
        #Download those that have finished
        time.sleep(10)
    if logfile is not None:
        logfile.write("Finished processing file or timeout\n\n")
        logfile.write(str(complete)+" Submissions completed "+str(queued)+" Submissions remained queued "+str(failed)+" Submissions failed\n\n")
    #if finished and not timed out download files    
    if(finished==True):
        urls = getDownloadUrl(tokens=tokens,url=URL)
        numfiles = downloadFiles(path=path,tokens=tokens,user=user,passwrd=passwrd,urls=urls,logfile=logfile)
        if logfile is not None:
            logfile.write("Retrieved "+str(numfiles)+" of "+str(len(files)))
    else:
        #Timed out
        print "ERROR: File retrieval timed out. Re-submit with longer timeout"
    
def downloadFiles(path="./",tokens=[],user=None,passwrd=None,urls=[],logfile=None):
    #count the number of downloaded files
    count=0
    for token,url in zip(tokens,urls):
        #download dicts containing file urls
        try:
            req = requests.get(url,auth=(user, passwrd))
            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print "ERROR: ",e
            sys.exit(1)
        except requests.exceptions.Timeout:
            print "ERROR: Timeout on attempt to get load response\n"
        except requests.exceptions.TooManyRedirects:
            print "ERROR: Too many re-directs\n"
        except requests.exceptions.RequestException as e:
            print e
            sys.exit(1)

        if logfile is not None:
            logfile.write("Response for token "+token+" using URL "+url+"\n\n")
            pprint.pprint(req.json(),logfile)
            logfile.write("\n\n")
        images = req.json()["data"][0]["vehicles"][0]["images"]
        #Download images
        
        for image in images:
            if logfile is not None:
                logfile.write("Downloading image from URL "+image["modifiedUrl"]+"\n to "+path+"\n")
            try:
                req2 = requests.get(image["modifiedUrl"], allow_redirects=True)
                req2.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print "ERROR: ",e
                sys.exit(1)
            except requests.exceptions.Timeout:
                print "ERROR: Timeout on attempt to download file\n"
            except requests.exceptions.TooManyRedirects:
                print "ERROR: Too many re-directs\n"
            except requests.exceptions.RequestException as e:
                print e
                sys.exit(1)
                
            #Try to make directory, if exists and is a directory continue
            try: 
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise
            try:
                open(path+"/"+image["modifiedUrl"].rsplit('/', 1)[1], 'wb').write(req2.content)
                count = count + 1
            except IOError as e:
                print "ERROR: While writing file ",image["modifiedUrl"].rsplit('/', 1)[1],e
        return count
    
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

def checkOptimiseStatus(tokens=[],passwrd=None,user=None,urls=[],logfile=None):
    status = []
    for token,url in zip(tokens,urls):
        if logfile is not None:
            logfile.write("Checking status of submissions to PhotoAI\n\n")
        try:
            req = requests.get(url,auth=(user, passwrd))
            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print "ERROR: ",e
            sys.exit(1)
        except requests.exceptions.Timeout:
            print "ERROR: Timeout on attempt to get check status\n"
        except requests.exceptions.TooManyRedirects:
            print "ERROR: Too many re-directs\n"
        except requests.exceptions.RequestException as e:
            print e
            sys.exit(1)
        if logfile is not None:
            logfile.write("Response for token "+token+" using URL "+url+"\n\n")
            pprint.pprint(req.json(),logfile)
            logfile.write("\n")
        
        status.append(req.json()["data"][0]["status"])
    return status

def checkAndParseSubmit(request=None):
    #check status_code = 200
    tokens = []
    status = []
    for req in request:
        if(req.status_code != 200):
            print "ERROR: on submission of file\n"
            print req.text
        else:
            if 'meta' in req.json():
                #error
                print "ERROR: ",req.json()["meta"]["errorMsg"]
            else:
                tokens.append(req.json()["data"][0]["token"])
                status.append(req.json()["data"][0]["status"])
                
    return tokens,status

def submitDictionaries(passwrd=None,user=None,dicts=None,url=None,logfile=None):
    request = []
    for sub in dicts:
        if logfile is not None:
            logfile.write("Submiting to PhotoAI (POST)\n\n")
            pprint.pprint(sub,logfile)
            logfile.write("\n")
        try:
            req = requests.post(url,json=sub,auth=(user, passwrd))
            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print "ERROR: ",e
            sys.exit(1)
        except requests.exceptions.Timeout:
            print "ERROR: Timeout on attempt to submit request\n"
        except requests.exceptions.TooManyRedirects:
            print "ERROR: Too many re-directs\n"
        except requests.exceptions.RequestException as e:
            print e
            sys.exit(1)

        if logfile is not None:
            logfile.write("Response from PhotoAI upon POST\n\n")
            pprint.pprint(req.json(),logfile)
            logfile.write("\n")
        request.append(req)
    return request
    
def makeSubmissionDictionaries(dealer=1,files=None,opt=0):
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

