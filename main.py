#-*-coding:utf-8-*-

import os
import requests
import time
import ast

rpath = "/home/<userhome>"    #例/home/rex
tempPath = rpath + "/back_MySQL"    #main.py所在資料夾
targetFolder = rpath + "/backupMySQL"    #備份檔存放資料夾
machineTxt = rpath + "/.machine/machine.txt"    #主機資料
getToday = time.strftime("%Y%m%d", time.localtime())
mySQLAcc = "<xxx>"    #MySQL 帳號
mySQLPass = "<xxx>"    #MySQL 密碼
mySQLPort = "<sql_port>"    #MySQL Port 號 預設為3306
dbName = "<db_name>"    #欲備份的資料庫名稱，需有權限

def getIPList(path):
    #Get All Machine IP
    data = open(path, "r", encoding="utf-8")
    datalist = data.read()
    ips = datalist.split()
    return ips

def getMachineList(path):
    #Get Machine IPs and operator name
    #data type: dict
    data = open(path, "r", encoding="utf-8")
    datalist = data.read()
    redata = ast.literal_eval(datalist)

    return redata

#檢查資料夾是否存在
def chkBackUpFolder(path, folderNmae=""):
    if(os.path.isdir(path + "/" + folderNmae)):
        return path + "/" + folderNmae

    os.system("sudo mkdir " + path + "/" + folderNmae)
    return path + "/" + folderNmae


#檢查檔案是否已存在
def chkBackUpDataName(path, prefixName, dfName="", tar="", num=1):
    for d in range(num, num+1):
        suffixNum = ("%03d")%(d)

    nTargetdfName = ""

    if(dfName != ""):
        ndfName = "." + dfName 

    if(tar != ""):
        nTargetdfName = "." + dfName + "." + tar

    if(os.path.isfile(path+prefixName+suffixNum+nTargetdfName)):
        num += 1
        return chkBackUpDataName(path, prefixName, dfName, tar, num)

    fullName = prefixName+suffixNum+ndfName
    
    return fullName

def telegramMsag(msg):
    oneCDNLoginAcc = "ppcaipiao123@3311.com"
    oneCDNLoginPass = "ppcaipiao123"

    telegramBot = "<telegramBot>"
    telegramBot2 = "<telegramBot2>"
    telegramToken = "<telegramToken_key>"
    telegramToken2 = "<telegramToken2_key>"
    telegramSendUrl = "https://api.telegram.org/" + telegramBot2 + ":" + telegramToken2 + "/sendMessage"
    telegramChatId = "@" + "a123485sw859"
    telegramPlData = {
                          "chat_id": telegramChatId, 
                          "text": "", 
    }

    telegramPlData["text"] = msg
    requests.get(telegramSendUrl, data=telegramPlData)

if __name__ == "__main__":

    if(os.path.isdir(targetFolder) == False):
        #沒有備份目標資料夾則退出程序
        print("Target folder does not exist ....")
        os._exit(0)

    if(os.path.isfile(machineTxt) == False):
        #沒有IP設定檔則退出程序
        print("Machine IPs does not exist ....")
        os._exit(0)

    #取得所有欲備份資料庫的伺服器
    machineList = getMachineList(machineTxt)

    #取得所有欲備份資料庫的伺服器
    #ips = getIPList(machineTxt)

    for machine in machineList:

        targetFolderPath = chkBackUpFolder(targetFolder, machineList[machine]["Operator"])
        backupSQLName = chkBackUpDataName(targetFolderPath+"/", getToday, "sql", "tar.gz")
        msg1 = "開始備份 " + machineList[machine]["Operator"]
        telegramMsag(msg1)
        mySQLIp = machineList[machine]["mysqlip"]

        #mysqldump 命令語句
        cmdMysqldump = "sudo mysqldump -u" + mySQLAcc + " -p" + mySQLPass + " -h" + mySQLIp + " -P"
        cmdMysqldump += mySQLPort + " " + dbName+" > " + tempPath + "/" + backupSQLName
        getResult = os.system(cmdMysqldump)
        
        if(getResult == 0):

            cmdTar = "sudo tar -C " + tempPath + " -zcPf " + tempPath + "/"
            cmdTar += backupSQLName + ".tar.gz " + backupSQLName
            os.system(cmdTar)
            os.system("sudo rm -rf " + tempPath + "/" + backupSQLName)
            os.system("sudo mv " + tempPath + "/" + backupSQLName + ".tar.gz " + targetFolderPath)
                    
            if(os.path.isfile(targetFolderPath+"/"+backupSQLName+".tar.gz")):
                backUpStatus = "成功"

        else:
            backUpStatus = "失敗"

        getNowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = "MySQL 資料庫備份 \n"
        msg += "主機： " + machineList[machine]["Operator"] + "\n"
        msg += "檔案： " + backupSQLName + ".tar.gz \n"
        msg += "時間： " + getNowTime + "\n"
        msg += "備份 " + backUpStatus

        telegramMsag(msg)
