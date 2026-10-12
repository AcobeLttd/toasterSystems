from gpiozero import LED
from time import sleep

blue = LED(17)
g = 0
#sets led pin to 17

while True: #Infinite loop, sort of like void loop
    red.on()
    sleep(1)
    red.off()
    sleep(1)
    g+=1
    print("hello world", g)