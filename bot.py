import asyncio
from os import path
from pathlib import Path
import os
import discord
from discord.ext import commands , tasks
import time
import sqlite3
import config
from calendar import monthrange
#----------------- requirement ------------------

TOKEN = config.TOKEN

bot = commands.Bot(command_prefix='e/')
bot.remove_command('help')

channel_remind = 893232057596133446

@bot.event
async def on_ready():
    print('---------------')
    print(bot.user.name)
    print('---------------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you | e/help"))
    clock.start()

@tasks.loop(seconds=30)
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
    await ctx.send("Epsilone remind one day before the alert.\n\n__Commands:__ \nr/add {**remind**} {**dd/mm/yy**} {**hh:mm**}\n   **remind**: Sentence to remember\n    **dd/mm/yy**: date\n    **hh:mm**: hours\n\n\nr/list {**none/all**}\n   **none**: List dates not yet passed\n   **all**: list all dates")


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

            month = int((str(date[3:]))[:-5])
            year = int(str(date[6:]))
            num_days = monthrange(year, month)[1]
            day_test = int(str(date[:2]))

            if day_test <= num_days and day_test > 0:   #Check if the day exist in the month
                if date == f"01/01/{year}":
                    date_r = f"{monthrange((year)-1, 12)[1]}/12/{(year)-1}"
                else:
                    if date[:1] == "0":
                        day = (int(date[:2])-1)
                        day = ("000"+str(day))
                        day = day[2:]
                    else:
                        day = (int(date[:2])-1)
                        day = ("00"+str(day))
                        day = day[2:]

                    date_r = day + str(date[2:])
                    if day == "00":
                        month = month - 1
                        if month < 10:
                            month = f"0{str(month)}"

                        num_days = monthrange(int(year), int(month))[1]
                        date_r = f"{num_days}/{month}/{year}"

                conn = sqlite3.connect('data.db')
                conn.execute("INSERT INTO DATA (DATE,DATE_R,HOUR,REMIND,ALERT) VALUES (?, ?, ?, ?, 0);", (date, date_r, hour, remind,))
                conn.commit()
                conn.close()

                print(date_r)
                await ctx.send("Save. I will alert one day before")

            else:
                await ctx.send(f'{day_test} does not exist this month.')

@bot.command()
async def list(ctx, arg=None):
    exist = False
    if arg == None:
        conn = sqlite3.connect('data.db')
        data = conn.execute("SELECT DATE,DATE_R,HOUR,REMIND,ALERT FROM DATA")
        for cron in data:
            if cron[4] == 0:
                exist = True
        if exist == True:
            data = conn.execute("SELECT DATE,DATE_R,HOUR,REMIND,ALERT FROM DATA")
            for cron in data:
                if cron[4] == 0:
                    await ctx.send(f"Date:{cron[0]} | Recalls on {cron[1]} at {cron[2]} | ``{cron[3]}``")
        else:
            await ctx.send("No date recorded")
    elif arg == "all":
        conn = sqlite3.connect('data.db')
        data = conn.execute("SELECT DATE,DATE_R,HOUR,REMIND,ALERT FROM DATA")
        for cron in data:
            await ctx.send(f"Date:{cron[0]} | Recalls on {cron[1]} at {cron[2]} | ``{cron[3]}``")

    conn.close()


bot.run(TOKEN)
