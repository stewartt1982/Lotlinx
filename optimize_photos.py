import requests
import json
import copy

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
 
    #Make the dictionary for submitting the files
    #Can be submitted as one POST or multiple POST
    dicts = makeSubmissionDictionaries(dealer=dealer,files=files,opt=1)

    #submit photos to the optimizer
   
    req = submitDictionaries(dicts=dicts,user='testaccount3', passwrd='bbf979ab9188',url=url+POST)
    
    #Parse token and status
    #handle error on submit
    tokens,status = checkAndParseSubmit(req)

    #Poll server until all jobs have finished or timeout occurs
    #Poll every X sec.  Sum up status when finished to know when to jump out
    
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
