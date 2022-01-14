# Rapberry Pi Pico - Serratura Smart con NFC
Codice MicroPython per controllare un servo motore tramite card RFID autorizzate.

Vediamo come costruire una  **serratura smart**  con lettore di carte NFC RC522 e Raspberry Pi Pico, se non sai di cosa stiamo parlando,  [dai un occhiata al mio articolo sul Pico](https://davidepirelli.it/raspberry-pi-pico-scopiamo-insieme-cose/).

Se hai appena ricevuto il Raspberry Pi Pico, devi prima installare il firmware e Thonny,  [leggi l’articolo su come preparare la board!](https://davidepirelli.it/installare-thonny-iniziamo-ad-usare-il-nostro-raspberry-pi-pico/)

Andremo a vedere come collegare tutti i componenti richiesti per la nostra  **serratura smart**, come scrivere il codice e quali librerie utilizzare. In questa guida useremo un Ring Led  **Neopixel**, ma dato il costo elevato, nei prossimi giorni metterò a disposizione una versione “leggera” con le stesse funzionalità, eliminando alcuni elementi come il buzzer e sostituendo l’anello led Neopixel (24€) con due semplici led R/G.

### Materiali necessari:

Tutti i materiali richiesti per creare la nostra  **serratura smart**, sono facilmente reperibili su  _Amazon_  a qualche € in più, altrimenti potete fare un giro su  **[thepihut.com](https://thepihut.com/collections/pico)**  per avere il migior rapporto prezzo/spedizione.

-   1x  **Raspberry Pi Pico**
-   1x Lettore RFID RC522
-   1x Servo SG-90 (o equivalente)
-   1x Buzzer  _(facoltativo)_
-   1x Anello  **NeoPixel Ring 24**  RGB/BGR (_facoltativo, possiamo usare anche due semplici led Rosso/Verde), trovi la guida sulla variante più snella qui)_
-   x3 Fili di collegamento Maschio/Maschio
-   x12 Fili di collegamento Femmina/Maschio

### Schema di connessione Serratura Smart NFC/RFID

![](https://davidepirelli.it/wp-content/uploads/2022/01/image-2-1024x868.png)

Collegamenti Necessari per la serratura smart

### Serratura Smart NFC – Step By Step

Una volta collegati tutti i componenti alla nostra board, andiamo ad alimentare il Pico collegandolo al PC, e utilizzando  **Thonny**  iniziamo a scrivere il nostro codice.

Per prima cosa, importiamo tutte le librerie richieste, ovvero:

```python
from libs.mfrc522 import MFRC522 #libreria RFID
from libs.neopixel import Neopixel #libreria neopixel
from libs.servodegree import servo
from random import randint
import utime
from machine import Pin, PWM
from utime import sleep

```
Abbiamo importato, in ordine, la libreria  **del lettore RFID**  **MFRC522**, la libreria  **neopixel**  per gestire il ring RGB Neopixel (o qualsiasi led Neopixel, incluse le strip) e come ultima libreria esterna, la  **servodegree**  che ci consentirà di muovere il servo SG-90 (o qualsiasi altro servo) passando ad una funzione i gradi di movimento.  
Andiamo ora a importare le librerie interne a  **MicroPython**, nello specifico ci servirà  **utime**, una libreria che ci consente di accedere a date e intervalli di tempo.  
Importiamo poi da  **machine**  Pin e PWM, che useremo per definire i collegamenti sul nostro Pico.

### Definiamo i collegamenti

Se avete seguito il mio schema di connessione, potere copiare e incollare lo stesso codice all’interno del vostro main.py senza cambiare nulla.

```python
#Definisco lettore RFID
reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)

#Numero di pixel dell'anello
numpix = 24

#Imposto numpixel, 0, pin di connessione, metodo
pixels = Neopixel(numpix, 0, 28, "GRB")

#Imposto il pin per il Buzzer
buzzer = PWM(Pin(15))

```

Abbiamo definito una variabile  **reader**, passando tutte le connessioni effettuate secondo lo schema presente nell’immagine. Per gestire il  **NeoPixel Ring**, abbiamo prima definito la variabile  **numpix**  con il numero dei pixel del nostro anello (in questo caso 24, ma sono presenti anche anelli a 16 o a 8 led). Successivamente, dichiariamo la variabile  **pixels**, inserendo il metodo colore dell’anello (può essere RGB o GRB).

### Definiamo gli accessi

Una volta dichiarate le connessioni, possiamo scrivere la parte di codice relativa a gli accessi consentiti (ID univoci delle carte NFC RFID). Per farlo dichiariamo una variabile  **accessi**  nel quale inseriremo un array con tutti gli ID delle carte abilitate.

```python
#Metto in array gli id delle carte che hanno accesso
accessi = [2127566297, 1274987924, 825572532]

#Imposto lo stato della serratura iniziale (0 = Chiuso / 1 = Aperto)
stato = 0

```
La variabile  **stato**  la utilizzeremo nella funzione  **toggle,**  che vedremo più avanti. Questa variabile (_stato_) indicherà lo stato attuale della serratura smart (aperta 1, chiusa 0), in modo da poterla chiudere quando aperta, o aprirla quando chiusa.

### Definiamo alcuni “effetti” per il NeoPixel

Andiamo a scrivere alcune funzioni che ci permetteranno di creare degli effetti con il nostro anello RGB, in modo da avvisare ad esempio l’utente in modo visivo sullo stato della serratura smart (rosso – chiusa / verde – aperta).

```python
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

```

Abbiamo definito alcune funzioni, tra cui  **spegni_pixel**, questa funzione la useremo ogni volta allo startup del codice per assicurarci di “resettare” i pixel rimasti accesi a seguito di un errore non gestito.

### Logica di apertura e chiusura

Con tutte le variabili definite, e i collegamenti pronti, siamo al punto di scrivere il pezzo relativo all’apertura e chiusura della serratura.

```python
print("Avvio in corso..")
chiudi()
spegni_pixel()
utime.sleep_ms(500)
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
            if card in accessi:
                beep(0.1)
                toggle()
            else:
                print("Accesso negato")
                red_blynk(3)
                chiudi()
                lucerossa()
        else:
            print("Reader KO")
            red_blynk(10)
            pass
utime.sleep_ms(50)

```

Con questo ccodice, appena la nostra board riceverà corrente, andremo a chiudere la serratura (**chiudi()**) e spegnere i led  **(spegni_pixel())**, dopo una pausa di mezzo secondo  **(**utime.sleep_ms(500)**)**  andiamo a richiamare la funzione definita poco fa per il  **NeoPixel**  **(loading())**  passando come argomento l’attesa in millisecondi tra l’accensione di un pixel e un altro, creando cosi un effetto a “spirale” di accensione sequenziale dei led.

Attendiamo 1 secondo (**utime.sleep_ms(1000) o utime.sleep(1))**  e impostiamo l’anello sulla luce rossa (porta chiusa – tramite la funzione  **lucerossa())**

Andiamo a definire un ciclo senza fine (**while True:**) e inzializziamo il lettore RFID; assegniamo poi alla variabile  **card**  l’id letto dal RC255 e lo stampiamo in console (**print(card)**).

_NOTA: Questo print, ci permetterà di individuare l’id di qualsiasi carta che presentiamo al lettore, consentendoci poi di inserirla nell’array  **autorizzati.**_

Dopo aver letto la carta e assegnato l’id alla variabile  **card**  controlliamo tramite un  **if**  se la carta letta è presente tra le carte abilitate (**if card in accessi**).

Se l’ID della card presentata è presente nell’array di carte “conosciute” lanciamo la funzione  **toggle()**  che controllerà lo stato della serratura e, come detto sopra, se aperta la chiuderà e se chiusa la aprirà, impostando la luce del NeoPixel del relativo colore (rossa o verde). Inoltre usiamo la funzione  **beep(0.1)** per segnalare acusticamente l’avvenuta lettura della carta.  
Nel caso la carta presentata non fosse nell’elenco, restituiamo un errore con la funzione  **red_blynk(3)**  che farà lampeggiare per 3 volte in rosso il nostro NeoPixel.

Se hai domande, o dubbi, scrivi nei commenti del mio blog e..happy coding!
