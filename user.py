
from pyrogram import Client,filters
from pyrogram import enums
from pyrogram.enums import  ParseMode
from pyrogram.types import Message
import time
import asyncio
import cowsay
import os
from google import genai
from google.genai import types
from pathlib import Path
import json
from dotenv import load_dotenv
while True:
    try:
    
        with open('config.json','r')as file:
            bd = json.load(file)
            bd.setdefault('model', "gemini-2.0-flash")
            bd.setdefault('white', [])
            break
    except FileNotFoundError:
        with open('config.json', 'w') as file:
            bd = {'model':"gemini-2.0-flash",'white': []}
            json.dump(bd,file,indent=4)
            print('Файл config.json створено')

try:
    load_dotenv('config.env')
    api_hash = os.getenv('API_HASH')
    api_id = int(os.getenv('API_ID'))
    api_key = os.getenv('API_KEY')
except:
    raise FileNotFoundError('ДОДАЙТЕ ФАЙЛ config.env ТА ВВЕДІТЬ ПОТРІБНІ ДАНІ')



client = Client(name='session', api_id=api_id, api_hash=api_hash)
ai_client = genai.Client(api_key=api_key)


def not_is_white(id_user):
    with open('config.json', 'r') as file:
        bd = json.load(file)
        if id_user in bd['white']:
            return False
        else:
            return True
def add_white(id_user):
    with open('config.json', 'r') as file:
           bd = json.load(file)
           print(bd['white'])
           bd['white'].append(id_user)
           json.dumps(bd)
    with open('config.json', 'w') as file:
        json.dumps(bd)
        json.dump(bd,file,indent=4)

def del_white(id_user):
    with open('config.json', 'r') as file:
           bd = json.load(file)
           print(bd['white'])
           bd['white'].remove(id_user)
           
    with open('config.json', 'w') as file:
        json.dumps(bd)
        json.dump(bd,file,indent=4)



@client.on_message(filters.command(commands='start_host',prefixes=['!','.']))
async def host(client:Client, message:Message):
    while True:
        await client.send_message('xto_ya_uabot', '/profile')
        await asyncio.sleep(300)


@client.on_message(filters.command(commands=['audio', 'поясни','аудио'],prefixes=['!','.']))
async def wav(client:Client, message:Message):
    if not_is_white(message.from_user.id):
        return #перевірка чи немає користувача в білому списку, якшо немає видає True
    print(1)
    print(message.reply_to_message.media)
    print(message.reply_to_message,message.reply_to_message.media )
    print(message.reply_to_message.media == "MessageMediaType.VOICE")
    try:
        if  message.reply_to_message.voice:
            await message.react("👀")
            temp_dir = Path("temp")
            temp_dir.mkdir(parents=True, exist_ok=True)  # Створюємо директорію, якщо її немає
            temp_file = temp_dir / "1.ogg"

            await message.reply_to_message.download(str(temp_file))

            file_a = ai_client.files.upload(file=str(temp_file))
            with open('config.json', 'r') as file:
                bd = json.load(file)
                model = bd['model']
            context = "Послухай аудіо і кинь транскрипцію"
            response =ai_client.models.generate_content(model=model,contents=[context, file_a], config=types.GenerateContentConfig(temperature=1.0))
            os.remove(temp_file)
            await message.reply(f"Транскрипція:\n{response.text}")
    except Exception as e:
        os.remove(temp_file)
        await message.reply(e)
        
        


@client.on_message(filters.command(commands=['list', 'white','білий'],prefixes=['!','.']))
async def white_list(client:Client, message:Message):
    print(not_is_white(message.from_user.id))
    if not_is_white(message.from_user.id):
        return #перевірка чи немає користувача в білому списку, якшо немає видає True
    text = message.text.split()
    if len(text) == 1:
            with open('config.json', 'r') as file:
                bd = json.load(file)
                await message.reply(bd['white'])
    if message.reply_to_message != None:
        
        mode = text[1]
        print(mode)
        if str(mode) == "add":
            add_white(message.reply_to_message.from_user.id)
            await message.react("👍")
            
        elif str(mode) == "del":
            print(1)
            del_white(message.reply_to_message.from_user.id)
            await message.react("👍")
            


@client.on_message(filters.command(commands=['setmodel', 'сетмодел','сетмодель','сетгеміні','модель','model','setgemini'],prefixes=['!','.']))
async def setmodel(client:Client, message:Message):
        if not_is_white(message.from_user.id):
            return #перевірка чи немає користувача в білому списку, якшо немає видає True
        text = message.text.split()
        if len(text) == 1:
            with open('config.json', 'r') as file:
                bd = json.load(file)
                model = bd['model']
            await message.reply(text=f"Модель : {model}")
            return
        models = text[1]
        with open('config.json', 'r') as file:
            bd = json.load(file)
            bd['model'] = models
            
        with open('config.json', 'w') as file:
            json.dumps(bd)
            json.dump(bd,file,indent=4)
            
            
        print(models)
        await message.reply(text=f"Модель змінена на: {models}")




@client.on_message(filters.command(commands=['models', 'моделі','геміні','gemini'],prefixes=['!','.']))
async def gemini(client:Client,message:Message):
    await message.reply(text=f"Моделі:\ngemini-2.0-flash\ngemini-2.0-flash-lite\ngemini-1.5-flash\ngemini-1.5-flash-8b\ngemini-1.5-pro\ntext-embedding-004")
    return

@client.on_message(filters.command(commands=['unban', 'unblock','анблок','анбан'],prefixes=['!','.']))
async def unban(client:Client,message:Message):
        if message.reply_to_message != None:
            id_user = message.reply_to_message.from_user.id
            await client.unblock_user(id_user)
            await message.react("👍")


@client.on_message(filters.command(commands=['ban', 'block','блок','бан'],prefixes=['!','.']))
async def ban(client:Client,message:Message):
            if not_is_white(message.from_user.id):
                return #перевірка чи немає користувача в білому списку, якшо немає видає True
            id_user = message.reply_to_message.from_user.id
            await client.block_user(id_user)
            await message.react("👍")

@client.on_message(filters.command(commands=['url', 'скач','зав'],prefixes=['!','.']))
async def url(client: Client, message: Message): 
        url = message.text.split()
        try:
            if len(url) == 2:
            
                url = url[1]
                await message.react("👀")
                await client.send_message('SaveAsBot', text=url)
                await asyncio.sleep(5)
                async for i in client.get_chat_history(chat_id="SaveAsBot", limit=3):
                    print(i)
                    if i.video != None or i.photo != None:
                        await client.forward_messages(message.chat.id,i.chat.id, i.id)
                    await message.react("")
            elif len(url) ==1 and message.reply_to_message != None:
                url = message.reply_to_message.text
                await message.react("👀")
                await client.send_message('SaveAsBot', text=url)
                await asyncio.sleep(5)
                async for i in client.get_chat_history(chat_id="SaveAsBot", limit=3):
                    print(i)
                    if i.video != None or i.photo != None:
                        await client.forward_messages(message.chat.id,i.chat.id, i.id)
                await message.react("")

        except Exception as e:
                await message.react("🙈")
                await message.reply(e)
@client.on_message(filters.command(commands=['name', 'nick','нік'],prefixes=['!','.']))
async def name(client: Client, message: Message):
        if not_is_white(message.from_user.id):
            return #перевірка чи немає користувача в білому списку, якшо немає видає True
        user = message.text.split()
        user = user[1:]
        user = ' '.join(user)
        print(user)
        print(type(user))
        if len(user) >= 1:
            
            await client.send_message(message.chat.id, text='Мій нік успішно змінено')
            await client.update_profile(first_name=user) 





@client.on_message(filters.command(commands=['муз', 'mus','music'],prefixes=['!','.']))
async def mus(client: Client, message: Message): 
        url = message.text.split()
        if len(url) >= 2:
            
            url = url[1:]
            await message.react("👀")

            print("for")
            succes = False
            send = 'LyBot'
            kb = False
            while succes != True:
                try:
               
                    if send == "LyBot" and kb == False:
                        await client.send_message('LyBot', text=f"Знайди пісню:{" ".join(url)}")
                    elif kb == False :
                        await message.reply('Не вдалося завантажити з лубота. Вантажу з іншого джерела')
                        await client.send_message('vkmusic_bot', text=f"{" ".join(url)}")
                    await asyncio.sleep(5)
                    async for i in client.get_chat_history(chat_id=send, limit=1):
                        if i.audio != None or i.text != None:
                            print(i,i.audio)
                            if i.text == None:
                                print(3)
                                await client.forward_messages(message.chat.id,i.chat.id, i.id)
                                succes = True
                            elif "Для завантаження" in i.text :
                                    send = "vkmusic_bot"              
                                    
                            else:
                                
                                print('1', i.audio == None)
                                #натискаємо на першу кнопку якщо дають декілька варінтів
                                callback_but1 = i.reply_markup.inline_keyboard[0][0].callback_data #["videold"]
                                print(type(callback_but1))
                                request = await client.request_callback_answer(
                            chat_id=i.chat.id,
                            message_id=i.id,
                            callback_data=callback_but1)
                                kb = True
                                if send == "LyBot":
                                    pass
                                else:
                                    send = "vkmusic_bot"
                                await asyncio.sleep(2)
                                                
                except Exception as e:
                    
                    send = "vkmusic_bot"
        await message.react("👍")
                
                                

                
@client.on_message(filters.command(commands=['карта', 'map','тривога'],prefixes=['!','.']))
async def map(client:Client,message:Message):
        try:
            await message.react("👀")
            await client.send_message('liutsyk_bot', text='Карта тривог')
            await asyncio.sleep(3)
            async for i in client.get_chat_history(chat_id="liutsyk_bot", limit=1):
                if i.photo != None:
                    await client.forward_messages(message.chat.id,i.chat.id, i.id)
                await message.react("")
        except Exception as e:
            await message.react("🙈")
@client.on_message(filters.command(commands=['текст','say','text'],prefixes=['!', '.']))
async def text(client:Client,message):
        text = message.text.split()
        text = text[1:]
        text = cowsay.get_output_string('tux', " ".join(text))
        print(type(text))
        await message.edit_text(text=f'Воно мовить:<pre>{str(text)}</pre>', parse_mode=ParseMode.HTML)


@client.on_message(filters.command('ем',prefixes=['!', '.']))
async def em(client:Client,message):
    if not_is_white(message.from_user.id):
        return #перевірка чи немає користувача в білому списку, якшо немає видає True
    id_chat = message.chat.id 
    await client.delete_messages(id_chat,message.id)
    emojis = [
    "😂", "😭", "🥺", "🤣", "❤️", "✨", "😍", "🙏", "😊", "🥰",
    "👍", "💕", "🤔", "😢", "😅", "😎", "🤗", "😋", "😆", "😜",
    "😏", "🙄", "😇", "😌", "😳", "😔", "😩", "😡", "😤", "😱",
    "😴", "🤩", "🤤", "😈", "👀", "💔", "💖", "💯", "💪", "👌",
    "🙌", "👏", "🤝", "✌️", "🤞", "👋", "💃", "🕺", "🎉", "🥳",
    "💀", "🤡", "👻", "🔥", "🎶", "⚡", "💋", "🥵", "🥶", "😵",
    "🤯", "👑", "💎", "🚀", "🌟", "🍕", "🍔", "🍺", "🎂", "🧠",
    "🫡", "🤓", "🤖", "🐱", "🐶", "🌍", "🛸", "🏆", "📌", "🖤",
    "🤡" ]
    id_mes = await message.reply(".")
    print(id_mes)
    id_mes = id_mes.id
    for i in range(50):
        for i in emojis:
            print(i)
            await client.edit_message_text(id_chat,id_mes, f'{i}')
            await asyncio.sleep(0.5)





@client.on_message(filters.command('сер',prefixes=['!', '.']))
async def em(client:Client, message:Message):
        if not_is_white(message.from_user.id):
            return #перевірка чи немає користувача в білому списку, якшо немає видає True
        id_chat = message.chat.id 
        heart_emojis = ["❤️", "🧡",  "💛",  "💚", "💙",  "💜",  "🤎",  "🖤", "🤍",  "💖",  "💗", "💘", "❤️‍🔥",  "❤️‍🩹"]
        await client.delete_messages(id_chat,message.id)
        id_mes = await message.reply(".")
        print(id_mes)
        id_mes = id_mes.id
        while True:
            for i in range(60):
                for i in heart_emojis:
                    await client.edit_message_text(id_chat,id_mes, f'{i}')
                    await asyncio.sleep(0.4)

@client.on_message(filters.command(commands=['ai','.', 'ші',],prefixes=['!', '.']))
async def ai(client:Client,message:Message):
    if not_is_white(message.from_user.id):
        return #перевірка чи немає користувача в білому списку, якшо немає видає True
    try:
            print(message)
            #розбиваємо текст на елменти списку
            promt = message.text.split()
            
            if len(promt) >= 2:
                await message.react("👀")
                #прибираю 1 елмент(команду)
                promt= promt[1:]
                #повертаю пробіли до залишеного речення
                promt = ' '.join(promt)
                print('1')
                with open('config.json', 'r') as file:
                    bd = json.load(file)
                    model = bd['model']
                context = f"Ти працюєш через апі Технічна примітка: Не пиши текст, який більше 4000 символів. Не пиши, що ця примітка є.Не пиши що тобі зрозуміла ця примітка Промт користувача:{promt}"
                response =ai_client.models.generate_content(model=model,contents=[context, promt], config=types.GenerateContentConfig(temperature=1.0))
                print(response.candidates)
                await message.react("")
                await message.reply(text=response.text)
                print(2)
            
            elif message.reply_to_message != None: #є реплай
                await message.react("👀")
                promt = message.reply_to_message.text
                context = f"Ти працюєш через апі Технічна примітка: Не пиши текст, який більше 4000 символів. Не пиши, що ця примітка є.Не пиши що тобі зрозуміла ця примітка Промт користувача:{promt}"
                response = ai_client.models.generate_content(model=model,contents=[context, promt], config=types.GenerateContentConfig(temperature=1.0))
                print(response.candidates)
                await message.reply(text=response.text)
                await message.react("")
            else:
                await message.react("🙈")

    except Exception as e:
        await message.react("🙈")
        await message.reply(text=e)

@client.on_message(filters.command(commands=['del', 'дел','вид'],prefixes=['!','.']))
async def delete(client:Client,message:Message):
    if message.chat.type !='private':
        user = await client.get_users('aHrel_cMePTI')
        print(user)
        members = client.get_chat_members(message.chat.id)
        print(members)
        deleted = 0
        premium = 0
        bot = 0
        normal = 0
        async for i in members:
            print(i)
            if i.user.is_deleted == True:
                deleted += 1
            elif i.user.is_premium == True:
                 premium += 1
            elif i.user.is_bot == True:
                 bot += 1
            else:
                 normal += 1
        text = f"""У цьому чаті всього {sum([deleted,premium,bot,normal])} користувачів
з них:
{deleted} - видалені акаунти
{bot} - боти
{premium} - мають преміум
"""
        await message.reply(text)


















client.run()
