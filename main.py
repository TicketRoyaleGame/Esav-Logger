import os
import discord
from discord.ext import commands
from flask import Flask
import threading

# שרת רקע קטן בשביל הסטטוס הירוק ב-Render (משתמש בפורט 10003)
app = Flask(__name__)
@app.route('/')
def home(): 
    return "Logger Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10003))
    app.run(host="0.0.0.0", port=port)

# =========================================================
# הגדרות הבוט השלישי
# =========================================================
TOKEN = os.getenv("TOKEN")
GENERAL_LOG_CHANNEL_ID = 1560756016604512376  # ה-ID של חדר הלוגים הכללי בשרת הצוות
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    print(f"📊 {bot.user.name} מחובר ומתעד לוגים בשרת!")

# 1. לוג הודעות שנמחקו (Message Delete)
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    log_channel = bot.get_channel(GENERAL_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="🗑️ הודעה נמחקה",
            description=f"**נשלחה על ידי:** {message.author.mention}\n**בערוץ:** {message.channel.mention}",
            color=discord.Color.red()
        )
        if message.content:
            embed.add_field(name="תוכן ההודעה שנמחקה:", value=f"```{message.content}```", inline=False)
        else:
            embed.add_field(name="תוכן ההודעה:", value="*הודעה ריקה או מדיה (תמונה/קובץ)*", inline=False)
            
        embed.set_footer(text=f"User ID: {message.author.id} | Message ID: {message.id}")
        await log_channel.send(embed=embed)

# 2. לוג הודעות שנערכו (Message Edit)
@bot.event
async def on_message_edit(message_before, message_after):
    if message_before.author.bot:
        return
        
    if message_before.content == message_after.content:
        return

    log_channel = bot.get_channel(GENERAL_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="📝 הודעה נערכה",
            description=f"**נערכה על ידי:** {message_before.author.mention}\n**בערוץ:** {message_before.channel.mention}\n[קפוץ להודעה]({message_after.jump_url})",
            color=discord.Color.blue()
        )
        embed.add_field(name="לפני השינוי:", value=f"```{message_before.content}```", inline=False)
        embed.add_field(name="אחרי השינוי:", value=f"```{message_after.content}```", inline=False)
        embed.set_footer(text=f"User ID: {message_before.author.id}")
        await log_channel.send(embed=embed)

# הפעלת שרת הרקע והבוט ביחד
threading.Thread(target=run_flask, daemon=True).start()
bot.run(TOKEN)
