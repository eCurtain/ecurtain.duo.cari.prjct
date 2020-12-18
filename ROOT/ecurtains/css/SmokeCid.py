'''
Created on Aug 12, 2020

@author: Duo_Peng
'''
import Helper as helper
import requests
import Config as config
import sys
import re
import Languages as languages
import os
import Ssh as ssh
from datetime import datetime
import report as report
import HtmlTable as htmlTable
import Email as email
import logging
import CpuMem as cpumem
import chromedriver as chromedriver
import time
from decimal import Decimal
import CheckCli as checkcli



anchor_url="Stable URL"
regs_url = r"https:[^<>]*.cerence.net"
regs_asr = r"asr[:][0-9a-zA-Z-]*"
anchor_asr = "Supported cid and languages for ASR"
regs_tps =  r"tps[:][0-9a-zA-Z-]*"
anchor_tps = "Supported cid and languages for TPS"
skip_string="#asr:"
knownLanguages_asr=['eng-USA', 'deu-DEU', 'cmn-CHN', 'eng-GBR', 'fra-FRA','ita-ITA', 'spa-ESP']
jsonCids={'eng-USA':'asr-dev:smoke-eng-USA-9d917c5a-22cc-11eb-b27f-000d3a7c5f56',
          'deu-DEU':'asr-dev:smoke-deu-DEU-a4f71d06-22cc-11eb-86ec-000d3a7c5f56',
          'cmn-CHN':'asr-dev:smoke-cmn-CHN-a98c05c0-22cc-11eb-bace-000d3a7c5f56',
          'eng-GBR':'asr-dev:smoke-eng-GBR-ad39dcec-22cc-11eb-880d-000d3a7c5f56',
          'fra-FRA':'asr-dev:smoke-fra-FRA-b0959ebc-22cc-11eb-86f1-000d3a7c5f56',
          'ita-ITA':'asr-dev:smoke-ita-ITA-b4c92be8-22cc-11eb-96c0-000d3a7c5f56',
          'spa-ESP':'asr-dev:smoke-spa-ESP-c088d15e-22cc-11eb-a911-000d3a7c5f56'}
elapseThreshold_asr={"eng-USA":3.2, 'deu-DEU':3.6,'cmn-CHN':7.5, 'fra-FRA':7, 'ita-ITA':7,  'eng-GBR':7, 'spa-ESP':7, 'others':7 }
elapseThreshold_tokenize={'others':2}
elapseThreshold_format={'others':2}
badPodStatus=['Error','Pending','CrashLoopBackOff']

def getNamespaces(htmltext):
    pass

def getPage():
    passwd = helper.base64Decode(config.cerencePassword)
    url = requests.get(config.cid_page, auth=(config.cerenceUser, passwd))
    htmltext = url.text
    return htmltext

def getCid_Asr(htmltext):
   
    cids = []
    cids1, cids2 = htmlCids(htmltext, anchor_asr, regs_asr)
    return cids+cids1, cids+cids2

def getCid_Tps(htmltext):
    
    return htmlCids(htmltext, anchor_tps, regs_tps)

def getElapse(output):
    timestampstr1=output[0:20]
    timestampstr2=output[-21:-1]
    try:
        timestamp1 = Decimal(timestampstr1)* 1000
        timestamp2 = Decimal(timestampstr2)* 1000
        ms = int(timestamp2 - timestamp1)
        return ms
    except:
        return 999999
    
def htmlUrls(htmltext, type_sign):
    html_text_type_index= htmltext.index(type_sign)
    htmltext_type=htmltext[html_text_type_index:]
    index1 = htmltext_type.index(anchor_url)
    htmltext1 = htmltext_type[index1:]
    index2_text = "</tr>"
    index2 = htmltext1.index(index2_text)
    htmltext2 = htmltext1[:index2]
    index3_text = "</td>"
    index3 = htmltext2.index(index3_text)
    htmltext3 = htmltext2[:index3]
    htmltext4 = htmltext2[index3:]
    urls1 = getUrls1(htmltext3, regs_url)
    urls2 = getUrls1(htmltext4, regs_url)
    return urls1, urls2

def htmlCids(htmltext, anchor_text, regs):
    #ulogging.info(htmltext)
    
    index1 = htmltext.index(anchor_text)
    htmltext1 = htmltext[index1:]
    index2_text = "</tr>"
    index2 = htmltext1.index(index2_text)
    htmltext2 = htmltext1[:index2]
    index3_text = "</td>"
    index3 = htmltext2.index(index3_text)
    htmltext3 = htmltext2[:index3]
    htmltext4 = htmltext2[index3:]
    cids1= getCids1(htmltext3, regs)
    cids2= getCids1(htmltext4, regs)
    return  cids1, cids2;   

def getUrls1(htmltext, regs): 
    
    p = re.compile(regs)
    results = p.findall(htmltext)
    ret=[]
    for result in results:
        if not result in ret:
            ret.append(result)
    
    return  ret[0]; 
 
def getCids1(htmltext, regs): 
    
    p = re.compile(regs)
    htmltext1 = htmltext.replace(skip_string, "SKIP_CID_TO_TEST")
    results = p.findall(htmltext1)
    ret=[]
    for result in results:
        lang = languages.getLanguages(result)
        ret.append({result:lang})
    
    return  ret; 

def deployment(cid):
    cmd = "export PATH=$PATH:/home/jmeter/go/bin/; cd /var/www/html/tony/analysis/asr-config-server-tester; "
    cmd+="./deploy-request.sh "  + cid  
    hostname=config.client
    port=config.port
    username=config.username
    password=config.password
    stdout = ssh.ssh2(hostname, port, username, password, cmd)
    print(stdout)
    return stdout
    
def undeployment(cid):
    #cmd = "export PATH=$PATH:/home/jmeter/go/bin/; cd /var/www/html/tony/analysis/asr-config-server-tester; " 
    #cmd+="./undeploy-request.sh "  + cid  
    cmd = 'echo "/var/www/html/tony/analysis/asr-config-server-tester/undeploy-request.sh '+cid+'"|at -m now + 1 minute'
    hostname=config.client
    port=config.port
    username=config.username
    password=config.password
    print("undeploy:" + cid)
    ssh.ssh2(hostname, port, username, password, cmd)
    print("undeploy issued")
    #return stdout

def checkReady(cid):
    hostname=config.client
    port=config.port
    username=config.username
    password=config.password
    cmd = "nohup kubectl --context "+config.context+" -n "+config.namespace+" port-forward `kubectl --context "+config.context+" -n "+config.namespace+" get pods |grep proxy|head -1|cut -d ' ' -f 1` 5555 > nohup.out 2> nohup.err < /dev/null &"
    ssh.ssh2(hostname, port, username, password, cmd) 
    cmd ="curl --basic -u dataplaneapi:changeit http://127.0.0.1:5555/v2/services/haproxy/configuration/raw | jq -r .data" 
   
    stdout = ssh.ssh2(hostname, port, username, password, cmd, ignore_error=True)
    str_out= stdout.decode("utf-8") 
    #print(str_out)
    reg=r'[A-Fa-f0-9]{80,}'
    list_hex = re.findall(reg, str_out)
    print(list_hex)
    for hex_str in list_hex:
        cid1 = bytes.fromhex(hex_str).decode("ASCII")
        print("CID:"+cid1)
        if(cid == cid1):
            print("ready")
            return True
    
    return False

def checkElapse(elapse, elapseThreshold_asr, language):
    if(language in elapseThreshold_asr):
        return elapse-elapseThreshold_asr.get(language)*1000
    else:
        return elapse-elapseThreshold_asr.get("others")*1000

def checkAsrResult(language, str_out):
    if(language=='eng-USA'):
        if('Costco' in str_out):
            return "PASS"
        else:
            return "FAIL"
            #return "PASS*")
    elif(language=='deu-DEU'):
        if('"an"' in str_out and '"Martha"' in str_out):
            return "PASS"
        else:
            return "FAIL"
            #return "PASS*")
    elif(language=='cmn-CHN'):
        if('bo1_fang4' in str_out):
            return "PASS"
        else:
            return "FAIL"
            #return "PASS*")
    elif(language=='eng-GBR'):
        if('Spotify' in str_out):
            return "PASS"
        else:
            return "FAIL"
    elif(language=='fra-FRA'):
        if('ailleurs' in str_out):
            return "PASS"
        else:
            return "FAIL" 
    elif(language=='ita-ITA'):
        if('canzone' in str_out):
            return "PASS"
        else:
            return "FAIL"   
    elif(language=='spa-ESP'):
        if('Perfect' in str_out):
            return "PASS"
        else:
            return "FAIL"              
            
    else:
        return 'PASS'+":new Language"

def runTest_dev(namespace, jsonCids, url):
    allGood = True
    results = []
    readyStatus = False
    for key in jsonCids:
        cid = jsonCids[key]
        language=key
        deployment(cid)
        time.sleep(30)
        for unused in range(50):
            if checkReady(cid):
                readyStatus = True
                time.sleep(60)
                break
            else:
                print('Not Ready')
                #deployment(cid)
                time.sleep(10)
                
        cwd = "/var/www/html/MonitorAsr" #os.getcwd()
        command = "date +%s.%N;"
        command += "cd "+cwd+"/cars-server-grpc-testers;"
        command +="sed 's/{{CID}}/"+cid+"/' pcmStreamingConfig.json >pcmStreamingConfigReplaced.json;"
       
        if(language in knownLanguages_asr):
            command +='sh grpcurl-stream.sh '+url+' 443 '+language+'.opus'
        else:
            command +='sh grpcurl-stream.sh '+url+' 443 eng-USA.opus'
        #command +='sh grpcurl-stream.sh '+url+' 443 '+language+'.opus'
        command+=";date +%s.%N"
        hostname=config.client
        port=config.port
        username=config.username
        password=config.password
        
        stdout = ssh.ssh2(hostname, port, username, password, command)
        time.sleep(10)
        print("again")
        stdout = ssh.ssh2(hostname, port, username, password, command)
        print("again")
        start = time.time()
        stdout = ssh.ssh2(hostname, port, username, password, command)
        end = time.time()
        str_out= stdout.decode("utf-8") 
        elapse = getElapse(str_out)
        #logging.info(stdout)
        result=[]
        result.append(namespace)
        result.append("ASR")
        result.append(url)
        if(readyStatus):
            result.append(cid)
        else:
            result.append("NOT READY:"+cid)
        result.append(language)
        sessionId=helper.getString(str_out, 'cerence-session-id:', ' ')
        
        elaspeDiff = checkElapse(elapse, elapseThreshold_asr, language)
        if(elaspeDiff<0 or elapse==999999):
            if('finalAlternatives' in str_out):
                resultPassFail = checkAsrResult(language, str_out)
                if(elapse==999999 or resultPassFail=='FAIL'):
                    allGood = False
                result.append(resultPassFail)
                results.append(result)
                result.append(elapse)
                result.append(sessionId)
                
            else:
                result.append("FAIL")
                allGood = False
                results.append(result)
                result.append(elapse)
                result.append(sessionId+":"+str_out)
            
        else:
            resultPassFail = checkAsrResult(language, str_out)
            if(resultPassFail=='FAIL'):
                result.append("FAIL")
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL AND FAILED:"+sessionId+":"+str_out)
                allGood=False
            else:
                result.append("PASS")
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL:"+sessionId)
                
            
        
        undeployment(cid)
        #for unused in range(100):
        #    if not checkReady(cid):
        #        break
        #    else:
        #        time.sleep(5)
        
    return results, allGood

def runTest(namespace, listCid, url):
    allGood = True
    
    results = []
    for cidItem in listCid:
        cid = list(cidItem)[0]
        language=cidItem.get(cid)
        cwd = "/var/www/html/MonitorAsr" #os.getcwd()
        
        command = "date +%s.%N;"
        command+="cd "+cwd+"/cars-server-grpc-testers;"
        command+="sed 's/{{CID}}/"+cid+"/' pcmStreamingConfig.json >pcmStreamingConfigReplaced.json;"
        
        if(language in knownLanguages_asr):
            command +='sh grpcurl-stream.sh '+url+' 443 '+language+'.opus'
        else:
            command +='sh grpcurl-stream.sh '+url+' 443 eng-USA.opus'
        command+=";date +%s.%N"
        hostname=config.client
        port=config.port
        username=config.username
        password=config.password
        start = time.time()
        stdout = ssh.ssh2(hostname, port, username, password, command)
        end = time.time()
        str_out= stdout.decode("utf-8") 
        elapse = getElapse(str_out)
        #logging.info(stdout)
        result=[]
        result.append(namespace)
        result.append("ASR")
        result.append(url)
        result.append(cid)
        result.append(language)
        sessionId=helper.getString(str_out, 'cerence-session-id:', ' ')
        elaspeDiff = checkElapse(elapse, elapseThreshold_asr, language)
        if(elaspeDiff<0 or elapse==999999):
            if('finalAlternatives' in str_out):
                resultPassFail = checkAsrResult(language, str_out)
                if(elapse==999999 or resultPassFail=='FAIL'):
                    allGood = False
                result.append(resultPassFail)
                
            else:
                result.append("FAIL")
                allGood = False
            results.append(result)
            result.append(elapse)
            result.append(sessionId)
        else:
            resultPassFail = checkAsrResult(language, str_out)
            if(resultPassFail=='FAIL'):
                result.append("FAIL")
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL AND FAILED:"+sessionId)
            else:
                result.append("FAIL")
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL:"+sessionId)
            allGood=False
    return results, allGood

def checkTps(language, str_out, expect):
    if(expect in str_out):
        return "PASS"
    else:
        return "FAIL"

def runTestTokenize(namespace, listCid, url):
    allGood = True
    results = []
    for cidItem in listCid:
        cid = list(cidItem)[0]
        language=cidItem.get(cid)
        cwd = "/var/www/html/MonitorAsr" #os.getcwd()
        command = "date +%s.%N;"
        command += "cd "+cwd+"/cars-server-grpc-testers;"
        command +="sed 's/{{CID}}/"+cid+"/' Tokenize.sentence01.json >Tokenize.sentence01ConfigReplaced.json;"
        command +='sh grpcurl-tokenize.sh '+url+' 443 '
        command += ";date +%s.%N;"
        hostname=config.client
        port=config.port
        username=config.username
        password=config.password
        start = time.time()
        stdout = ssh.ssh2(hostname, port, username, password, command)
        logging.info(stdout)
        end = time.time()
        str_out= stdout.decode("utf-8") 
        elapse = getElapse(str_out)
        result=[]
        result.append(namespace)
        result.append("Tokenize")
        result.append(url)
        result.append(cid)
        result.append(language)
        sessionId=helper.getString(str_out, 'cerence-session-id:', ' ')
        elaspeDiff = checkElapse(elapse, elapseThreshold_tokenize, language)
        if(elaspeDiff<0 or elapse==999999):
            resultPassFail =  checkTps(language, str_out, 'tokens' )
            if(elapse==999999 or resultPassFail=='FAIL'):
                allGood = False
            result.append(resultPassFail)    
            results.append(result)
            result.append(elapse)
            result.append(sessionId)
        else:
            resultPassFail =  checkTps(language, str_out, 'tokens' )
            if(resultPassFail=='FAIL'):
                result.append("FAIL")
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL AND FAILED:"+sessionId)
                allGood=False
            else:
                if 'dev' in namespace:
                    result.append("PASS")
                    
                else:
                    result.append("FAIL")
                    allGood=False
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL:"+sessionId)
                
    return results, allGood

def runTestFormat(namespace, listCid, url):
    allGood = True
    results = []
    for cidItem in listCid:
        cid = list(cidItem)[0]
        language=cidItem.get(cid)
        cwd = "/var/www/html/MonitorAsr" #os.getcwd()
        command = "date +%s.%N;"
        command += "cd "+cwd+"/cars-server-grpc-testers;"
        command +="sed 's/{{CID}}/"+cid+"/' Format.sentence01.json >Format.sentence01ConfigReplacedMid.json;"
        if(language=='eng-USA'):
            command+="sed 's/{{CONTENT}}/One/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;"
        elif (language=='deu-DEU'):
            command+="sed 's/{{CONTENT}}/Einer/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;"
        elif (language=='cmn-CHN'): 
            command+="sed 's/{{CONTENT}}/一/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;"
        elif (language=='eng-GBR'):
            command+="sed 's/{{CONTENT}}/One/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;"   
        elif (language=='fra-FRA'): 
            command+="sed 's/{{CONTENT}}/Un/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;" 
        elif (language=='ita-ITA'): 
            command+="sed 's/{{CONTENT}}/Una/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;" 
        elif (language=='spa-ESP'): 
            command+="sed 's/{{CONTENT}}/Una/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;" 
        else:
            command+="sed 's/{{CONTENT}}/1/' Format.sentence01ConfigReplacedMid.json >Format.sentence01ConfigReplaced.json;" 
        command +='sh grpcurl-format.sh '+url+' 443 '
        command += ";date +%s.%N;"
        hostname=config.client
        port=config.port
        username=config.username
        password=config.password
        start = time.time()
        stdout = ssh.ssh2(hostname, port, username, password, command)
        logging.info(stdout)
        end = time.time()
        str_out= stdout.decode("utf-8") 
        elapse = getElapse(str_out)
        result=[]
        result.append(namespace)
        result.append("Format")
        result.append(url)
        result.append(cid)
        result.append(language)
        sessionId=helper.getString(str_out, 'cerence-session-id:', ' ')
        elaspeDiff = checkElapse(elapse, elapseThreshold_format, language)
        if(elaspeDiff<0 or elapse==999999):
            resultPassFail =  checkTps(language, str_out, 'formatWords' )
            if(elapse==999999 or resultPassFail=='FAIL'):
                allGood = False
            result.append(resultPassFail)
            results.append(result)
            result.append(elapse)
            result.append(sessionId)
        else:
            resultPassFail =  checkTps(language, str_out, 'formatWords' )
            if(resultPassFail=='FAIL'):
                result.append('FAIL')
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL AND FAILED:"+sessionId)
                allGood=False
            else:
                if 'dev' in namespace:
                    result.append("PASS")
                else:
                    result.append("FAIL")
                    allGood=False
                    
                results.append(result)
                result.append(elapse)
                result.append("HIGH CPL:"+sessionId)
            
            
    return results, allGood

def titlesResults():
    titleList = ["namespace","Function", "URL","CID", "Language", "PASS?", "Elapse", "SessionId"]
    formats = [  "str", "str", "str",    "str",      "str",     "str", "decimal,0,ms", "str"]
    return titleList, formats

def checkContainerStatus(html):
    for status in badPodStatus:
        if status in html:
            return True
    return False
        
def replacePodStatus(html):
    for status in badPodStatus:
        if status in html:
            html=helper.color('red', html, status)
    return html

def sendReport(resultList, allGood, testtype):
    if allGood:
        title = "ALL PASSED:"
    else:
        title = "SOMETHING WRONG:"
    if(testtype=="day"):
        title +="Everyday smoke test of CID for namespace: "
        title += config.cid_namespaces_asr[0]+","+config.cid_namespaces_asr[1]+","+config.cid_namespaces_tps[0]+" and "+config.cid_namespaces_tps[1]
    else:
        title +="Everyhour smoke test of CID for namespace: "
        title += config.cid_namespaces_asr[1]+","+config.cid_namespaces_tps[0]+" and "+config.cid_namespaces_tps[1]
        
    #title += config.cid_namespaces_asr[0]+","+config.cid_namespaces_asr[1]+","+config.cid_namespaces_tps[0]+" and "+config.cid_namespaces_tps[1]
    #title += config.cid_namespaces_asr[1]+","+config.cid_namespaces_tps[0]+" and "+config.cid_namespaces_tps[1]
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")
    html = report.formatTextH3("timestamp: "+helper.getLocalTime(timestampStr)+"&nbsp;&nbsp;&nbsp;"+"context:"+config.context);
    
    titleList, formats =titlesResults();
    html2 = htmlTable.table(titleList, formats, resultList, "cid smoke test results")
    html+="<br/><br/>"
    html+=html2
    html+="<br/><br/>"
    #html+= PodStatus(config.cid_namespaces_asr[0],config.cid_namespaces_asr[1])
    if(testtype=="day"):
        html+= PodStatus(config.cid_namespaces_asr[0],config.cid_namespaces_asr[1])
    else:
        html+= PodStatus(config.cid_namespaces_asr[1],None)
    
    html+="<br/><br/>"
    if(testtype=="day"):
        caption = "CPU Memory of namespace: "+config.cid_namespaces_asr[0]
        html1, pods_asr1=cpuMem(config.cid_namespaces_asr[0], caption)
        html+=html1
        
    caption = "CPU Memory of namespace: "+config.cid_namespaces_asr[1]
    html1, pods_asr1=cpuMem(config.cid_namespaces_asr[1], caption)
    html+=html1
    
    html+="<br/>"
    
    html+="<br/><br/>"
    if(testtype=="day"):
        html+= PodStatus(config.cid_namespaces_tps[0],config.cid_namespaces_tps[1])
    else:
        html+= PodStatus(config.cid_namespaces_tps[1],None)   
    
    html+="<br/>"
    if(testtype=="day"):
        caption = "CPU Memory of namespace: "+config.cid_namespaces_tps[0];
        html1, pods_tps1=cpuMem(config.cid_namespaces_tps[0], caption)
        html+=html1
    
    html+="<br/>"
    caption = "CPU Memory of namespace: "+config.cid_namespaces_tps[1];
    html2, pods_tps2 =cpuMem(config.cid_namespaces_tps[1], caption)
    html+=html2
    
    attached_files=[]
    
    if checkContainerStatus(html):
        allGood = False
        title="pod status is wrong;"+title
        html=replacePodStatus(html)
        
    if(testtype=="day"):
        
        '''indexImg=0
        run_id='0000'
        podFilenames = granfanaImages(run_id, config.cid_namespaces_asr[1], pods_asr1)
        html3, indexImg, attached_files = tableGranfana(run_id, podFilenames, indexImg, attached_files)
        if(len(attached_files)>1):
            html+="<br/><br/>"
            html+=report.formatTextH3("Grafana images of namespace: "+config.cid_namespaces_asr[1]);
            
            html+=html3
            
            #podFilenames = granfanaImages(run_id,config.cid_namespaces_asr[1],pods_asr2)
            #html4, indexImg, attached_files = tableGranfana(run_id, podFilenames, indexImg, attached_files)
            #html+="<br/>"
            #html+=report.formatTextH3("Grafana images of namespace: "+config.cid_namespaces_asr[1]);
            #html+=html4
        '''
        receivers = config.cid_email_receivers
        print(html)
        email.sendHtmlEmailReceivers(title, html, attached_files, receivers)
    else:
        if(allGood):
            receivers = config.cid_email_receivers_passed
        else:
            receivers = config.cid_email_receivers
        email.sendHtmlEmailReceivers(title, html, attached_files, receivers)
    
    for filename in attached_files:
        os.remove(filename)
    
    print(html)    
    return html

#def printinfo(*objects, sep=' ', end='\n', file=sys.stdout):
#    enc = file.encoding
#    if enc == 'UTF-8':
#        logging.info(*objects, sep=sep, end=end, file=file)
#    else:
#        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
#        logging.info(*map(f, objects), sep=sep, end=end, file=file)

def granfanaImages(run_id, namespace, pods):
    filenames = []
    
    for pod in pods:
        try:
            podname = helper.getFirstWord(pod)
            for prefix in config.grafana_pods:
                if(podname.startswith(prefix)):
                    filename = chromedriver.graph_pods2(run_id, config.grafana_local_port, podname, 1440, 1024, 24, namespace, timeout=1000)
                    filenames.append(filename)
                    logging.info(filename)
                    break
        except:
            continue
    return filenames

def tableGranfana(run_id, podFilenames, indexImg, attached_files):
    html="<table>"
    podHtml=""
    podImgHtml =""
    i=0
    for podFilename in podFilenames:
        if(int(i/2)*2 == i):
            if(i==0):
                podHtml+="<tr>"
                podImgHtml +="<tr>"
            else:
                podHtml+="</tr>"
                podImgHtml +="</tr>"
                html+=podHtml
                html+=podImgHtml
                podHtml="<tr>"
                podImgHtml="<tr>"
        podHtml+="<td>" 
        podHtml+=podFilename.replace("snapshot/","").replace(".png","").replace(run_id+"_","")
        podHtml+="</td>\n"
        
        podImgHtml+="<td>"
        podImgHtml+="<img src='cid:img"+str(indexImg)+"' alt='img' width='720' height='512' />"
        podImgHtml+="</td>\n"
        
        indexImg+=1
        i+=1
        attached_files.append(podFilename)
    podHtml+="</tr>"
    podImgHtml +="</tr>"
    html+=podHtml
    html+=podImgHtml
    html+="</table>"    
    return html, indexImg, attached_files
   
    
def smoke(testtype="hour"):
    #try:
    htmltext = getPage()
    #urls1, urls2 = htmlUrls(htmltext)
    urls_asr_1, urls_asr_2 = htmlUrls(htmltext, config.cid_namespaces_asr[0])
    #urls_asr_2 = "asr.stable.na.onecloud.hosting.cerence.net"
    urls_tps_1, urls_tps_2 = htmlUrls(htmltext, config.cid_namespaces_tps[0])
    #urls_tps_2 = "tps.stable.na.onecloud.hosting.cerence.net"
    s1, s2 = getCid_Asr(htmltext)
    ts1, ts2 = getCid_Tps(htmltext)
    #logging.info(s1)
    #logging.info(s2)
    #to do : tps-dev cid test
    
    logging.info(urls_asr_1+";"+urls_asr_2)
    logging.info(urls_tps_1+";"+urls_tps_2)
    if(testtype=="day"):
        results1, allGood1 = runTest_dev(config.cid_namespaces_asr[0], jsonCids, urls_asr_1.replace("https://",""))
        #results3, allGood3 = runTestTokenize(config.cid_namespaces_tps[0], ts1, urls_tps_1.replace("https://",""))
        #results5, allGood5 = runTestFormat(config.cid_namespaces_tps[0], ts1, urls_tps_1.replace("https://",""))
    results2, allGood2 = runTest(config.cid_namespaces_asr[1], s2, urls_asr_2.replace("https://",""))
    urls_asr_2_1 = "asr.stable.na.onecloud.hosting.cerence.net"
    namespace_asr_2_1 = "stable-1-ASR"
    results2_1, allGood2_1 = runTest(namespace_asr_2_1, s2, urls_asr_2_1)
    results4, allGood4 = runTestTokenize(config.cid_namespaces_tps[1], ts2, urls_tps_2.replace("https://",""))
    results6, allGood6 = runTestFormat(config.cid_namespaces_tps[1], ts2, urls_tps_2.replace("https://",""))
    urls_tps_2_1 = "tps.stable.na.onecloud.hosting.cerence.net"
    namespace_tps_2_1 = "stable-1-TPS"
    results4_1, allGood4_1 = runTestTokenize(namespace_tps_2_1, ts2, urls_tps_2_1)
    results6_1, allGood6_1 = runTestFormat(namespace_tps_2_1, ts2, urls_tps_2_1)
    if(testtype=="day"):
        #if(allGood1 & allGood2 & allGood3 & allGood4 & allGood5 & allGood6):
        if(allGood1 & allGood2 &  allGood4 &  allGood6 & allGood2_1 &  allGood4_1 & allGood6_1):
            allGood = True
        else:
            allGood = False
            
        #results= results1+results2+results3+results4+results5+results6
        results= results2_1+results4_1+results6_1 + results1+results2+results4+results6
    else:
        #if(allGood2 &  allGood4 & allGood6):
        if(allGood2 &  allGood4 & allGood6 & allGood2_1 &  allGood4_1 & allGood6_1):
            allGood = True
        else:
            allGood = False
        #results= results2+results4+results6
        results= results2_1+results4_1+results6_1 + results2+results4+results6
    #results= results1+results2+results3+results4+results5+results6
    #results= results2+results3+results4+results5+results6
    
    sendReport(results, allGood, testtype)
    #except:
    #    receivers = config.cid_email_receivers_passed
    #    email.sendHtmlEmailReceivers("script is broken out, please check", str(sys.exc_info()[0]),[], receivers)
    
    checkcli.test()
     
def PodStatus(namespace1, namespace2):
    html="<table>"
    html+="<caption>Pod Status</caption>\n"
    html+="<tr><td>"
    namespace=namespace1
    html+=namespace+"</td>"
    if namespace2!=None:
        html+="<td>"
        html+=namespace2+"</td>"
    pods1 = helper.getPodStatus2(namespace)
    html+="<tr><td>"
    s1=pods1.decode("utf-8").replace("\n","<br/>")+"</td>"
    html+=replaceStatus(s1)
    if namespace2!=None:
        #html+="<td>"
        namespace=namespace2
        
        pods2 = helper.getPodStatus2(namespace)
        html+="<td>"
        s2=pods2.decode("utf-8").replace("\n","<br/>")+"</td></tr>\n"
        html+=replaceStatus(s2)
    html+="</table>"
    return html

def cpuMem(namespace, caption):
    titles = ["POD","Container", "Resources"]
    formats = ["str","str",  "str"]
    listCpuMem = []
    pods = helper.getPodStatus(namespace)
    
    for pod in pods:
        if(pod.startswith("NAME READY STATUS RESTARTS AGE")):
            continue
        values = pod.split(" ")
        if(len(values)<5):
            continue
        podname=values[0]
        
        #for prefix in config.grafana_pods:
        #    if(podname.startswith(prefix)):
        cpuMemInfo = cpumem.containerCpuMem(namespace, podname)
        listCpuMem+=cpuMemInfo
    result = htmlTable.table(titles, formats, listCpuMem, caption)
    return result, pods

def replaceStatus(html):
    html = helper.color("green", html, "Running")
    html = helper.color("green", html, " Completed ")
    html = helper.color("red", html, "Crashed")
    return html

def getHourStr():
    dateTimeObj = datetime.now()
    hourStr = dateTimeObj.strftime("%H")
    return hourStr
   
if __name__ == '__main__':  
    logging.basicConfig(filename='smokeCid.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
    hourStr = getHourStr()
    if(len(sys.argv)==0):
        if(int(hourStr)==8):
            smoke("day")
        else:
            smoke("hour")
    else:
        typeTest=sys.argv[0]
        if(typeTest=='day'):
            smoke("day")
        else:
            smoke("hour")
        #smoke("day")
        
# crontab -e
# 5 * * * * /root/checkCid.sh>/dev/null 2>&1