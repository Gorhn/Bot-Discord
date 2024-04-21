import discord
import time
import locale
from keep_alive import keep_alive

locale.setlocale(locale.LC_TIME, '')

intents = discord.Intents.all()
intents.message_content = True
intents.guild_scheduled_events = True

client = discord.Client(intents=intents)

guild_id = 1046389103266107404
event_channel_id = 1228670607789395978
event_role_id = 1228266794503114805

event_notifications = { }

@client.event
async def on_scheduled_event_create(event):
  await notificationEventCreate(event)

@client.event
async def on_scheduled_event_update(event, user):
  await notificationEventUpdate(event, user)

@client.event
async def on_schedule_event_delete(event):
  await notificationEventDelete(event)

# ---

async def notificationEventCreate(event):
  guild = client.get_guild(guild_id)

  if guild is not None:
    event_channel = guild.get_channel(event_channel_id)

    if type(event_channel) == discord.channel.TextChannel:
      response = generateEventSummaryResponse(event)
      event_notifications[event.id] = await event_channel.send(content = response[0], embed = response[1])
      await event_channel.create_thread(event.creator.display_name + " - " event.name, "Vous pouvez discuter de l'événement ici !", 1440, None, "Fil d'événement créé par le bot.", True, None)

# ---

async def notificationEventUpdate(event, user):
  guild = client.get_guild(guild_id)

  if guild is not None:
    event_channel = guild.get_channel(event_channel_id)

    if type(event_channel) == discord.channel.TextChannel:
      response = generateEventSummaryResponse(event)

      print("a")
      if event_notifications[event.id] is not None :
        print("b")
        print(event)
        event_notifications[event.id] = await event_notifications[event.id].edit(content = response[0], embed = response[1], suppress = False)
      else :
        print("c")
        event_notifications[event.id] = await event_channel.send(content = response[0], embed = response[1])
        

# ---

async def notificationEventDelete(event):
  guild = client.get_guild(guild_id)

  if guild is not None:
    event_channel = guild.get_channel(event_channel_id)

    if type(event_channel) == discord.channel.TextChannel:
      response = generateEventDeletionResponse(event)

      if event_notifications[event.id] is not None :
        event_notifications[event.id] = await event_notifications[event.id].edit(content = response[0], embed = response[1], suppress = False)
      else :
        event_notifications[event.id] = await event_channel.send(content = response[0], embed = response[1])

  event_notifications.pop(event.id)

# ---

def generateEventDeletionResponse(event):
  date = " "

  if hasattr(event, "scheduled_start_time") :
    date = time.strftime(event.scheduled_start_time)

  if hasattr(event, "scheduled_end_time") :
    date += " - " + time.strftime(event.scheduled_end_time)

  if hasattr(event, "location") :
    date += "\n" + event.location
    
  eventContent = "<@&" + str(event_role_id) + "> : L'événement de " + event.creator.display_name + " a été annulé. \n"

  eventEmbed = discord.Embed(title = "ANNULATION : " + event.name, description = date, color = 0xaa0000)
  eventEmbed.add_field(name = " ", value = event.description, inline = False)
  eventEmbed.add_field(name = " ", value = "On aura d'autres occasions de se retrouver :wink:", inline = False)

  return eventContent, eventEmbed

# ---

def generateEventSummaryResponse(event):
  date = " "

  if hasattr(event, "scheduled_start_time") :
    date = time.strftime(event.scheduled_start_time)

  if hasattr(event, "scheduled_end_time") :
    date += " - " + time.strftime(event.scheduled_end_time)

  if hasattr(event, "location") :
    date += "\n" + event.location

  eventContent = "<@&" + str(event_role_id) + "> : Un nouvel événement a été créé par " + event.creator.display_name + " !\n"

  eventEmbed = discord.Embed(title = event.name, description = date, color = 0x00aa00)
  eventEmbed.add_field(name = " ", value = event.description, inline = False)
  eventEmbed.add_field(name = " ", value = "Manifestez vous dans la rubrique événements en haut du serveur ou discutez-en dans le fil juste en dessous !", inline = False)

  return eventContent, eventEmbed

# ---

keep_alive()

client.run('MTIyODY2NDQ1MTcyMTMzNDg3NA.GX-scm.eBF2jv7qXe1ODdeB-CQT0COVhNntaA-ULNiXEg')
