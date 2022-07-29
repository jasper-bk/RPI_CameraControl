#!/usr/bin/env python3
#-*- coding:UTF-8 -*-

import os, sys, tty, termios, time
import pigpio #sudo pigpio 
from flask import Flask, Response, stream_with_context
import requests

import cv2 #for opencv camera

app = Flask(__name__)


cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

def gather_img():
    while True:
        time.sleep(0.1)
        _, img = cam.read()
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

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
<h1>RPI-Webcam</h1>

<img src="/kamera" id="kamera">

<script>
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function changeImage()
{
    document.getElementById('kamera').style.width = document.getElementById('image_size').value;
    document.getElementById('kamera').style.transform = "rotate("+ document.getElementById('image_rotation').value +"deg)";
}

document.addEventListener("change", changeImage);

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

<br/>

<p>Image size</p>
<select name="image_size" id="image_size">
<option value="300px" >300px</option>
<option value="400px" >400px</option>
<option value="600px" >600px</option>
<option value="800px" >800px</option>
<option value="1000px" >1000px</option>
<option value="1200px" >1200px</option>
</select>

<p>Image rotation</p>
<select name="image_rotation" id="image_rotation">
<option value="0" >0°</option>
<option value="90" >90°</option>
<option value="180" >180°</option>
<option value="270" >270°</option>
</select>

</body>
</html>

"""

@app.route("/")
def index():
    return html_code

#Proxy zum Kamera-Stream
@app.route("/kamera")
def kamera_stream():
    return Response(gather_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
