# version 0.1.1
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord.utils import get
from datetime import datetime, timedelta
from time import mktime
import json #json used for settings file
import asyncio #required for asyncio.TimeoutError in checkword command
import signal # save files when receiving KeyboardInterrupt
import sys # exit program after Keyboardinterrupt signal is notices
import threading # for running clockQuestionEvent(); a function to say the Question of the Day, every day at a certain time.

import requests #for sending a custom thread creation request
async def create_thread(self,name,auto_archive_duration,message):
    print("Creating thread...")
    token = 'Bot ' + self._state.http.token
    url = f"https://discord.com/api/v9/channels/{self.id}/messages/{message.id}/threads"
    headers = {
        "authorization" : token,
        "content-type" : "application/json"}
    data = {
        "name" : name,
        "type" : 11,
        "auto_archive_duration" : auto_archive_duration}
    response = requests.post(url,headers=headers,json=data).json()
    return response
discord.TextChannel.create_thread = create_thread

#setup default discord bot client settings, permissions, slash commands, and file paths
intents = discord.Intents.default()
client =  commands.AutoShardedBot(shard_count=2,shard_id=1, intents = intents
, command_prefix=commands.when_mentioned_or("/"), case_insensitive=True
, activity = discord.Game(name="with slash (/) commands!"))
slash = SlashCommand(client, sync_commands=True)
path = ""   #"C:Users\\[........]\\MiaBot\\version 0.1.1\\"

#default defining before settings
astronomyWords = []
settings = {}
qotds = []
qotdEmbed = 0
defaultSettings = {
    'msgCount':0,
    'limit':20,
    'timeOfLastMsg': mktime(datetime.now().timetuple()),
    'threadCount':0,
    'timeSinceMention':0
}

@client.event
async def on_ready():
    global astronomyWords, settings, qotds
    #try to join #MiaBot channel
    print("Logged in as {0.user}".format(client,end="   "))
    #load astronomyWords [] file, split the string at every comma and ensure that it follows the correct format
    # space,astronomy,saturn,jupiter,antenna,satellite,radio,telescope
    words = open(path+"astronomyWords.txt","r").read().split(",")
    for x in words:
        x = x.lower().strip()
        if x not in astronomyWords:
            astronomyWords.append(x)
    #Load settings file for all guilds.
    if len(settings) == 0:
        settings = json.loads(open('settings.json',"r").read())
    if len(qotds) == 0:
        qotds = json.loads(open('qotds.json',"r").read())


@client.event
async def on_message(message):
    global settings, qotdEmbed, qotds
    try: #check if a user has a nickname: yes? use that for the print log statements
        userName = message.author.nick
        if userName == None:
            raise AttributeError
    except AttributeError:
        userName = message.author.name

    #check if the guild of the message is in the settings
    try:
        settings[str(message.guild.id)]
    except:
        if len(settings) == 0:
            #await ctx.send("You can't add a word because the file is too short! Something probably went wrong when loading the file.\nChanging a setting now will overwrite and clear it (try again in a few seconds)")
            print("Did not set default settings because the dictionary is 0, so unloaded")
            return
        settings[str(message.guild.id)] = defaultSettings
    print(f"{settings[str(message.guild.id)]['msgCount']+1} | {datetime.now().strftime('%H:%M')} | {message.channel.name} | {userName}:\t{message.content}")

    #check if message was sent by the bot; if yes, ignore the rest
    if message.author.bot:
        return

    if qotdEmbed != 0: #Say message if time has passed
    #939488789984841738
        print("sending...")
        await client.get_channel(829356293206310926).send("<@&934862221165617250>",embed=qotdEmbed)
        print("sent!")
        qotdEmbed = 0
        del qotds[0]

    #some custom commands
    if message.content.startswith(":say "):
        await message.channel.send(message.content.split(" ",1)[1].replace("[[del]]",""),delete_after=64)
        return
    if message.content.startswith(":kill"): #kill switch if ever something goes wrong and I'm not online to help
        await message.add_reaction("💀")
        signal_handler(None,None)
    if "\s" in message.content.lower():
        sendable = False
        if not ((message.content.startswith("$") and message.content.startswith("$")) or message.startswith(",text")):
            #    convert "hello there, how are you \s" into "hElLo tHeRe, HoW ArE YoU"
            # convert "hello \sthere\s"
            def swap(message, sendable):
                try:
                    start = message.content.index("\s")
                    end = message.content.index("\s", start+1)
                    if end-start > 2:
                        sendable = True
                        section = message.content[start+2:end]
                        section = ''.join([section[x].lower() if x%2 == 0 else section[x].upper() for x in range(len(section))])
                        message.content = message.content[:start] + section + message.content[end+2:]
                        return swap(message), sendable

                    else:
                        return 0
                except:
                    return message.content, sendable
            ans, sendable = swap(message, sendable)
            if ans == 0:
                await message.channel.send("That's too short!", delete_after=8)
            elif message.content.endswith("\s"):
                if len(message.content) < 3:
                    await message.channel.send("I can't really do much with an empty message, dumdum",delete_after=8)
                else:
                    sponge = ''.join([message.content[x].lower() if x%2 == 0 else message.content[x].upper() for x in range(len(message.content))])
                    sponge = await message.channel.send(sponge[:-2])
                    await sponge.edit(content="<@"+str(message.author.id)+">: "+sponge.content)
            else:
                if sendable:
                    sponge = await message.channel.send(ans)
                    await sponge.edit(content="<@"+str(message.author.id)+">: "+sponge.content)
    if message.content.startswith(":thread"):
        thread = client.get_guild(934862221165617242).get_thread(936791587101487164)
        await thread.join()
        await thread.send("hello    ")



    if "miabot" in  message.content.lower():
        if settings[str(message.guild.id)]["timeSinceMention"] > 50:
            await message.channel.send("Do I hear my name? o_O",delete_after=4)
            settings[str(message.guild.id)]["timeSinceMention"] = 0
    settings[str(message.guild.id)]["timeSinceMention"] += 1

    #check if picture was sent in #deep-space or #lunar-planetary ;; Astrophotography channels. Then react star
    if message.channel.id in [934862222667182093,936758514527924284] and message.attachments:
        try:
            await message.add_reaction("⭐")
        except discord.errors.Forbidden:
            pass #1) no permission to add reactions to the message; or
            #2) already 20 emojis on the message (dunno how, since the message was sent only half a second ago)
    #if message sent in #introductions and contains a welcoming word, react wave
    if message.channel.id in [934862221895422051]:
        if any(x in message.content.lower() for x in "hello,hey,heya,howdy,i'm,hi,im,name,hiya,yo".split(",")):
            await message.add_reaction("👋")
            #await message.add_reaction("💫")
            return
    #if picture sent in #banner-icon-competition, add vote and potential thread emojis
    if message.channel.id in [938377129232597052] and message.attachments:
        await ctx.message.add_reaction("🔺")
        await ctx.message.add_reaction("🔻")
        await ctx.message.add_reaction("📰")

    #check if message was sent in #general-astro; if not, ignore the rest
    if message.channel.id != 934862222272901126: #this one is for The Sphere -> 829356293206310926:
        return
    #otherwise, if the most recent message contains an astronom-related word or was sent more than 10 minutes ago, reset the off-topic counter
    trigger = 0
    wordList = []
    for word in astronomyWords:
        if word in message.content:
            wordList.append(word)
    if len(wordList) > 0:
        trigger = "I found this word(s) ("+", ".join(wordList)+") in a message!"
    if mktime(datetime.now().timetuple()) - settings[str(message.guild.id)]["timeOfLastMsg"] > timedelta(minutes=10).total_seconds():
        trigger = "10 minutes passed"
    if trigger != 0:
        settings[str(message.guild.id)]["timeOfLastMsg"] = mktime(datetime.now().timetuple())
        print("Astronomy counter reset")
        message.channel = client.get_channel(829356293206310930) # !!! can only do this because there is a 'return' at the end of the if statement!!
        await message.channel.send("Message counter reset after "+str(settings[str(message.guild.id)]["msgCount"])+" messages: "+trigger+" (log channel pog? maybe)")
        settings[str(message.guild.id)]["msgCount"] = 0
        return
    #else, increase the off-topic counter, and set the most recen   t message's time to the current time.
    settings[str(message.guild.id)]["msgCount"] += 1
    settings[str(message.guild.id)]["timeOfLastMsg"] = mktime(datetime.now().timetuple())

    #if there are x messages without astronomy words, it will send a message and reset the off-topic counter variable
    if settings[str(message.guild.id)]["msgCount"] == settings[str(message.guild.id)]["limit"]:
        reply = await message.channel.send("""<a:offTopicAAA:938007837018325012> Is this conversation space related? If not, take it to <#934862222667182095>.
Do you think this is a mistake? Mention a staff member or Mia. Thank you for keeping the chat on-topic.""")
        await reply.add_reaction("❌")
        settings[str(message.guild.id)]["msgCount"] = 0
        message.channel = client.get_channel(829356293206310930) # !!! can only do this because there is a 'return' at the end of the if statement!!
        await message.channel.send("Sent off-topic notifier message.")


@client.event
async def on_raw_reaction_add(reaction):
    global settings
    #get the message id from reaction.message_id through the channel (with reaction.channel_id) (oof lengthy process)
    message = await client.get_channel(reaction.channel_id).fetch_message(reaction.message_id)

    #Create thread at message when someone (not bot) adds this emote
    if reaction.emoji.name == '📰' and reaction.member != client.user:
        if len(settings) == 0:
            await ctx.send("You can't start thread because the settings file is too short! Something probably went wrong when loading the file.\nChanging a setting now (to default settings) will overwrite and clear it (try again in a few seconds)")
            return
        try: #to give the thread a number, else add setting and reset thread number
            threadCount = settings[str(message.guild.id)]['threadCount']
        except:
            try:
                settings[str(message.guild.id)]['threadCount'] = 0
            except:
                settings[str(message.guild.id)] = defaultSettings
            threadCount = 0
        if message.attachments:
            type = " image "
        else: type = " message "
        data = await message.channel.create_thread(name="Thread for"+type+str(threadCount), message = message, auto_archive_duration=180)
        print(data)
        settings[str(message.guild.id)]['threadCount'] += 1

    #delete message if bot message is reacted to with ':x:'
    if reaction.emoji.name == '❌':
        if message.author == client.user:
            if message.content.startswith("<@!"):
                if not int(message.content.split(" ",1)[0][3:21]) == reaction.user_id or reaction.user_id == 262913789375021056:
                    return
            await message.delete()

@slash.slash(name="addword",description="Add a new word to the list of astronomy words. (seperate with commas)")
async def addWord(ctx, text):
    #only execute if user is staff or Mia
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        global astronomyWords
        if len(astronomyWords) < 5:
            await ctx.send("You can't add a word because the list is too short! Something probably went wrong when loading the list.\nAdding a word now will overwrite it and clear everything (can only be brought back from backups!)")
            return
        #suppose: "/addWord space, universe, star", split words at the comma, strip them, and make them lowercase
        #store variables that couldn't be added (in list already or less than 2 letters)
        invalid = []
        #ensure that multi-lined words do not keep their newline characters (if they could)
        wordList = text.replace("\n",",").split(",")
        for word in wordList:
            wordEdit = word.lower().strip()
            if len(word) < 3:
                invalid.append(wordEdit)
                wordList.remove(word)
            elif not word in astronomyWords:
                astronomyWords.append(wordEdit)
            else:
                invalid.append(wordEdit)
                wordList.remove(word)
        astronomyWords = sorted(astronomyWords)
        # print which words were added and which couldn't
        reply = []
        if len(wordList) > 0:
            reply.append("Successfully added: "+(', '.join(wordList))+"!")
        if len(invalid) > 0:
            reply.append(', '.join(invalid)+" could not be added (they are already in the list, or are too short).")
        reply = '\n'.join(reply)
        await ctx.send(reply, hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)
@slash.slash(name="aw",description="Alias of /addword.")
async def aw(ctx, text):
    addWord(ctx,text)

@slash.slash(name="removeword",description="Remove a word from the list of astronomy words. (seperate with commas)")
async def removeWord(ctx, text):
    #only execute if user is staff or Mia
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        global astronomyWords
        #suppose: "/addWord space, universe, star"; very similar to /addword
        invalid = []
        wordList = text.replace("\n",",").split(",")
        for word in wordList:
            wordEdit = word.strip().lower()
            if word in astronomyWords:
                astronomyWords.remove(wordEdit)
            else:
                invalid.append(wordEdit)
                wordList.remove(word)
        astronomyWords = sorted(astronomyWords)
        reply = []
        if len(wordList) > 0:
            reply.append("Successfully removed: "+', '.join(wordList)+"!")
        if len(invalid) > 0:
            reply.append(', '.join(invalid)+" could not be removed (they are not in the list, if you think this is wrong, message Mia).")
        reply = '\n'.join(reply)
        await ctx.send(reply, hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)
@slash.slash(name="rw",description="Alias of /removeword.")
async def rw(ctx, text):
    removeWord(ctx,text)

@slash.slash(name="setlimit",description="Send confirmation every x messages since the most recent astronomy-related word.")
async def setLimit(ctx, msg_nr = None):
    #only execute if user is staff or Mia
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        global settings
        if len(settings) == 0:
            await ctx.send("You can't add a word because the settings file is too short! Something probably went wrong when loading the file.\nChanging a setting now (to default settings) will overwrite and clear it (try again in a few seconds)")
            return
        # if user only types /setLimit, print the current limit
        if msg_nr == None:
            await ctx.send("The current limit is: "+settings[str(ctx.guild.id)]["limit"], hidden=True)
            return
        # else try to parseInt the given argument, and if the new limit is above 1, set it as the new goal for the off-topic counter
        try:
            counter = int(msg_nr)
        except:
            await ctx.send("The counter must be a number!", hidden=True)
            return
        if counter < 1:
            await ctx.send("The counter must be above 0!", hidden=True)
            return
        #set the setting as the new counter. If it doesn't exist yet, re-set it.
        try:
            settings[str(ctx.guild.id)]['limit'] = counter
        except KeyError:
            settings[str(ctx.guild.id)] = defaultSettings
        await ctx.send("Successfully set the counting limit to: `"+str(settings[str(ctx.guild.id)]['limit'])+"`!", hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name="wordlist",description="Get a file of the word list")
async def wordList(ctx, hide_file_from_others___yes_no = 'True'):
    # Get the list of astronomy-related words, and potentially share them with everyone in the server
    hide = hide_file_from_others___yes_no
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        if hide.lower() in "true,yes,yeh,ye,yah,yeah,sure,ok,okay,hidden,hide,secret,1".split(","):
            hide = True
        else: hide = False

        open(path+"astronomyWords.txt","w").write(f"{', '.join(astronomyWords)}")
        await ctx.send(file=discord.File(path+"astronomyWords.txt"), hidden=hide)
    else:
        # em = discord.Embed(title="Only staff can run this command.")
        # await ctx.send(embed=em, hidden = True) #Todo: embeds?
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name="resetcounter",description="Set the confirmation counter for the astronomy topic to 0")
async def resetCounter(ctx, newvalue=0):
    global settings
    #set the off-topic counter to the given value, as long as it's not above the limit/goal for sending a message
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        try:
            newvalue = int(newvalue)
        except:
            await ctx.send("The new value must be a number!", hidden=True)
            return
        if newvalue > settings[str(ctx.guild.id)]['limit']:
            await ctx.send("You can't really set the counter above the limit... :/", hidden=True)
            return
        settings[str(ctx.guild.id)]["msgCount"] = newvalue
        await ctx.send("Successfully set the counter!", hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name="rc",description="Alias for /resetcounter")
async def rc(ctx, newvalue=0):
    resetCounter(ctx, newvalue)

@slash.slash(name="checkword",description="Check if a word is in the astronomy-related words list")
async def checkword(ctx, words):
    #check if a word is in the astronomy-related words. If yes: give buttons to add it or remove the message
    # If no: give two buttons to add it or delete the message
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        for word in words.split(","):
            pass
        if word in astronomyWords:
            await ctx.send("This word (`"+word+"`) is in the list.",hidden=True)
        else:
            #required button component layout
            components = [{
                "type": 1,
                "components":[
                    {
                        "type": 2,
                        "label": "Add!",
                        "style": 1,
                        "custom_id": "addWordOk",
                        "disabled": False
                    },{
                        "type": 2,
                        "label": "Nevermind",
                        "style": 2,
                        "custom_id": "addWordNo",
                        "disabled": False
                    }]}]
            msg = await ctx.send("This word (`"+word+"`) is not in the list. Do you want to add it?",components=components) #TODO: buttons
            print(type(msg))
            try:
                def check(i):
                    print("executing check")
                    return i.user == ctx.author and i.message == ctx.message and "custom_id" in i.data.keys()
                interaction = await client.wait_for("button_click", check=check, timeout=16.0)
                print(dir(interaction))
                print(repr(interaction))
                print(interaction)
                #await addWord(ctx, word)
                components[0]["components"][0]["disabled"] = True
                components[0]["components"][1]["disabled"] = True
                components[0]["components"][0]["style"] = 3 #add
                components[0]["components"][1]["style"] = 4 #nevermind
                await msg.edit(components=components)
            except asyncio.TimeoutError: #todo1
                components[0]["components"][0]["disabled"] = True
                components[0]["components"][1]["disabled"] = True
                components[0]["components"][0]["style"] = 2 #give both gray color
                await msg.edit(components=components)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name="addvote",description="Add :small_red_triangle: emotes to the mentioned message_id")
async def addVote(ctx, msg_id):
    #add triangle reactions to a message with the given ID
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        try:
            msg_id = int(msg_id)
        except:
            await ctx.send("msg_id must be the id of a message!", hidden=True)
            return
        async for x in ctx.channel.history(limit=1):
            ctx.message = x;
            break
        ctx.message.id = msg_id
        await ctx.message.add_reaction("🔺")
        await ctx.message.add_reaction("🔻")
        await ctx.send("Successfully added the two reactions",hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name="addreaction",description="Add an emote to the mentioned message_id")
async def addReaction(ctx, msg_id, emote):
    # add an (any accessable) emote to a message with the given ID
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        try:
            msg_id = int(msg_id)
        except:
            await ctx.send("Please use a valid message ID!",hidden=True)

        emote = emote.split(" ")[0]
        if len(emote) == 0:
            await ctx.send("You didn't specify a reaction to add!",hidden=True)
        try:
            async for x in ctx.channel.history(limit=1):
                ctx.message = x;
                break
            ctx.message.id = msg_id
            await ctx.message.add_reaction(emote)
        except:
            await message.channel.send("Unknown emoji!",delete_after=8)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name='addquestion', description="Add a question to the queue")
async def addQuestion(ctx, question):
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        qotds.append(question)
        await ctx.send("✅ Successfully added question ("+str(len(qotds))+" questions in queue)", hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name='questionlist', description="Get the current question queue")
async def questionlist(ctx, hide_file_from_others___yes_no = 'True'):
    hide = hide_file_from_others___yes_no
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        if hide.lower() in "true,yes,yeh,ye,yah,yeah,sure,ok,okay,hidden,hide,secret,1".split(","):
            hide = True
        else: hide = False

        reply = []
        for x in range(len(qotds)):
            reply.append("`"+str(x)+"` | "+qotds[0])
        limit = len(reply)
        if len('\n'.join(reply)) > 2000:
            while '\n'.join(reply[:limit]) > 2000:
                limit -= 1
        await ctx.send('\n'.join(reply[:limit]),hidden=hide)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

@slash.slash(name="removequestion",description="Remove a question (with the given number) from the queue")
async def removeQuestion(ctx,index):
    global qotds
    role = discord.utils.find(lambda r: r.name == 'Mod', ctx.guild.roles)
    if ctx.author.id == 262913789375021056 or role in ctx.author.roles:
        try:
            index = int(index)
            del qotds[index]
        except:
            await ctx.send("Could not remove question! (index "+str(index)+"/"+str(len(qotds)-1)+")",hidden=True)
    else:
        await ctx.send("Only staff can run this command!", hidden=True)

timer = 0
def clockQuestionEvent():
    global timer, qotdEmbed
    # This function runs periodically every 60 second
    timer = threading.Timer(60, clockQuestionEvent)
    timer.start()
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    if current_time in ["13:59","14:00","14:01"]:
        print("Current Time =", current_time)
    if current_time == "14:00":  # check if matches with the desired time
        try:
            desc = qotds[0]
        except:
            print("Couldn't set new question: there are none, or the list isn't loaded in correctly.")
            return
        # color = int(color,16)
        embedVar = discord.Embed(title="❓❔ Question of the Day ❔❓", description=desc, color=0x00ffff)
        embedVar.set_footer(text="Astronomy Club      ("+str(len(qotds))+" queued)")
        qotdEmbed = embedVar

        none_of_this_workedTwT = {
        # qotdChannel.send(embed=embedVar)

        # async def send(embed):
        #     await qotdChannel.send(embed=embed)
        # try:
        #     loop = asyncio.get_event_loop()
        # except RuntimeError:
        #     loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(loop)
        # loop = asyncio.get_event_loop()
        # try:
        #     loop.run_until_complete(send())
        # finally:
        #     loop.run_until_complete(loop.shutdown_asyncgens())
        #     loop.close()
        # submit the coroutine to the event loop thread
        # send_fut = asyncio.run_coroutine_threadsafe(send(embedVar), client_loop)
        # wait for the coroutine to finish
        # send_fut.result()
        # loop.run_until_complete(send(embedVar))
        # loop.close()
    # await qotdChannel.send(embed=embedVar)})();
        # loop = asyncio.get_event_loop()
        # loop.create_task(send)
        # asyncio.run(send(embedVar))
        # loop = asyncio.get_event_loop()
        # loop.create_task(aioredis.create_redis('redis://localhost:6379'))
        # c = loop.run_until_complete(send(embedVar))
        }
clockQuestionEvent()

def signal_handler(signal, frame):
    global timer
    # try to save files. if they haven't been loaded in yet (discord hasn't started on_read() yet;
    # and the files are empty, don't save the empty variables into them!) Then exit the program using sys.exit(0)
    print("📉 Disconnecting...")
    if len(settings) > 0:
        with open('settings.json', 'w') as f:
            json.dump(settings, open(path+"settings.json","w"))
        print("Saved guild settings!")
    else:
        print("Couldn't save settings (unsafe)! Not loaded in correctly!")
    if len(astronomyWords) > 5:
        open(path+"astronomyWords.txt","w").write(f"{', '.join(astronomyWords)}")
        print("Saved astronomy words!")
    else:
        print("Couldn't save astronomy words (unsafe)! Not loaded in correctly!")
    if len(qotds) > 0:
        with open('qotds.json', 'w') as f:
            json.dump(qotds, open(path+"qotds.json","w"))
        print("Saved Questions Of The Day file!")
    else:
        print("Couldn't save the questions of the day file (unsafe)! Not loaded in correctly!")
    try:
        timer.cancel()
        print("Joined the QOTD time counter thread!")
    except:
        print("Could not join the QOTD time counter thread (for unknown reasons)!")
    print("-=--- Saved successfully ---=-")
    try:
        sys.exit(0)
    except RuntimeError:
        print("discord sent another one of their long runtime errors. so i ignore it. like always. Urghghg")

signal.signal(signal.SIGINT, signal_handler) #notice KeyboardInterrupt, and run closinvg code (save files and exit)


client.run( #token v2
    open('token.txt',"r").read()
)
