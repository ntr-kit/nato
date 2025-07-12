from socket import socket, AF_INET, SOCK_STREAM
import datetime
import bot_press

HOST = '192.168.1.23'
PORT = 51000
MAX_MESSAGE = 2048
NUM_THREAD = 1

CHR_CAN = '\18'
CHR_EOT = '\04'

def com_receive():
    #global sock

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind ((HOST, PORT))
    sock.listen (NUM_THREAD)
    
    light = 1
    print ('receiver ready...')

    while True:
        try:
            now = datetime.datetime.now()
            current_hour = now.hour
            conn,addr = sock.accept()
            mess = conn.recv(MAX_MESSAGE).decode('utf-8')
            mess = round(float (mess))
            conn.close()
            if(mess == CHR_EOT):
                break

            if(mess == CHR_CAN):
                continue

            print(mess,now.strftime('%Y/%m/%d %H:%M') )
            
            if 0 <= current_hour <= 2:
                if mess > 200.0000 and light == 1:
                 bot_press.main()
                 light = 0
                 
            else:
                light = 1
                 

        except KeyboardInterrupt:
            sock.close()
            print('end')
            break
        
if __name__ == '__main__':
    com_receive()