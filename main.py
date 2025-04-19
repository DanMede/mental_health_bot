import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv # type: ignore
from db import init_db, save_mood
from discord.ui import View, Button
from datetime import time
import pytz

# โหลดค่าจาก .env
load_dotenv()
TOKEN      = os.getenv("DISCORD_TOKEN")        # เอาแค่ชื่อคีย์
GUILD_ID   = int(os.getenv("GUILD_ID"))        # เอาแค่ชื่อคีย์
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))      # เอาแค่ชื่อคีย์

# ตั้งค่า intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} พร้อมใช้งานแล้ว!")
    # สร้างฐานข้อมูล (ถ้ายังไม่เคยมี)
    init_db()
    # เริ่มงานส่ง DM ถามอารมณ์ทุกวัน
    daily_mood_check.start()

class MoodView(View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # ให้เฉพาะคนที่ถูกถามเท่านั้นกดได้
        return interaction.user.id == self.user.id

    @discord.ui.button(label="ดีมาก 😊", style=discord.ButtonStyle.primary)
    async def good(self, button: Button, interaction: discord.Interaction):
        save_mood(self.user.id, "ดีมาก")
        await interaction.response.edit_message(
            content="✅ บันทึกอารมณ์ว่า **ดีมาก** เรียบร้อยแล้ว", view=None
        )

    @discord.ui.button(label="ปกติ 🙂", style=discord.ButtonStyle.primary)
    async def normal(self, button: Button, interaction: discord.Interaction):
        save_mood(self.user.id, "ปกติ")
        await interaction.response.edit_message(
            content="✅ บันทึกอารมณ์ว่า **ปกติ** เรียบร้อยแล้ว", view=None
        )

    @discord.ui.button(label="แย่ 😞", style=discord.ButtonStyle.primary)
    async def bad(self, button: Button, interaction: discord.Interaction):
        save_mood(self.user.id, "แย่")
        await interaction.response.edit_message(
            content="✅ บันทึกอารมณ์ว่า **แย่** เรียบร้อยแล้ว", view=None
        )

    @discord.ui.button(label="ยกเลิก ❌", style=discord.ButtonStyle.danger)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="❌ ยกเลิกการบันทึกอารมณ์แล้ว", view=None
        )

# ส่ง DM ถามอารมณ์ทุกวันเวลา 20:00 Asia/Bangkok
@tasks.loop(time=time(20, 0, 0, tzinfo=pytz.timezone("Asia/Bangkok")))
async def daily_mood_check():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(
                "💭 มาอัปเดตอารมณ์ของคุณวันนี้กันเถอะ!",
                view=MoodView(member)
            )
        except discord.Forbidden:
            # ถ้าปิด DM ให้ข้ามไป
            pass

@bot.command()
async def start(ctx: commands.Context):
    """
    คำสั่ง !start ให้บอทส่ง DM ถามอารมณ์ทันที
    """
    await ctx.author.send(
        "ลองเลือกอารมณ์ตอนนี้เลย 😄",
        view=MoodView(ctx.author)
    )
    await ctx.reply("✅ ส่ง DM ให้แล้วนะ")

if __name__ == "__main__":
    bot.run(TOKEN)
