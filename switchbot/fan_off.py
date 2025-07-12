import requests
from header import make_request_header, token, secret, base_url

#制御したいデバイスID
deviceId = "02-202306051904-77267992"
#デバイスの制御コマンド
data={
            "commandType": "command",
            "command": "setWindSpeed",
    }

def main():
    headers = make_request_header(token, secret)
    
    devices_url = base_url + "/v1.1/devices/" + deviceId + "/commands"
        
    try:
        res = requests.post(devices_url, headers=headers, json=data)
        res.raise_for_status()
        print(res.text)
        
    except requests.exceptions.RequestException as e:
        print('response error:')

if __name__ == "__main__":
    main()


