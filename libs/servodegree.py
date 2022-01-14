from machine import Pin, PWM
from time import sleep
import utime

##DEFINIZIONE PIN
servoPin = PWM(Pin(16))
servoPin.freq(50)

####### Converte in gradi
def servo(degrees):
    if degrees > 180: degrees=180
    if degrees < 0: degrees=0
    maxDuty=9000
    minDuty=1000
    newDuty=minDuty+(maxDuty-minDuty)*(degrees/180)
    servoPin.duty_u16(int(newDuty))