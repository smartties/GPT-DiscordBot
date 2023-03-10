import discord
import openai
from pytube import YouTube
import os
import requests
from pydub import AudioSegment
import subprocess
import math

openai.api_key = "INSERT YOUR OPENAI KEY HERE"

def DownloadYT(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_lowest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
        return False
    print("Download is completed successfully")
    return True

def DownloadAudio(link, name):
    yt = YouTube(link)
    # extract only audio
    video = yt.streams.filter(only_audio=True).last()
    # check for destination to save file
    #print("Enter the destination (leave blank for current directory)")
    destination = './temp/'
    # download the file
    #print("dl")
    out_file = video.download(output_path=destination)
    # save the file
    base, ext = os.path.splitext(out_file)
    new_file = name + '.mp3'
    os.rename(out_file, new_file)
  
    # result of success
    print(yt.title + " has been successfully downloaded.")
    return True


os.mkdir("./temp")
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
 
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
 
@client.event
async def on_message(message):
    global fullAccess
    if message.author == client.user:
        return 
    if message.author.bot :
        return
 
    
    if message.content.startswith('/prompt'):
        await message.channel.send("Seulement Martin peut me demander des choses")
    else:
        ss = message.content.replace('/prompt', '')

        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": ss}])
            
        chaine = completion['choices'][0]['message']['content']
            
        for i in range(0,len(chaine), 1600):
            mx = min(i+1600, len(chaine))
            m = chaine[i:mx]    
            await message.channel.send(m)
            
        if m.find("-speech") > 0:
            if os.path.exists("./temp/speech.wav"):
                os.remove("./temp/speech.wav")

            if m.find("-speechFR"):
                subprocess.call("mimic3 --voice fr_FR/tom_low \"" + chaine  + "\" > ./temp/speech.wav", shell=True)
            else:
                subprocess.call("mimic3 --voice en_UK/apope_low \"" + chaine + "\" > ./temp/speech.wav", shell=True)

            subprocess.call("ffmpeg -y -i ./temp/speech.wav -vn -ar 44100 -ac 2 -b:a 128k ./temp/speech.mp3", shell=True)
            await message.channel.send(file = discord.File("./temp/speech.mp3") )

    if message.content.startswith('/imagine'):
        ss = message.content.replace('/imagine', '')
        response = openai.Image.create(prompt=ss,n=1,size="1024x1024")
        image_url = response['data'][0]['url']
            
        img_data = requests.get(image_url).content
        with open("./temp/image.png", "wb") as handler:
            handler.write(img_data)

        await message.channel.send( file = discord.File("./temp/image.png") )

    if message.content.startswith('/transcript'):
        ss = message.content.replace('/transcript', '')
        yt = YouTube(ss)
            
        mm = "Téléchargement de " + yt.title
        await message.channel.send(mm)

        success = DownloadAudio(ss, "./temp/son")            
        
        await message.channel.send("Upload Sound to openai")

        if success:
            audioFile = open("./temp/son.mp3", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audioFile)
            
            chaine = transcript['text']
            for i in range(0,len(chaine), 1600):
                mx = min(i+1600, len(chaine))
                m = chaine[i:mx]
                await message.channel.send(m)
        else:
            await message.channel.send("Failed to download video from youtube")
        
 
client.run('INSERT YOUR DISCORD BOT TOKEN HERE')
