import asyncio
from os import path
from pathlib import Path
import os
import discord
from discord.ext import commands , tasks
import time
import sqlite3
import config
# --------- Import Library required ------------

TOKEN = config.TOKEN

bot = commands.Bot(command_prefix='r/')
bot.remove_command('help')

channel_remind = <CHANNEL_ID>

@bot.event
async def on_ready():
    print('---------------')
    print(bot.user.name)
    print('---------------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you | r/help"))
    clock.start()

@tasks.loop(seconds=30) #Loop every 30sec to check in db if its alert time
async def clock():
    time_data = os.popen("date +%d/%m/%Y")
    time_data = (time_data.read())[:10]
    hour_data = os.popen("date +%H:%M")
    hour_data = (hour_data.read())[:5]

    conn = sqlite3.connect('data.db')
    data = conn.execute("SELECT DATE,DATE_R,HOUR,REMIND,ALERT FROM DATA")
    for cron in data:
        if cron[1] == time_data:
            if cron[4] == 0:
                if cron[2] == hour_data:
                    channel = bot.get_channel(channel_remind)
                    await channel.send(f"Remind for **{cron[0]}**: ```{cron[3]}```")
                    conn.execute("UPDATE DATA SET ALERT = 1 WHERE HOUR = ?",(hour_data,))
                    conn.commit()
    conn.close()



@bot.command()
async def help(ctx):
    await ctx.send("Epsilone remind one day before the alert.\n\n__Command:__ \nr/add {**remind**} {**dd/mm/yy**} {**hh:mm**}\n\n   **remind**: Sentence to remember\n    **dd/mm/yy**: date\n    **hh:mm**: hours")


@bot.command()
async def add(ctx, remind=None, date=None, hour=None):
    if remind == None:
        await ctx.send("Remind missing")
    else:
        if date == None:
            await ctx.send("Date missing")
        else:
            if hour == None:
                hour = "12:00"

            if date[:1] == "0": #if the day is compose to 1 number = soustrat 1 to the day and add a 0 for first number on the day
                day = (int(date[:2])-1)
                day = ("000"+str(day))
                day = day[2:]
            else: #if the day is compose to 2 number = soustrat 1 to the day
                day = (int(date[:2])-1)
                day = ("00"+str(day))
                day = day[2:]

            date_r = day + str(date[2:])

            conn = sqlite3.connect('data.db')
            conn.execute("INSERT INTO DATA (DATE,DATE_R,HOUR,REMIND,ALERT) VALUES (?, ?, ?, ?, 0);", (date, date_r, hour, remind,)) #save in db the data
            conn.commit()
            conn.close()

            await ctx.send("Save. I will alert one day before")

bot.run(TOKEN)
