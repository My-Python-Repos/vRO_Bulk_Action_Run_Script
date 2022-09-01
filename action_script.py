#=========================================================================================================
#
#   NAME        :      action_script.py
#
#   DESC        :      To run any vRA Action on multiple VMs
#
#   DESCRIPITON :      vRA Action Run
#
#   AUTHOR      :      Praveen Beniwal
#
#   EMAIL ID    :      praveen1664@outlook.com
#                      
#
#   HISTORY     :      04-05-2020
#
#
#   version     :  1.0
#
#=========================================================================================================

from menu import *

class flushfile:
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()


@contextmanager
def custom_redirection(fileobj):
    old = sys.stdout
    sys.stdout = fileobj
    sys.stdout = flushfile(sys.stdout)
    try:
        yield fileobj
    finally:
        sys.stdout = old

def resource_id(vMName,vrafqdn,vraheaders):
    vraApiurl = "https://{}/catalog-service/api/consumer/resources/?%24filter=name+eq+'{}'".format(vrafqdn,vMName)
    req= requests.request("GET",vraApiurl,headers=vraheaders, verify=False).json()['content']
    #print(json.dumps(req, indent=4))
    if len(req) != 0:
        for i in req:
            if i['resourceTypeRef']['id'] == 'Infrastructure.Virtual':
                if i['name']== vMName:
                    resid=i['id']
                    x = i["parentResourceRef"]
                    reqid = x['id']
                    owner= i['owners'][0]['value']
                    return vMName,resid,reqid,owner,'exist'
    else:
        return vMName,'NA','NA','NA','not_exist'


def template(actionid,resid,vrafqdn,vraheaders):
    vraResUrl = "https://{}/catalog-service/api/consumer/resources/{}/actions/{}/requests/template".format(vrafqdn,resid,actionid)
    resreq = requests.request("GET", vraResUrl, headers=vraheaders, verify=False).json()
    return resreq


def Machine_Action(payload,actionid,resid,vrafqdn,vraheaders,machine):
    vraResUrl = "https://{}/catalog-service/api/consumer/resources/{}/actions/{}/requests".format(vrafqdn,resid,actionid)
   # resreq = requests.request("POST", vraResUrl,json=payload,headers=vraheaders, verify=False)
    resreq = requests.post(vraResUrl,json=payload,headers=vraheaders, verify=False)
    y=resreq.headers['location']
    #print resreq
    if resreq.status_code == 201:
          print 60 * " "
          print 60 * " "
          print bcolors.OKGREEN + ("Action succesfully triggered on ") + machine +bcolors.ENDC
          print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
          return 'Passed',y
    else:
          print 60 * " "
          print 60 * " "
          print bcolors.WARNING + ("Please check the error on ") + machine + bcolors.ENDC
          print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
          return 'Failed','NA'


def Shared_Access(payload,actionid,resid,vrafqdn,vraheaders,group,machine):
     payload["data"]["provider-groupName"] = "{}".format(group);
     vraResUrl = "https://{}/catalog-service/api/consumer/resources/{}/actions/{}/requests".format(vrafqdn,resid,actionid)
     #resreq = requests.request("POST", vraResUrl,json=payload,headers=vraheaders, verify=False)
     resreq = requests.post(vraResUrl,json=payload,headers=vraheaders, verify=False)
     y=resreq.headers['location']
     #print(json.dumps(req, indent=4))
     if resreq.status_code == 201:
          print 60 * " "
          print 60 * " "
          print bcolors.OKGREEN + ("Action succesfully triggered on ") + machine +bcolors.ENDC
          print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
          return 'Passed',y
      
     else:
          print 60 * " "
          print 60 * " "
          print bcolors.WARNING + ("Please check the error on ") + machine + bcolors.ENDC
          print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
          return 'Failed','NA'
   
def Change_owner(payload,actionid,resid,vrafqdn,vraheaders,new_owner,machine):
     payload["data"]["provider-NewOwner"] = "{}".format(str(new_owner));
    # print payload
     vraResUrl = "https://{}/catalog-service/api/consumer/resources/{}/actions/{}/requests".format(vrafqdn,resid,actionid)
     #print "Url is " + vraResUrl
     #resreq = requests.request("POST", vraResUrl,json=payload,headers=vraheaders, verify=False) 
     resreq = requests.post(vraResUrl,json=payload,headers=vraheaders, verify=False)
     #print resreq
     #print resreq.headers
     y=resreq.headers['location']
     if resreq.status_code == 201:
          print 60 * " "
          print 60 * " "
          print bcolors.OKGREEN + ("Action succesfully triggered on ")+ machine+ bcolors.ENDC
          print bcolors.OKBLUE + 85 * "-" + bcolors.ENDC
          return 'Passed',y

     else:
          print 60 * " "
          print 60 * " "
          print bcolors.WARNING + ("Please check the error")+machine+bcolors.ENDC
          print bcolors.OKBLUE + 85 * "-" + bcolors.ENDC
          return 'Failed','NA'
          

def resource_action(action,machine,resid,reqid,vrafqdn,vraheaders,owner,group,new_owner):
   if resid != "NA":
      vraResUrl="https://{}/catalog-service/api/consumer/resources/{}/actions".format(vrafqdn,resid)
      vrareqUrl="https://{}/catalog-service/api/consumer/resources/{}/actions".format(vrafqdn,reqid)
      resreq = requests.request("GET", vraResUrl, headers=vraheaders, verify=False).json()['content']
      reqreq= requests.request("GET", vrareqUrl, headers=vraheaders, verify=False).json()['content']
      #print(json.dumps(reqreq, indent=4))
      if action=='Power Off':
          str_status = "False"
          for i in resreq:
              if i['name'] == 'Power Off':
                  str_status = "True"
                  break
          if str_status == "True":
              for i in resreq:
                  if i['name'] == 'Power Off':
                     actId = i['id']
                     temp_act=template(actId,resid,vrafqdn,vraheaders)
                     st_action=Machine_Action(temp_act, actId,resid,vrafqdn,vraheaders,machine)
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+':Power Off:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
          else:
             valid_machine.append(machine+':Power Off:exist: Action Not available')
             Final_status.append("NA#"+machine)


      elif action=='Destroy':
          str_status = "False"
          for i in resreq:
              if i['name'] == 'Destroy':
                  str_status = "True"
                  break

          if str_status == "True":
              for i in resreq:
                  if i['name'] == 'Destroy':
                     actId = i['id']
                     temp_act = template(actId,resid,vrafqdn,vraheaders)
                     st_action=Machine_Action(temp_act, actId,resid,vrafqdn,vraheaders,machine)
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+':Destroy:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
          else:
              valid_machine.append(machine+':Destroy:exist: Action Not available')
              Final_status.append("NA#"+machine)

      elif action == 'Change Owner':
          str_status = "False"
          for i in reqreq:
              if i['name'] == 'Change Owner':
                  str_status = "True"
                  break
          #print str_status

          if str_status == "True":
              for i in reqreq:
                  if i['name'] == "Change Owner":
                     actId = i['id']
                     #print "action id is :" + actId
                     temp_act = template(actId, reqid,vrafqdn,vraheaders)
                     #print temp_act
                     st_action=Change_owner(temp_act, actId,reqid,vrafqdn,vraheaders,new_owner,machine)
                     #print st_action
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+':Change Owner:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
          else:
             valid_machine.append(machine+':Change Owner:exist: Action Not available')
             Final_status.append("NA#"+machine)

      elif action == 'Reboot':
          str_status = "False"
          for i in resreq:
              if i['name'] == 'Reboot':
                  str_status = "True"
                  break
          if str_status == "True":
              for i in resreq:
                  if i['name'] == 'Reboot':
                     actId = i['id']
                     temp_act = template(actId,resid,vrafqdn,vraheaders)
                     st_action=Machine_Action(temp_act, actId,resid,vrafqdn,vraheaders,machine)
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+':Reboot:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
          else:
              valid_machine.append(machine+':Reboot:exist: Action Not available')
              Final_status.append("NA#"+machine)

      elif action == 'Shutdown':
          str_status = "False"
          for i in resreq:
              if i['name'] == 'Shutdown':
                  str_status = "True"
                  break
          if str_status == "True":
              for i in resreq:
                  if i['name'] == 'Shutdown':
                     actId = i['id']
                     temp_act = template(actId,resid,vrafqdn,vraheaders)
                     st_action=Machine_Action(temp_act, actId,resid,vrafqdn,vraheaders,machine)
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+':Shutdown:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
                     return status_api
          else:
              valid_machine.append(machine+':Shutdown:exist: Action Not available')
              Final_status.append("NA#"+machine)

      elif action == 'Set Shared Access Group':
          str_status = "False"
          for i in resreq:
              if i['name'] == 'Set Shared Access Group':
                  str_status = "True"
                  break
          if str_status == "True":
              for i in resreq:
                  if i['name'] == 'Set Shared Access Group':
                     actId = i['id']
                     temp_act = template(actId,reqid,vrafqdn,vraheaders)
                     st_action = Shared_Access(temp_act, actId,resid,vrafqdn,vraheaders,group,machine)
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+ ':Set Shared Access Group:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
                     break
          else:
              valid_machine.append(machine+':Set Shared Access Group:exist: Action Not available')
              Final_status.append('NA#'+machine)

      elif action == 'Decommission':
          str_status = "False"
          for i in reqreq:
              if i['name'] == 'Decommission':
                  str_status = "True"
                  break
          if str_status == "True":
              for i in reqreq:
                  if i['name'] == 'Decommission':
                     actId = i['id']
                     temp_act = template(actId,reqid,vrafqdn,vraheaders)
                     st_action=Machine_Action(temp_act, actId,reqid,vrafqdn,vraheaders,machine)
                     status=st_action[0]
                     status_api=st_action[1]
                     valid_machine.append(machine+':Decommission:exist:'+status)
                     Final_status.append(status_api+'#'+machine)
                     return status_api

          else:
             valid_machine.append(machine+':Decommission:exist: Action Not available')
             Final_status.append('NA#'+machine)

   else:
      valid_machine.append(machine+':Action NA: Machine Not Exist:Failed')
      print 60 * " "
      print 60 * " "
      print " Machine " + bcolors.WARNING + machine + bcolors.ENDC + " not found..."
      print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
      Final_status.append('NA#'+machine)

valid_machine=[]
Final_status=[]

def Inputs():
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
    print bcolors.OKBLUE + 1 * "|" + bcolors.ENDC, 20 * " ", bcolors.BOLD + bcolors.CWHITE2 + "Enter the inputs: "+ bcolors.ENDC, 34 * " ", bcolors.OKBLUE + 1 * "|" + bcolors.ENDC
    print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
    print 60 * " "
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * "" 
    File_st=raw_input( bcolors.CWHITE+ "Enter the file path of machines: "+bcolors.OKBLUE)
    print 60 * " " + bcolors.ENDC
    while(str(os.path.exists(File_st))!= 'True'):
      print bcolors.FAIL
      Ent=raw_input( "\nWrong file path.Type [Yes] to type the filepath again Or Type [Exit/No] to Exit the code.: ")     
      if Ent in ('EXIT', 'exit', 'Exit', 'NO','N','No','no'):
            sys.exit()
      elif Ent in ('YES','Y','Yes','yes','y'):
           print 60 * " " + bcolors.CWHITE2
           File_st=raw_input( bcolors.CWHITE+ "Enter the file path of machines.. "+bcolors.OKBLUE)
           print bcolors.ENDC
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * ""
    mail=raw_input(bcolors.CWHITE + "Enter the mail id on which you want to recieve the report : "+ bcolors.OKBLUE)
    print 60 * " " + bcolors.ENDC
    print bcolors.BOLD + bcolors.CWHITE2 + 4 * ""
    incident=raw_input(bcolors.CWHITE + "Enter the Incident no.:  "+ bcolors.OKBLUE)
    print bcolors.ENDC
    return File_st,mail,incident
    

def machine_info(vrafqdn,vra_env,vraheaders,action,group,new_owner,file_path,user,incident_info,receiver_id):
    vra_vmInfo =[]
    tableList = []
    resource_id_ary = []
    clear()
    print 60 * " "
    print 60 * " "
    with open(file_path, "r") as f:
      for content in f:
         vra_vmInfo.append(content.strip('\n'))
         vMName = content.strip('\n')
         valDict = OrderedDict()
         rid_list = resource_id(vMName,vrafqdn,vraheaders)
         resource_id_ary.append(rid_list)
         owner = rid_list[3]
         mach_st = rid_list[4]
         valDict = OrderedDict()
         valDict['ENVIRONMENT_NAME'] = vra_env
         valDict['MACHINE_NAME'] = vMName
         valDict['OWNER_NAME'] = owner
         valDict['ACTION'] = action
         valDict['MACHINE_STATUS'] = mach_st
         valDict['ACTION'] = action
         tableList.append(valDict)
         if mach_st == 'not_exist':
             connect_mysql.insert_query('day_two_action_info',ENVIRONMENT_NAME=vra_env,VM_NAME=vMName,INCIDENT_NUMBER=incident_info,USER_NAME=user,VM_ACTION=action,ACTION_STATUS='Failed',ACTION_DATE=date_time().sqldate(),ACTION_TIME=date_time().sqltime())
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
    print 60 * " "
    print  bcolors.OKBLUE + "Below are the machines selected to perform "  + action   + " action on it" + bcolors.ENDC
    print 60 * " "
    print bcolors.CWHITE2 + 85 * "-" + bcolors.ENDC
    printTable(tableList)
    WAITContinue()
    clear()
    for res_id in resource_id_ary:
        machine = res_id[0]
        resid = res_id[1]
        reqid = res_id[2]
        owner = res_id[3]
        mach_st = res_id[4]
        status_api=resource_action(action,machine,resid,reqid,vrafqdn,vraheaders,owner,group,new_owner)
        #print status_api
    time.sleep(2)
    clear()
    print bcolors.CWHITE2
    print '\n\t\tFINAL STATUS'
    print '\t\t'+("-" * 15) +'\n'+bcolors.ENDC
    tableList = []
    for int_data in valid_machine:
      valDict = OrderedDict()
      valDict['VM_NAME'] = int_data.split(":")[0]
      valDict['ACTION_INFO'] = int_data.split(":")[1]
      valDict['VM_STATUS'] = int_data.split(":")[2]
      valDict['ACTION_STATUS'] = int_data.split(":")[3]
      tableList.append(valDict)
    printTable(tableList)
    StdOut = '/tmp/report.csv'
    with open(StdOut, 'w') as out:
        with custom_redirection(out):
            printTable(tableList)
    mail_status_send(sender_id,receiver_id,mail_subject='Day 2 Action triggered Status Report')
    sleep_tm(tm_scd=15)
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.OKBLUE + 112 * "-" + bcolors.ENDC
    print 4 * " ", bcolors.BOLD + bcolors.CWHITE2 + "Triggered Action Status Report will be sent to your mail in few mins....Please keep the script running... "+ bcolors.ENDC
    print bcolors.OKBLUE + 112 * "-" + bcolors.ENDC
    print 60 * " "
    print 60 * " "
    sleep_tm(tm_scd=130)
    print "\n"
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.OKBLUE + 65 * "-" + bcolors.ENDC
    print bcolors.OKBLUE + 1 * "|" + bcolors.ENDC, 20 * " ", bcolors.BOLD + bcolors.CWHITE2 + "Final Status Check  "+ bcolors.ENDC, 20 * " ", bcolors.OKBLUE + 1 * "|" + bcolors.ENDC
    print bcolors.OKBLUE + 65 * "-" + bcolors.ENDC
    print 60 * " "
    print 60 * " "
    tableList = []
    snum = 1
    for i in Final_status:
      status_api,machine=i.split('#')
      if status_api!='NA':
          response=requests.get(status_api,headers=vraheaders,verify=False)	
          #print(json.dumps(response.json(), indent=4))
          valDict = OrderedDict()
          #valDict['VM_NAME'] = json.loads(response.text)['resourceRef']['label']
          valDict['VM_NAME'] =machine
          valDict['ACTION_INFO'] = json.loads(response.text)['resourceActionRef']['label']
          valDict['Action_STATUS'] = json.loads(response.text)['state']
          tableList.append(valDict)
          connect_mysql.insert_query('day_two_action_info',ENVIRONMENT_NAME=vra_env,VM_NAME=machine,INCIDENT_NUMBER=incident_info,USER_NAME=user,VM_ACTION=json.loads(response.text)['resourceActionRef']['label'],ACTION_STATUS=json.loads(response.text)['state'],ACTION_DATE=date_time().sqldate(),ACTION_TIME=date_time().sqltime())
      else:
          valDict = OrderedDict()
          valDict['VM_NAME'] =machine
          valDict['ACTION_INFO'] =action
          valDict['Action_STATUS'] ='Failed/NA'
          tableList.append(valDict)
          connect_mysql.insert_query('day_two_action_info',ENVIRONMENT_NAME=vra_env,VM_NAME=machine,INCIDENT_NUMBER=incident_info,USER_NAME=user,VM_ACTION=action,ACTION_STATUS='Failed',ACTION_DATE=date_time().sqldate(),ACTION_TIME=date_time().sqltime())
    
    printTable(tableList)
    print bcolors.OKBLUE + 65 * "-" + bcolors.ENDC
    print 60 * " "
    print 60 * " "
    StdOut = '/tmp/report.csv'
    with open(StdOut, 'w') as out:
        with custom_redirection(out):
            printTable(tableList)
    mail_status_send(sender_id,receiver_id,mail_subject='Final Day 2 Action Status Report')

def vra_auth(vrafqdn,user,password,tenant):
   url="https://{}/identity/api/tokens".format(vrafqdn)
   payload= '{{"username":"{}","password":"{}","tenant":"{}"}}'.format(user,password,tenant)
   headers= {
     'accept':"application/json",
     'content-type':"application/json",
      }
   response= requests.request("POST",url,data=payload,headers=headers,verify=False)
   if response.status_code != 200:
       print 60 * " "
       print 60 * " "
       print bcolors.FAIL + ("Authentication Failed. Check the username or password!")
       print bcolors.OKBLUE + 105 * "-" + bcolors.ENDC
       sys.exit()
   else:
       print 60 * " "
       print 60 * " "
       print bcolors.OKGREEN + ("Authentication successful....")
       time.sleep(3)
       j = response.json()['id']
       auth = "Bearer "+j
       return auth


def sub_selection(vrafqdn,tenant,vra_env):
    clear()
    print 60 * " "
    print 60 * " "
    print bcolors.OKBLUE + 105 * "-" + bcolors.ENDC
    print bcolors.OKBLUE + 1 * "|" + bcolors.ENDC, 20 * " ", bcolors.BOLD + bcolors.CWHITE2 + "Authentication for Environment "+vra_env.upper()+" For Tenant "+tenant + bcolors.ENDC, 22 * " ", bcolors.OKBLUE + 1 * "|" + bcolors.ENDC
    print bcolors.OKBLUE + 105 * "-" + bcolors.ENDC
    print 60 * " "
    print 60 * " "
    user = raw_input("Enter the username: ")
    password = getpass("Password: ")
    auth = vra_auth(vrafqdn, user, password, tenant)
    vraheaders = {
        'content-type': "application/json",
        'accept': "application/json",
        'authorization': auth
    }
    print bcolors.OKBLUE + 105 * "-" + bcolors.ENDC
    sub_loop = True
    while sub_loop:
        act_selection()
        choose = input("Enter which action you want to run on these machine from [1..8] ")
        if choose == 1:
            action = 'Power Off'
            group="NA"
            msid="NA"
            Input=Inputs()
            file=Input[0]
            print file
            mail=Input[1]
            incident_info=Input[2]
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break
        elif choose == 2:
            action = 'Destroy'
            group="NA"
            msid="NA"
            Input=Inputs()
            file=Input[0]
            mail=Input[1]
            incident_info=Input[2]
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break
        elif choose == 3:
            action = 'Change Owner'
            group="NA"
            print 60 * " "
            print 60 * " "
            print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
            Input=Inputs()
            file=Input[0]
            mail=Input[1]
            incident_info=Input[2]
            print bcolors.BOLD + bcolors.CWHITE2 + 4 * ""
            msid= raw_input(bcolors.CWHITE +"Enter the new owner id in format (msid@your_org_domain_name):" +bcolors.OKBLUE)
            print msid
            print 60 * " " + bcolors.ENDC
            WAITContinue()
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break
        elif choose == 4:
            action = 'Reboot'
            group="NA"
            msid="NA"
            Input=Inputs()
            file=Input[0]
            mail=Input[1]
            incident_info=Input[2]
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break
        elif choose == 5:
            action = 'Shutdown'
            group="NA"
            msid="NA"
            Input=Inputs()
            file=Input[0]
            mail=Input[1]
            incident_info=Input[2]
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break
        elif choose == 6:
            action = 'Set Shared Access Group'
            Input=Inputs()
            file=Input[0]
            mail=Input[1]
            incident_info=Input[2]
            print bcolors.BOLD + bcolors.CWHITE2 + 4 * ""
            group=raw_input(bcolors.CWHITE +"Enter the group Name to which access needs to be provided: "+ bcolors.OKBLUE)
            print 60 * " " + bcolors.ENDC
            print bcolors.OKBLUE + 77 * "-" + bcolors.ENDC
            msid="NA"
            print 60 * " "
            WAITContinue()
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break

        elif choose == 7:
            action = 'Decommission'
            group="NA"
            msid="NA"
            Input=Inputs()
            file=Input[0]
            mail=Input[1]
            incident_info=Input[2]
            machine_info(vrafqdn,vra_env,vraheaders,action,group,msid,file,user,incident_info,mail)
            break

        elif choose == 8:
            sys.exit()
        else:
            input("Wrong input selection. Please choose the options between (1..8) and try again... ")


def main():
    clear()
    loop = True
    while loop:
        env_selection()
        choice = input("Enter your choice [1-5]: ")
        if choice == 1:
            vra_env="Dev"
            vrafqdn = 'vra-dev.your_org_domain_name'
            tenant = 'Your_Org_dev01'
            sub_selection(vrafqdn,tenant,vra_env)
            sys.exit()
        elif choice == 2:
            vra_env="Test"
            vrafqdn = 'vra-test.your_org_domain_name'
            tenant = 'Your_Org_tst01'
            sub_selection(vrafqdn,tenant,vra_env)
            sys.exit()
        elif choice == 3:
            vra_env="Stage"
            vrafqdn = 'vra-stage.your_org_domain_name'
            tenant = 'Your_Org_stg01'
            sub_selection(vrafqdn,tenant,vra_env)
            sys.exit()
        elif choice == 4:
            vra_env="Prod"
            vrafqdn = 'vra.your_org_domain_name'
            tenant = 'xxxxxxxxxx_your tenanat_ID'
            sub_selection(vrafqdn,tenant,vra_env)
            sys.exit()
        elif choice == 5:
            sys.exit()
        else:
            input("Wrong input selection. Please choose the options between (1..5) and try again... ")

main()
