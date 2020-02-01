import et as et
import requests
import xml.etree.ElementTree as et
import urllib3
import math
import json
from termcolor import colored
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def PAFW_login(PAFW_ip):
    server = 'https://'+PAFW_ip
    #username = input("username: ")
    #password = input("password: ")
    username = 'admin'
    password = 'admin'
    api_auth_path = "/api/?type=keygen&user="+username+"&password="+password
    auth_url = server + api_auth_path
    r = requests.post(auth_url, verify=False)
    resp = r.content
    root = et.fromstring(resp)
    key = root.find('result/key')
    PAFW_key = key.text
    indicator = root.attrib
    if indicator['status'] == "success":
        SyS_Exit = False
        return (PAFW_key, SyS_Exit)
    else:
        print("Error in generating auth key --> " + str(resp))
        SyS_Exit = True
        return (resp, SyS_Exit)
def PAFW_ReadNetworkObject(PAFW_ip, PAFW_key, Vsys, file_Dir,PAFW_Source_Triger):
    server = 'https://'+PAFW_ip
    api_auth_path = "/api/?type=config&action=get&xpath=/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='"+Vsys+"']/address&key="+PAFW_key
    url = server + api_auth_path
    r = requests.post(url, verify=False)
    with open(file_Dir, 'w') as f:
        f.write(r.text)
    resp = r.content
    root = et.fromstring(resp)
    OriginalFormList = []
    for entry in root.iter('entry'):
        Obj_Name = entry.attrib['name']
        if entry.find('ip-netmask')== None :
            Obj_Value =entry.find('ip-range').text
            Obj_Type = 'range'
        else:
            Obj_Type = 'Network'
            Obj_Value = entry.find('ip-netmask').text

        element = [{"name": Obj_Name, "value": Obj_Value, "type": Obj_Type}]
        OriginalFormList = OriginalFormList + element
    if PAFW_Source_Triger == True:
        with open('OriginalFormList.json', 'w') as f:
            json.dump(OriginalFormList, f, indent=4)
            f.write("\n")
    return (OriginalFormList)
        ###############################################
        ###############################################
def PAFW_Objects_Post(PAFW_ip, PAFW_key, Vsys, OriginalFormList, file_Dir,PAFW_Source_Triger):
    DestinationList = PAFW_ReadNetworkObject(PAFW_ip, PAFW_key, Vsys, file_Dir,PAFW_Source_Triger)
    ND = len(DestinationList)
    iOriginal = 0
    while iOriginal < len(OriginalFormList):
        xw = False
        for iDestination in range(0, ND):
            if OriginalFormList[iOriginal]['name'] == DestinationList[iDestination]['name']:
                del OriginalFormList[iOriginal]
                xw = True
                break
        if xw == True:
            if iOriginal > len(OriginalFormList) - 1 and len(OriginalFormList)>0:
                iOriginal = len(OriginalFormList) - 1
            else:
                iOriginal = 0
        else:
            iOriginal = iOriginal + 1
    NO = len(OriginalFormList)
    N_loop = math.ceil(NO - 1 / 500)
    PAFW_Full_form = ''
    if OriginalFormList == []:
        print(colored('all Objects are already existed','red'))
    else:
        for ii in range(0, N_loop):
            x = ii * 500
            y = (ii + 1) * 500
            if y >= NO - 1:
                y = NO - 1
            for i in range(x, y + 1):
                Obj_Name = OriginalFormList[i]['name']
                Obj_Value = OriginalFormList[i]['value']
                Obj_Type = OriginalFormList[i]['type']
                if Obj_Type == 'Range':
                    Obj_Value = "<ip-range>" + Obj_Value + "</ip-range>"
                else:
                    Obj_Value = "<ip-netmask>" + Obj_Value + "</ip-netmask>"
                PAFW_form = "<entry name=\"" + Obj_Name + "\">" + Obj_Value + "</entry>"
                PAFW_Full_form = PAFW_Full_form + PAFW_form
            # request
            server = 'https://' + PAFW_ip
            api_auth_path = "/api/?type=config&action=set&xpath=/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='" + Vsys + "']/address&key=" + PAFW_key + "&element=" + PAFW_Full_form
            url = server + api_auth_path
            r = requests.post(url, verify=False)
            print(r.text)

        with open('PAFW_Objects.xml', 'w') as f:
            f.write(PAFW_Full_form)
    return(PAFW_Full_form)


