import requests
import urllib3
import json
import math
from termcolor import colored
from requests_toolbelt.utils import dump
class mydict(dict):
    def __str__(self):
        return json.dumps(self)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def FMC_login(FMC_ip):

    server = 'https://'+FMC_ip
    username = 'admin'#input("username: ")
    password = 'FMC_P@ssw0rd'#input("password: ")
    headers = {'Content-Type': 'application/json'}
    api_auth_path = "/api/fmc_platform/v1/auth/generatetoken"
    auth_url = server + api_auth_path
    try:
        r = requests.post(auth_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username, password), verify=False)
        auth_headers = r.headers
        auth_token = auth_headers.get('X-auth-access-token', default=None)
        refresh_token = auth_headers.get('X-auth-refresh-token', default=None)
        Domain_id = auth_headers.get('DOMAIN_UUID', default=None)
        headers['X-auth-access-token'] = auth_token
        headers['X-auth-refresh-token'] = refresh_token
        return (headers,Domain_id)
        if auth_token == None:
            print("auth_token not found. Exiting...")
            sys.exit()
    except Exception as err:
        print("Error in generating auth token --> " + str(err))
def FMC_ReadNetworkObject(FMC_ip, headers, Domain_id, file_Dir, Source_Triger):
    server = 'https://' + FMC_ip
    api_path = "/api/fmc_config/v1/domain/"+Domain_id+"/object/networkaddresses?expanded=true"  # param
    url = server + api_path
    if url[-1] == '/':
        url = url[:-1]
    r = requests.get(url, headers=headers, verify=False)
    status_code = r.status_code
    resp = r.text
    if (status_code == 200):
        print("GET successful. Response data --> ")
        json_resp = json.loads(resp)
        #print(json.dumps(json_resp, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        r.raise_for_status()
        print("Error occurred in GET --> " + resp)
    NetworkObj = json_resp
    NumOfObject = NetworkObj['paging']['count']
    print("the FMC contains", NumOfObject, "Object")

    ######################################################
    ######################################################
    N_loop = math.ceil(NumOfObject / 500)
    limit = 500
    Original_Object_list = []
    print('Reading process will take ', N_loop, ' rounds')
    ########################
    for m in range(1, N_loop + 1):
        print('round ', m)
        offset = (m - 1) * 500
        print(str(offset)+'x')

    ######################################################
    ######################################################
        api_path = "/api/fmc_config/v1/domain/" + Domain_id + "/object/networkaddresses?expanded=true&offset="+str(offset)+"&limit="+str(limit)  # param
        url = server + api_path
        if (url[-1] == '/'):
            url = url[:-1]
        r = requests.get(url, headers=headers, verify=False)
        status_code = r.status_code
        resp = r.text
        if (status_code == 200):
            print("GET successful. Response data --> ")
            json_resp = json.loads(resp)
            # print(json.dumps(json_resp, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            print(json.loads(resp))
            r.raise_for_status()
            print("Error occurred in GET --> " + resp)
        NetworkObjects_data = json_resp['items']
        FMC_Objects_Source_file = file_Dir + str(m) + ".json"
        with open(FMC_Objects_Source_file, 'w') as FMC_Objects_Source:
            json.dump(NetworkObjects_data, FMC_Objects_Source, indent=4)
            FMC_Objects_Source.write("\n")
        Original_Object_list = Original_Object_list + NetworkObjects_data
    with open ('Original_Objects.json', 'w') as f :
        json.dump(Original_Object_list, f, indent=4)
        f.write("\n")

    NO = len(Original_Object_list)
    OriginalFormList = []
    for x in range(0, NO):
        Obj_Name = Original_Object_list[x]['name']
        Obj_Value = Original_Object_list[x]['value']
        if "/" in Obj_Value:
            Obj_Type = "Network"
        elif "-" in Obj_Value:
            Obj_Type = "Range"
        else:
            Obj_Type = "Host"

        element = [{"name": Obj_Name, "value": Obj_Value, "type": Obj_Type}]
        OriginalFormList = OriginalFormList + element
    if Source_Triger == True:
        with open('OriginalFormList.json', 'w') as f:
            json.dump(OriginalFormList, f, indent=4)
            f.write("\n")
    return (OriginalFormList)
def FMC_Post_Function(FMC_ip,api_path,headers, post_data):
    url = 'https://'+FMC_ip + api_path
    if (url[-1] == '/'):
        url = url[:-1]
    for pi in range(0, len(post_data)):
        post_datai = mydict(post_data[pi])
        try:
            print(post_datai)
            r = requests.post(url, data=json.dumps(post_datai), headers=headers, verify=False)
            status_code = r.status_code
            resp = r.text
            print("Status code is: " + str(status_code))
            if status_code == 201 or status_code == 202:
                #print("Post was successful...")
                json_resp = json.loads(resp)
                #print(json.dumps(json_resp, sort_keys=True, indent=4, separators=(',', ': ')))
            else:
                r.raise_for_status()
                print("Error occurred in POST --> " + resp)
        except requests.exceptions.HTTPError as err:
            print("Error in connection --> " + str(err))
        finally:
            if r: r.close()

def FMC_Objects_Post(FMC_ip, headers, Domain_id, OriginalFormList,file_Dir,FMC_Source_Triger):
    DestinationList = FMC_ReadNetworkObject(FMC_ip, headers, Domain_id, file_Dir,FMC_Source_Triger)
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
    NetworkList = []
    HostList = []
    RangeList = []

    if OriginalFormList == []:
        print(colored('all Objects are already existed','red'))
    else:
        for ioi in range(0,len(OriginalFormList)):
            if OriginalFormList[ioi]['type'] == 'Network':
                NetworkList = NetworkList + [OriginalFormList[ioi]]
            if OriginalFormList[ioi]['type'] == 'Host':
                HostList = HostList + [OriginalFormList[ioi]]
            if OriginalFormList[ioi]['type'] == 'Range':
                RangeList = RangeList + [OriginalFormList[ioi]]
        api_path = "/api/fmc_config/v1/domain/"+Domain_id+"/object/networks"
        FMC_Post_Function(FMC_ip, api_path, headers, NetworkList)
        api_path = "/api/fmc_config/v1/domain/"+Domain_id+"/object/hosts"

        FMC_Post_Function(FMC_ip, api_path, headers, HostList)
        api_path = "/api/fmc_config/v1/domain/"+Domain_id+"/object/ranges"

        FMC_Post_Function(FMC_ip, api_path, headers, RangeList)