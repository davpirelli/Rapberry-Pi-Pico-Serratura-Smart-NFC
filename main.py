#https://www.tomshardware.com/how-to/raspberry-pi-pico-powered-rfid-lighting
from libs.mfrc522 import MFRC522 #libreria RFID
from libs.neopixel import Neopixel #libreria neopixel
from random import randint
import utime
from machine import Pin, PWM
from utime import sleep

from libs.servodegree import servo

#Definisco lettore RFID
reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
#Numero di pixel dell'anello
numpix = 24
#Imposto numpixel, 0, pin di connessione, metodo
pixels = Neopixel(numpix, 0, 28, "GRB")
#Imposto il pin per il Buzzer
buzzer = PWM(Pin(15))
#Imposto lo stato della serratura iniziale (0 = Chiuso / 1 = Aperto)
stato = 0

#Spengo tutti i led
pixels.fill((0,0,0))
#Scrivo il valore sul led
pixels.show() 


####################################################
# FUNZIONI PER IL LED NEOPIXEL RING
####################################################

#Spegne i pixel
def spegni_pixel():
    pixels.fill((0,0,0))
    pixels.show()

#Luce fissa rossa
def lucerossa():
    pixels.fill((128,0,0))
    pixels.show()
  
#Luce fissa verde
def luceverde():
    pixels.fill((0,128,0))
    pixels.show()
        
#Lampeggia per X volte in rosso
def red_blynk(times):
    for i in range(times):
        pixels.fill((128,0,0))
        pixels.show()
        beep(0.1)
        utime.sleep_ms(100)
        beep(0.1)
        pixels.fill((0,0,0))
        pixels.show()
        utime.sleep_ms(100)

#Non in uso, sostituito da "loading"
def spirale():
    color = 100,100,100
    for i in range(24):
        print(i)
        pixels.set_pixel(i, (color))
        pixels.show()
        utime.sleep_ms(10)
    utime.sleep_ms(100)
    spegni_pixel()

#Spirale di caricamento bianca
def loading(speed):
    for i in range(24):
        pixels.set_pixel(i, (100, 100, 100))
        pixels.show()
        utime.sleep_ms(speed)
        beep(0.03)
    utime.sleep_ms(10)
    spegni_pixel()
    
#Lampeggia in fade verde
def success_boot():
    hue = 0
    for i in range(50):
        color = pixels.colorHSV(20000, 255, hue)
        pixels.fill(color)
        pixels.show()
        hue += 1
    hue1 = 50
    beep(0.1)
    for i in range(50):
        color = pixels.colorHSV(20000, 255, hue1)
        pixels.fill(color)
        pixels.show()
        hue1 -= 1
    spegni_pixel()



#####################################################
# INIZIO CODICE BUZZER 
#####################################################
def beep(durata):
    buzzer.freq(1500)
    buzzer.duty_u16(3000)
    sleep(durata)
    buzzer.duty_u16(0)
        

#####################################################
# INIZIO CODICE SERVO 
#####################################################        

def apri():
 servo(10)
 print("Serratura aperta")

def chiudi():
 servo(70)
 print("Serratura chiusa")
 
def toggle():
    global stato
    #Se lo stato è uno, chiudo la serratura e imposto la luce su rosso
    if stato == 1:
        stato = 0
        chiudi()
        lucerossa()
        utime.sleep_ms(1000)
    #Se lo stato è zero, apro la serratura e imposto la luce su verde
    elif stato == 0:
        stato = 1
        apri()
        luceverde()
        utime.sleep_ms(1000)
    else:
        red_blynk(5)
    
##############################################
# INIZIO CODICE ##############################
##############################################


print("Avvio in corso..")
chiudi()
utime.sleep_ms(500)
print("Attendere...")

for i in range(1):
    loading(20)
utime.sleep_ms(1000)
lucerossa()


while True:
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            print(card)
            if card == 1274987924:
                beep(0.1)
                toggle()
            elif card == 825572532:
                beep(0.1)
                toggle()
            else:
                print("Carta non trovata")
                red_blynk(3)
                chiudi()
                lucerossa()
        else:
            print("Reader KO")
            red_blynk(10)
            pass
utime.sleep_ms(50)
