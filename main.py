import discord
import locale
import time
import os
from datetime import timedelta, datetime
from keep_alive import keep_alive

locale.setlocale(locale.LC_TIME, '')

intents = discord.Intents.all()
intents.message_content = True
intents.guild_scheduled_events = True

client = discord.Client(intents=intents)

gown_id = 115486361833701383
guild_id = 1046389103266107404
event_channel_id = 1228670607789395978
event_role_id = 1228266794503114805
coiffeur_emoji = 1231603611864137768

event_notifications = { }

coiffeur_cooldowns = { }
coiffeur_score = { }

@client.event
async def on_scheduled_event_create(event):
  await notificationEventCreate(event)

@client.event
async def on_schedule_event_delete(event):
  await notificationEventDelete(event)

@client.event
async def on_message(message):
  await coiffeurCheck(message)

@client.event
async def on_member_join(member):
  await creationDateCheck(member)

# ---

async def creationDateCheck(member):
  if (member.created_at > datetime.now(member.created_at.tzinfo) - timedelta(weeks = 4)):
    guild = client.get_guild(guild_id) 
    gown = await guild.fetch_member(gown_id)
    await gown.send("Warning : The member " + member.display_name + " (<@" + str(member.id) + ">) has less than 1 month since account creation.")

# ---

async def coiffeurCheck(attackerMessage):
  if (attackerMessage.reference is not None):

    guild = client.get_guild(attackerMessage.reference.guild_id)
    if (guild is not None):

      channel = guild.get_channel(attackerMessage.reference.channel_id)
      if (channel is not None and type(channel) == discord.channel.TextChannel):

        victimMessage = await channel.fetch_message(attackerMessage.reference.message_id)
        coiffeurDone = ("feur" in attackerMessage.content.lower()) and ("quoi" in victimMessage.content.lower())
        coiffeurAvailable = (attackerMessage.author.id not in coiffeur_cooldowns) or (coiffeur_cooldowns[attackerMessage.author.id] + timedelta(hours = 1) < datetime.now())

        print("Coiffeur done = " + str(coiffeurDone))
        print("Coiffeur available = " + str(coiffeurAvailable))

        if (coiffeurDone and coiffeurAvailable):
          score = 0
          if (attackerMessage.author.id in coiffeur_score):
            score = coiffeur_score[attackerMessage.author.id]

          print("Current score for " + attackerMessage.author.display_name + " : " + str(score))

          score = score + 1

          print("New score for " + attackerMessage.author.display_name + " : " + str(score))

          coiffeur_score[attackerMessage.author.id] = score
          coiffeur_cooldowns[attackerMessage.author.id] = datetime.now()

          guild = client.get_guild(guild_id)
          if (guild is not None):
            await attackerMessage.add_reaction(guild.get_emoji(coiffeur_emoji))

        print("Cooldown set to " + str(datetime.now()))
# ---

async def notificationEventCreate(event):
  guild = client.get_guild(guild_id)

  if guild is not None:
    event_channel = guild.get_channel(event_channel_id)

    if type(event_channel) == discord.channel.TextChannel:
      response = generateEventSummaryResponse(event)
      event_notifications[event.id] = await event_channel.send(content = response[0], embed = response[1])
      await event_channel.create_thread(name = event.creator.display_name + " - " + event.name, message = event_notifications[event.id], auto_archive_duration = 1440, type = None, reason = "Fil d'événement créé par le bot.", invitable = True, slowmode_delay = None)

# ---

async def notificationEventDelete(event):
  guild = client.get_guild(guild_id)

  if guild is not None:
    event_channel = guild.get_channel(event_channel_id)

    if type(event_channel) == discord.channel.TextChannel:
      response = generateEventDeletionResponse(event)

      if event.id in event_notifications :
        event_notifications[event.id] = await event_channel.send(content = response[0], embed = response[1])
      else :
        event_notifications[event.id] = await event_notifications[event.id].edit(content = response[0], embed = response[1], suppress = False)

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

discordToken = os.environ.get('DISCORD_TOKEN')
client.run(discordToken)
