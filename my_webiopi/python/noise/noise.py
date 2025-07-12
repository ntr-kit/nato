#import webiopi

content = "from web\n"

#@webiopi.macro
def run_script():

 with open('/home/pi/my_webiopi/python/example.txt', 'a') as file:
  file.write(content)
  file.close()
  print("Success\n")

run_script()
