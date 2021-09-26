from selenium import webdriver
# from selenium.common import exceptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
import os
import random
import json
from datetime import datetime, timedelta
import asyncio
import string

import discord
from discord.ext import commands
from discord.ext.commands import errors
from discord.ext.commands.core import has_permissions
import discord.utils

import dotenv
dotenv.load_dotenv()

# https://discord.com/api/oauth2/authorize?client_id=831875019071291433&permissions=8&scope=bot

def DOK(content):
    print(f"\033[92m[{datetime.now().strftime('%Y %b.%d %H:%M:%S')}] {content}\033[0m")
def DINFO(content):
    print(f"\033[93m[{datetime.now().strftime('%Y %b.%d %H:%M:%S')}] {content}\033[0m")
def DERROR(content):
    print(f"\033[91m[{datetime.now().strftime('%Y %b.%d %H:%M:%S')}] {content}\033[0m")

class C:
    OK = '\033[92m'
    INFO = '\033[93m'
    ERROR = '\033[91m'

    DOK = '\033[92m' + f"[{datetime.now().strftime('%Y %b.%d %H:%M:%S')}] "
    DINFO = '\033[93m' + f"[{datetime.now().strftime('%Y %b.%d %H:%M:%S')}] "
    DERROR = '\033[91m' + f"[{datetime.now().strftime('%Y %b.%d %H:%M:%S')}] "

    END = '\033[0m'

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def get_quote(method, message, caption, dl_path):
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2) # 0 means to download to the desktop, 1 means to download to the default "Downloads" directory, 2 means to use the directory
    fp.set_preference("browser.helperApps.alwaysAsk.force", False)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", dl_path)
    # fp.set_preference("browser.download.dir", os.getcwd())
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/download')
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/plain,text/csv,application/csv,application/vnd.ms-excel,text/comma-separat‌​ed-values,application/excel,application/octet-stream')
    fp.set_preference("browser.helperApps.neverAsk.openFile", "image/png, text/html, image/tiff, text/csv, application/zip, application/octet-stream")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png, text/html, image/tiff, text/csv, application/zip, application/octet-stream")

    options = Options()
    options.headless = True

    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    driver = webdriver.Firefox(capabilities=firefox_capabilities, firefox_profile = fp, options=options) #firefox_binary=binary

    link = "https://quotescover.com/tools/online-quotes-maker"
    driver.get(link)

    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)

    DOK(f"Webdriver page loaded")

    driver.execute_script("window.scrollTo(0, 1500);")

    main = driver.find_element_by_xpath('//textarea[@id="inputMainTextUtama"]')
    main.clear()
    main.send_keys(message)

    await asyncio.sleep(0.5)

    name = driver.find_element_by_xpath('//textarea[@id="inputSecondText"]')
    name.clear()
    name.send_keys(caption)

    await asyncio.sleep(0.5)
    tab = driver.find_element_by_xpath('//li[@id="tabText1"]')
    tab.click()

    await asyncio.sleep(0.5)
    quotes = driver.find_element_by_xpath('//button[@id="quotesMark-0"]')
    quotes.click()

    await asyncio.sleep(0.5)
    DINFO(f"Method : {method}")
    if method == "screen":
        path = dl_path + "/screenshot.png"
        driver.find_element_by_xpath('//div[@id="image-offset"]').screenshot(path)
        # driver.get_screenshot_as_file("screenshot.png")
    else:
        dl = driver.find_element_by_xpath('//button[@class="button openDownload buttonDownload"]')
        dl.click()

        await asyncio.sleep(random.randint(20,21))
        png = driver.find_element_by_xpath('//button[@data-pic="png2"]')
        png.click()

        now = datetime.now()
        filename = f"{now.year}_{now.month:02d}_{now.day:02d}_{now.hour:02d}_{now.min:02d}_{now.second:02d}_{caption.lower().split(' ~ ')[0]}"
        valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in filename if c in valid_chars).replace('-','_').replace(' ','_')
        filenamebox = driver.find_element_by_xpath('//input[@value="Your-Custom-Beautiful-Quotes-Here"]')
        filenamebox.clear()
        filenamebox.send_keys(filename)

        await asyncio.sleep(0.5)
        png2 = driver.find_element_by_xpath('//button[@class=" defaultHidden dlButton-2 button designButton save_image_locally"]')
        png2.click()

        await asyncio.sleep(1)
        path = f"{dl_path}/{filename}.png"
        path = path.replace('//','/');
        DINFO(f"File exists : {os.path.exists(path)}")

    driver.quit()
    return path


async def reaction_to_quote(payload):
    pinuser = bot.get_user(payload.user_id)
    if pinuser.bot or payload.guild_id == None: return # Bot ou Réaction en MP

    react = payload.emoji
    guild_data = await load_guild(payload.guild_id) # Load guild_data

    if str(react) == guild_data['emoji']:
        guild = discord.utils.get(bot.guilds, id=payload.guild_id)
    else: return

    try:
        message_channel = discord.utils.get(guild.text_channels, id=payload.channel_id)
        message =  await message_channel.fetch_message(payload.message_id)
        message_content = message.content
        author = message.author
        if author.id == bot.user.id:
            await message.remove_reaction(guild_data['emoji'], pinuser)
            return
    except Exception as e:
        DERROR(f"Unknown error {e}")
        return

    reactions = message.reactions
    for react in reactions:
        if bot.user in await react.users().flatten():
            DINFO(f"Le message a déjà été cité")
            return

    DOK(f"New quote")

    channel = False
    if 'channel' in guild_data and guild_data['channel']:
        channel = bot.get_channel(guild_data['channel'])
    if not channel:
        channel = message_channel

    DINFO(f"Message length : {len(message_content)}")
    if len(message_content) == 0:
        DERROR(f"Message vide")
        await channel.send("Ce message est vide, et ne peut pas être quote")
        return
    if len(message_content) > 500:
        DERROR(f"Message trop long")
        await channel.send("Ce message est trop long pour être quote")
        return

    # if str(pinuser.id) in guild_data['users_timeout'] and datetime.now() < datetime.strptime(guild_data['users_timeout'][str(pinuser.id)], "%m/%d/%Y, %H:%M:%S"):
    #     waitingTime = datetime.strptime(guild_data['users_timeout'][str(pinuser.id)], "%m/%d/%Y, %H:%M:%S") - datetime.now()
    # await channel.send(f"{pinuser.mention}, tu ne peux pas pin de messages avant {int(waitingTime.seconds/3600)}h{int(waitingTime.seconds/60)%60}m !", delete_after=10)
    # await message.remove_reaction(guild_data['emoji'], pinuser)
    # return

    confirmation_content = f"""{pinuser.mention}, es tu sûr de vouloir quote ```markdown\n{message_content}```de {author.mention} ?"""
    #\nTu pourra pin à nouveau dans 20h
    try:
        await pinuser.create_dm()
    except Exception as e:
        DERROR(f"DM channel with {pinuser.mention} cannot be created")
        await channel.send(f"{pinuser.mention} Merci d'autoriser les mps avec le serveur, pour utiliser le bot", delete_after=5)
        return
    try:
        confirmation = await pinuser.dm_channel.send(confirmation_content)
    except Exception as e:
        DERROR(f"Cannot DM {pinuser.mention}")
        await channel.send(f"{pinuser.mention} Impossible de t'envoyer un mp ...", delete_after=5)
        return

    await confirmation.add_reaction("☑️")
    await confirmation.add_reaction("❎")

    def check(reaction, user):
        if user.id == bot.user.id:
            return
        DINFO(f"Reaction {reaction} - {user}")
        return (str(reaction.emoji) == "☑️" or str(reaction.emoji) == "❎") and reaction.message.id == confirmation.id and user.id == pinuser.id

    try:
        react, user = await bot.wait_for('reaction_add', check = check, timeout=30)
        if str(react) == "❎":
            DERROR(f"Cancelled by user")
            await confirmation.edit(content = confirmation_content + f"\n*Annulé par {pinuser.mention}.*")
            # await confirmation.edit(delete_after=10)
            await message.remove_reaction(guild_data['emoji'], pinuser)
            return
    except asyncio.exceptions.TimeoutError:
        DERROR(f"Cancelled by Timeout")
        await confirmation.edit(content = confirmation_content + f"\n*Annulé par Timeout.*")
        await message.remove_reaction(guild_data['emoji'], pinuser)
    except Exception as e:
        DERROR(f"Unknow error {e}")
        await confirmation.edit(content = confirmation_content + f"\n*Annulé par Timeout.*")
        # await confirmation.edit(delete_after=10)
        await message.remove_reaction(guild_data['emoji'], pinuser)
        return

    await confirmation.edit(content = confirmation_content + f"\n<a:loading:809405677297729547> *Génération de la citation, ceci peut prendre jusqu'à 30 secondes*")
    DINFO(f"dl_path\t\t{dl_path}")

    DINFO(f"Message content\t{message_content}")
    caption = f"{author.display_name} ~ {message.created_at.day:02d}/{message.created_at.month:02d}/{message.created_at.year} {message.created_at.hour:02d}:{message.created_at.minute:02d}"
    DINFO(f"Caption\t\t{caption}")

    filepath = await get_quote("button download", message_content, caption, dl_path)
    DOK(f"File saved at {filepath}")

    fp =  discord.File(filepath)

    msg = random.choice(msgs).format(user.mention, author.mention)
    DINFO(f"Random message : {msg}")

    embed = discord.Embed(description = msg + f"\n[pin]({message.jump_url})")
    # embed.set_footer(text="Quotes", icon_url=bot.user.avatar_url)
    try:
        file_message = await channel.send(embed = embed, file = fp)
        # file_message = await channel.send(content = msg, file = fp)
    except Exception as e:
        DERROR(f"Erreur innatendue : {e}")
        await confirmation.edit(content = confirmation.content + f"\nErreur innatendue. Impossible d'envoyer le message")
        await message.remove_reaction(guild_data['emoji'], pinuser)
        return
    else:
        # guild_data['users_timeout'][str(pinuser.id)] = (datetime.now() + timedelta(hours=20)).strftime("%m/%d/%Y, %H:%M:%S")
        await save_guild(payload.guild_id, guild_data)
        # await confirmation.delete()
        await message.add_reaction(guild_data['emoji'])
        await confirmation.edit(content = confirmation.content + f"\n{file_message.jump_url}")


TOKEN = os.getenv("TOKEN")
if not TOKEN:
    DERROR(f"Token couldnt be loaded")
    exit()

pwd = os.path.dirname(os.path.abspath(__file__))
dl_path = pwd + "/quotes"
guilds_path = pwd + "/guilds"
if not os.path.exists(dl_path):
    os.mkdir(dl_path)
    DINFO(f"dl_path {dl_path} has been created")

if not os.path.exists(guilds_path):
    os.mkdir(guilds_path)
    DINFO(f"guilds_path {guilds_path} has been created")

# print(intents)
# for intent in intents:
#     print(intent)
# intents.guild_emojis = True

prefixes_path = pwd + "/prefixes.json"
if os.path.exists(prefixes_path):
    with open(prefixes_path, "r") as fo:
        try:
            custom_prefixes = json.load(fo)
        except Exception as e:
            DERROR(f"Erreur innatendue {e}")
            DINFO(f"Couldn't load custom_prefixes")
            custom_prefixes = {}
else:
    custom_prefixes = {}

default_prefixes = ['.']

async def determine_prefix(bot, message):
    guild = message.guild
    #Only allow custom prefixs in guild
    if guild:
        return custom_prefixes.get(guild.id, default_prefixes)
    else:
        return default_prefixes

intents = discord.Intents.all()
bot = commands.Bot(intents = intents, command_prefix = determine_prefix, help_command=None)
# client = discord.Client(intents = intents)

msgs = [
   "{} a décidé d'afficher {}",
   "Hop, {} n'a pas manqué {}",
   "{} a gravé à jamais la bêtise de {}",
   "{} a mis en lumière le <:BigBrain:825476978097389589> de {}",
   "En accord avec {}, {} nous montre le chemin du savoir ...",
   "Mis en avant par {}, écoutons ensemble ce que {} a à nous partager :"
]


@bot.command(name="custom_quote", description="Create a custom quote")
async def custom_quote(ctx, *arguments):
    DOK(f"Custom quote by {ctx.author}")
    arguments = " ".join(arguments)
    DINFO(f"Message : {arguments}")
    if "| " in arguments:
        message_content = arguments.split("|")[0].strip()
        caption = arguments.split("|")[1].strip()
    else:
        DINFO(f"Le message ne contient pas de caption")
        message_content = arguments.split("|")[0].strip()
        caption =""
    if len(message_content) == 0:
        await ctx.send("Mauvais arguments.\nExemple d'utilisation : `.custom_quote La vie n'est pas un long fleuve tranquille | Jean ~ 12/03/2021` ou `.custom_quote uwu`")
        return
    elif len(message_content) > 500:
        await ctx.send("Message trop long pour être cité :(")
        return

    guild_data = await load_guild(ctx.guild.id)
    channel = False
    if 'channel' in guild_data and guild_data['channel']:
        channel = bot.get_channel(guild_data['channel'])
    if not channel:
        channel = ctx.channel

    # await bot.add_reaction(ctx.message, "a:loading:809405677297729547")
    # await ctx.message.add_reaction("a:loading:809405677297729547")
    await ctx.message.add_reaction("<a:loading:809405677297729547>")
    # emoji = discord.utils.get(bot.get_all_emojis(), name='loading')
    # await bot.add_reaction(ctx.message, emoji)
    # loading = bot.get_emoji(809405677297729547)
    # await ctx.message.add_reaction(loading)
    filepath = await get_quote("button download", message_content, caption, dl_path)
    DOK(f"filepath : {filepath}")

    fp =  discord.File(filepath)
    msg = f"Citation faite par {ctx.author.mention}"
    file_message = await ctx.channel.send(content = msg, file = fp)
    await ctx.message.delete()



@bot.event
async def on_ready():
    DINFO(f"{bot.user} has connected to Discord!")
    game = discord.Game(f".help | {len(bot.guilds)}")
    await bot.change_presence(status=discord.Status.online, activity=game)

async def on_guild_join(self, guild):
    DOK(f"==========")
    DOK(f"New guild")
    DOK(f"{guild.name}")
    DOK(f"==========")
    game = discord.Game(f".help | {len(bot.guilds)}")
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command(name = "set_prefix", description = "Switch from '.' prefix to a custom one.")
@has_permissions(administrator=True)
@commands.guild_only()
async def set_prefix(ctx, prefix):
    prefix = prefix.split(" ")[0]
    if len(prefix) > 10:
        await ctx.send("Le préfixe est trop long. Merci d'en choisir plus court")
        return
    custom_prefixes[ctx.guild.id] = prefix or default_prefixes

    # Save custom_prefixes
    with open(prefixes_path, "w") as fw:
        json.dump(custom_prefixes, fw, indent=2)
    await ctx.send(f"Préfixe changé en {prefix}!")
    DINFO(f"{ctx.guild.name} | {ctx.guild.id} \t| Nouveau préfixe {custom_prefixes[ctx.guild.id]}")


@bot.event
async def on_raw_reaction_add(payload):
    await reaction_to_quote(payload)
    return


@bot.command(name = "set_quote_channel", description="Set channel where all quotes will be sent")
async def set_quote_channel(ctx, argument):
    try:
        channel = await commands.TextChannelConverter().convert(ctx, argument)
    except errors.ChannelNotFound:
        await ctx.send(f"Soit ce n'est pas un channel, soit il est introuvable (merci d'essayer un autre channel)")
        return
    except Exception as e:
        await ctx.send("Erreur innatendue")
        return

    if channel.guild != ctx.guild:
        await ctx.send(f"Le channel {channel.mention} n'appartient pas à cette guilde.")
        return

    bot_member = await ctx.guild.fetch_member(bot.user.id)
    if not bot_member.permissions_in(channel).send_messages:
        await ctx.send(f"Le bot ne peut pas envoyer de message dans le channel {channel.mention}")
        return

    guild_data = await load_guild(ctx.guild.id)
    guild_data['channel'] = channel.id
    await save_guild(ctx.guild.id, guild_data)

    await ctx.send(f"Les citations seront envoyés dans {channel.mention}")
    DINFO(f"{ctx.guild.name} | {ctx.guild.id} \t| Channel choisi: {channel} - {channel.id}")


@bot.command(name = "set_quote_reaction", description="Set emoji that will quote messages")
async def set_quote_reaction(ctx, argument:discord.Emoji):
    try:
        emoji = await commands.EmojiConverter().convert(ctx, argument)
    except errors.EmojiNotFound:
        await ctx.send(f"Soit ce n'est pas un émoji, soit il est introuvable (merci d'essayer un autre)")
        return
    except Exception as e:
        await ctx.send("Erreur inattendue")
        DERROR(f"Unknow error : {e}")
        return

    # print(emoji)
    # print(emoji.animated)
    # print(emoji.available)
    # print(emoji.created_at)
    # print(emoji.guild)
    # print(emoji.guild_id)
    # print(emoji.id)
    # print(emoji.managed) #twitch integration
    # print(emoji.name)
    # print(emoji.require_colons) #in client
    # print(emoji.roles)
    # print(emoji.url)
    # print(emoji.user)
    # print(emoji.is_usable())
    # print(emoji.url_as())
    if not emoji.guild == ctx.guild: # emoji.is_usable() or not
        await ctx.send("L'émoji doit provenir de cette guild")
        return

    guild_data = await load_guild(ctx.guild.id)
    guild_data['emoji'] = str(emoji)
    await save_guild(ctx.guild.id, guild_data)

    await ctx.send(f"{emoji} a été choisi comme réaction de citation")
    DINFO(f"{ctx.guild.name} | {ctx.guild.id} \t| Reaction choisie pour {emoji.name} - {emoji.id}")


async def load_guild(guild_id):
    global guilds_path
    if f"{guild_id}.json" in os.listdir(guilds_path):
        path =  f"{guilds_path}/{guild_id}.json"

        with open(path, "r") as fo:
            try:
                guild_data = json.load(fo)
            except Exception as e:
                DERROR(f"{guild_id} : guild_data unreadable")
            else:
                if not 'guild_id' in guild_data or guild_data['guild_id'] != guild_id:
                    DERROR(f"{guild_id} : guild_data incorrect")
                else:
                    return guild_data

    guild_data = {
        'guild_id': guild_id,
        'emoji': False,
        'channel': False,
        'messages_customs': [],
        'disable_base_messages': False
        # 'users_timeout': {}
    }

    await save_guild(guild_id, guild_data)
    DINFO(f"New guild file created : {guild_id}")
    return guild_data

async def save_guild(guild_id, guild_data):
    global guilds_path
    path =  f"{guilds_path}/{guild_id}.json"

    with open(path, "w") as fw:
        json.dump(guild_data, fw, indent=2)


@bot.command()
async def help(ctx):

    embed = discord.Embed(title = "**Quotes - Help**", description = f"""**Fonctionnement**
    Une réaction doit être set via la commande `{prefix}set_quote_reaction` pour permettre au bot de quote des messages.
    Une quote avec le contenu du message et la caption *"Autheur ~ Date Heure"* sera généré en moins de 30 secondes
    La quote sera envoyé sous format image sur discord, dans le channel choisi via la commande `{prefix}set_quote_channel` ou sinon dans le channel du message originel.
    Une quote peut être générée par un membre toute les 20h.\n""", color=0x29c87e)
    embed.timestamp = datetime.utcnow()
    try:
        embed.set_footer(text="Quotes", icon_url=bot.user.avatar_url)
    except Exception as e:
        DINFO(f"avatar url get failed")

    embed.add_field(name = f"**❯** `{prefix}set_quote_reaction <reaction>`", value = "Changer la réaction des quotes", inline=True)
    embed.add_field(name = f"**❯** `{prefix}set_quote_channel <#text_channel>`", value = "Changer le channel des quotes", inline=True)
    embed.add_field(name = f"**❯** `{prefix}set_prefix <prefix>`", value = "Changer le préfixe", inline=True)

    guild_data = await load_guild(ctx.guild.id)
    embed.add_field(name = " ‎", value = f"Prefix : {custom_prefixes[ctx.guild.id] if ctx.guild.id in custom_prefixes else default_prefixes} - Reaction : {guild_data['emoji']} - Channel : <#{guild_data['channel']}>")

    # content = f"""
    # **❯** `{prefix}set_quote_reaction <reaction>` - Pour changer la réaction des quotes
    # **❯** `{prefix}set_quote_channel <#text_channel>` - Pour changer le channel des quotes
    # **❯** `{prefix}set_prefix <prefix>` - Pour changer le préfixe.
    # ** -- Fonctionnement -- **
    # Une réaction doit être set via la commande `{prefix}set_quote_reaction` pour permettre au bot de quote des messages.
    # Une quote avec le contenu du message et la caption "Autheur ~ Date Heure" sera généré en moins de 30 secondes
    # La quote sera envoyé sous format image sur discord, dans le channel choisi via la commande `{prefix}set_quote_channel` ou sinon dans le channel du message originel.
    # Une quote peut être générée par un membre toute les 20h.
    # """
    # await ctx.send(content = content)
    await ctx.send(embed = embed)


bot.run(TOKEN)