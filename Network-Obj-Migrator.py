import sys
from FMC import *
from PA import *
from xlsx import read_xlsx_file
s = 'y'
while s == 'y':
    print(colored('Welcome to bmb Network Object Migrator', 'red'))
    print(colored('Select your Source and Destination of objects from the following', 'red'))
    print(colored('1. excel file\n2. Cisco FMC\n3. Palo Alto FW\n4. Palo Alto Panorama\n5. Fortigate FW\n6. StoneGate FW', 'cyan'))
    Srxlsx = False
    SrFMC = False
    SrPAFW = False
    SrPAP = False
    SrFortiFW = False
    SrStoneGate = False

    FMC = False
    PAFW = False
    PAP = False
    FortiFW = False
    StoneGate = False

    source = int(input(colored('enter the source number : ', 'blue')))
    if source == 1:
        Srxlsx = True
    if source == 2:
        SrFMC = True
    if source == 3:
        SrPAFW = True
    if source == 4:
        SrPAP = True
    if source == 5:
        SrFortiFW = True
    if source == 6:
        SrStoneGate = True
    trigerFMC = input(colored('Migrate to Cisco FMC ? y or n : ', 'blue'))
    trigerPAFW = input(colored('Migrate to Palo Alto FW ? y or n : ', 'blue'))
    trigerPAP = input(colored('Migrate to Palo Alto Panorama ? y or n : ', 'blue'))
    trigerFortiFW = input(colored('Migrate to Fortigate FW ? y or n : ', 'blue'))
    trigerStoneGate = input(colored('Migrate to Stonegate FW ? y or n : ', 'blue'))
    if trigerFMC == 'y':
        FMC = True
    if trigerPAFW == 'y':
        PAFW = True
    if trigerPAP == 'y':
        PAP = True
    if trigerFortiFW == 'y':
        FortiFW = True
    if trigerStoneGate == 'y':
        StoneGate = True
    #############################################################################
    ############################ Log in #########################################
    #############################################################################
    if FMC == True or SrFMC == True:
        FMC_ip =input(colored('enter your FMC IP address : ', 'blue'))
        (headers, Domain_id) = FMC_login(FMC_ip)
    if PAFW == True or SrPAFW == True:
        print('PAFW')
        PAFW_ip = input(colored('enter your Palo Alto FW IP address : ', 'blue'))
        Vsys = input(colored('insert Virtual System name : ','blue'))
        Vsys = 'vsys1'
        (PAFW_key, SyS_Exit) = PAFW_login(PAFW_ip)
    if PAP == True or SrPAP == True:
        print('pap')
    if FortiFW == True or SrFortiFW == True:
        print('forti')
    if StoneGate == True or SrStoneGate == True:
        print('Stone')

    #############################################################################
    ############################ Load and Convert Src Objects ###################
    #############################################################################
    if Srxlsx == True:
        #file_Dir = input(colored('Enter Your .xlsx file directory : ', 'blue'))
        file_Dir = 'NetworkObjSheet.xlsx'
        OriginalFormList = read_xlsx_file(file_Dir)
    if SrFMC == True:
        file_Dir = 'FMC_Objects_Source'
        FMC_Source_Triger = True
        OriginalFormList = FMC_ReadNetworkObject(FMC_ip, headers, Domain_id, file_Dir, FMC_Source_Triger)
    if SrPAFW == True:
        file_Dir = 'PAFW_Objects_Source.xml'
        PAFW_Source_Triger = True
        PAFW_ReadNetworkObject(PAFW_ip, PAFW_key, Vsys, file_Dir,PAFW_Source_Triger)
    if SrPAP == True:
        exit()
    if SrFortiFW == True:
        exit()
    if SrStoneGate == True:
        exit()
    #############################################################################
    ############################ Load Destination Target ###################
    #############################################################################
    if FMC == True:
        print('FMC')
    if PAFW == True:
        print('PAFW')
    if PAP == True:
        print('PAP')
    if FortiFW == True:
        print('FortiFW')
    if StoneGate == True:
        print('StoneGate')
    #############################################################################
    ############################ Posting Result ###################
    #############################################################################
    if FMC == True:
        FMC_Source_Triger = False
        file_Dir = 'FMC_Objects_Destinaion'
        FMC_Objects_Post(FMC_ip, headers, Domain_id, OriginalFormList,file_Dir,FMC_Source_Triger)
        print('post process 2')

    if PAFW == True:
        file_Dir = 'PAFW_Objects_Destination.xml'
        PAFW_Source_Triger = True
        PAFW_Objects_Post(PAFW_ip, PAFW_key, Vsys, OriginalFormList, file_Dir,PAFW_Source_Triger)
    if PAP == True:
        exit()
    if FortiFW == True:
        exit()
    if StoneGate == True:
        exit()
#################################################################################
#################################################################################
#################################################################################
    s = input(colored('press y to restart the program or press enter to exit : ', 'red'))
else :
    sys.exit()