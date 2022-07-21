import requests
from time import sleep
import json

print("使用本软件请将此软件与hmcl放置再一个目录.确保文件夹中有hmcl.json文件如果没有请先打开hmcl初始化")
print("右键hmcl.json把Hidden/隐藏选项去掉.再使用本软件")
refresh_token = input("请输入Refresh_Token:")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko", "Accept-Language": "en-US,en;q=0.9,fa;q=0.8"}
data = {
    "token_type": "bearer",
    "expires_in": 86400,
    "scope": "service::user.auth.xboxlive.com::MBI_SSL",
    "refresh_token": refresh_token,
    "foci": "1",
    "client_id": "00000000402b5328",
    "grant_type": "refresh_token"
}
res = requests.post("https://login.live.com/oauth20_token.srf", headers=headers, data=data)
if "error" in res.text:
    print(res.text)
    sleep(10)
    exit()
res = res.json()
at1 = res.get("access_token")
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Accept": "application/json",
        "x-xbl-contract-version": "0"}
payload = {
    "RelyingParty": "http://auth.xboxlive.com",
    "TokenType": "JWT",
    "Properties": {
        "AuthMethod": "RPS",
        "SiteName": "user.auth.xboxlive.com",
        "RpsTicket": at1,
    }
}
res = requests.post("https://user.auth.xboxlive.com/user/authenticate", json=payload,
                    headers=headers).json()
token = res["Token"]
payload = {
    "RelyingParty": "rp://api.minecraftservices.com/",
    "TokenType": "JWT",
    "Properties": {
        "SandboxId": "RETAIL",
        "UserTokens": [
            token
        ]
    }
}
resp = requests.post("https://xsts.auth.xboxlive.com/xsts/authorize", json=payload,headers=headers)
if resp.status_code != 200:
    if resp.status_code == 401:
        json = resp.json()
        if json["XErr"] == 2148916233 or json["XErr"] == "2148916238":
            print("NoXbox or Child Accuont")
            sleep(10)
            exit()
        else:
            print(f"Unknown Xsts Error code: {json['XErr']}")
            sleep(10)
            exit()
    else:
        print(resp.text)
        sleep(10)
        exit()
data = resp.json()
token = data["Token"]
user_hash = data["DisplayClaims"]["xui"][0]["uhs"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Accept": "application/json"
}
payload = {"identityToken": f"XBL3.0 x={user_hash};{token}"}
res = requests.post("https://api.minecraftservices.com/authentication/login_with_xbox",
                    json=payload,
                    headers=headers)
userid = res.json()["username"]
access_Token = res.json()["access_token"]
headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Authorization": f"Bearer {access_Token}"
}
res = requests.get("https://api.minecraftservices.com/minecraft/profile", headers=headers).json()
username = res.get("name")
uuid = res.get("id")
accountInfo = {
      "uuid": uuid,
      "displayName": username,
      "tokenType": "Bearer",
      "accessToken": access_Token,
      "refreshToken": refresh_token,
      "userid": userid,
      "type": "microsoft",
      "selected": True}
hmclCfg = open("hmcl.json", "r").read()
hmclCfg = json.loads(hmclCfg)
AccuontInfoList = hmclCfg.get("accounts")
AccuontInfoList.append(accountInfo)
hmclCfg["accounts"] = AccuontInfoList
open("hmcl.json", "w").write(json.dumps(hmclCfg, ensure_ascii=False))
print("登录成功!")
sleep(10)
