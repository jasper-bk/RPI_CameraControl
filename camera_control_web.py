#!/usr/bin/env python3
#-*- coding:UTF-8 -*-

import os, sys, tty, termios, time
import pigpio #sudo pigpio 
from flask import Flask, Response, stream_with_context
import requests
app = Flask(__name__)

class Kamera:

    def __init__(self):
        self.servo_pin_vertikal = 9
        self.servo_pin_horizontal = 11

        self.pi = pigpio.pi()

        self.verti_pos = 90
        self.hori_pos = 90

        self.init()

    def init(self):
        self.setze_servo_pos_horizontal(self.hori_pos)
        self.setze_servo_pos_vertikal(self.verti_pos)

    def setze_servo_pos_vertikal(self, pos):
        pulsweite = 500 + 2000 * round(pos/180, 2)

        if pulsweite < 500:
            pulsweite = 500
            self.verti_pos = 0
        elif pulsweite > 2500:
            pulsweite = 2500
            self.verti_pos = 180
        else:
            self.verti_pos = pos

        self.pi.set_servo_pulsewidth(self.servo_pin_vertikal, pulsweite)
        print("Verti.DutyCycle: " + str(pulsweite) )

        time.sleep(0.05)
        self.pi.set_servo_pulsewidth(self.servo_pin_vertikal, 0)

    def setze_servo_pos_horizontal(self, pos):
        pulsweite = 500 + 2000 * round(pos/180, 2)

        if pulsweite < 500:
            pulsweite = 500
            self.hori_pos = 0
        elif pulsweite > 2500:
            pulsweite = 2500
            self.hori_pos = 180
        else:
            self.hori_pos = pos

        self.pi.set_servo_pulsewidth(self.servo_pin_horizontal, pulsweite)

        print("Hori.DutyCycle: " + str(pulsweite) )

        time.sleep(0.05)

        self.pi.set_servo_pulsewidth(self.servo_pin_horizontal, 0)

    def links(self):
        self.setze_servo_pos_horizontal(self.hori_pos+3)

    def rechts(self):
        self.setze_servo_pos_horizontal(self.hori_pos-3)

    def hoch(self):
        self.setze_servo_pos_vertikal(self.verti_pos+3)

    def runter(self):
        self.setze_servo_pos_vertikal(self.verti_pos-3)

    def zeige_pos(self):
        print("x: " + str(self.hori_pos) + ", y: " + str(self.verti_pos))

kamera = Kamera()


html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>RPI4 PTZ Kamera</title>
</head>
<body style="text-align:center">
<h1>RPI4 PTZ-Kamera</h1>

<img src="/kamera" id="kamera">

<script>
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}
//document.getElementById('restreamer-player').src= "http://" + window.location.hostname + ":8081/player.html";

document.onkeydown = checkKey;

function checkKey(e) {

    e = e || window.event;

    if (e.keyCode == '38') {
        httpGet('/oben')
    }
    else if (e.keyCode == '40') {
        httpGet('/unten')
    }
    else if (e.keyCode == '37') {
       httpGet('/links')
    }
    else if (e.keyCode == '39') {
       httpGet('/rechts')
    }
}
</script>
<br/>

<table style="margin-left:auto; margin-right:auto;">
    <tr><td></td><td><button type="button" onclick="httpGet('/oben')">Nach Oben!</button></td><td></td></tr>
    <tr><td><button type="button" onclick="httpGet('/links')">Nach Links!</button></td><td></td><td><button type="button" onclick="httpGet('/rechts')">Nach Rechts!</button></td></tr>
    <tr><td></td><td><button type="button" onclick="httpGet('/unten')">Nach Unten!</button></td><td></td></tr>
</table>
<button type="button" onclick="document.getElementById('kamera').style.width = '300px'">300px</button><br/>
<button type="button" onclick="document.getElementById('kamera').style.width = '400px'">400px</button><br/>
<button type="button" onclick="document.getElementById('kamera').style.width = '600px'">600px</button><br/>
<button type="button" onclick="document.getElementById('kamera').style.width = '800px'">800px</button><br/>
<button type="button" onclick="document.getElementById('kamera').style.width = '1000px'">1000px</button>

</body>
</html>

"""

@app.route("/")
def index():
    return html_code

#Proxy zum Kamera-Stream
@app.route("/kamera")
def kamera_stream():
    req = requests.get('http://localhost:8081', stream = True)
    return Response(stream_with_context(req.iter_content(chunk_size=10*1024)) , mimetype=req.headers['Content-Type'], content_type=req.headers['Content-Type'], direct_passthrough=True )

@app.route("/links")
def seite_links():
    kamera.links()
    return "Nach Links!"

@app.route("/rechts")
def seite_rechts():
    kamera.rechts()
    return "Nach Rechts!"

@app.route("/oben")
def seite_oben():
    kamera.hoch()
    return "Nach Oben!"

@app.route("/unten")
def seite_unten():
    kamera.runter()
    return "Nach Unten!"

def main():
    app.run(host= '0.0.0.0', port="5000")


if __name__ == '__main__':
    main()