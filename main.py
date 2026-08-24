
import asyncio
import json
import os
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİTABANI İŞLEMLERİ ---
DB_FILE = "database.json"


def load_db():
  if not os.path.exists(DB_FILE):
    return {}
  with open(DB_FILE, "r", encoding="utf-8") as f:
    try:
      return json.load(f)
    except:
      return {}


def save_db(data):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


@bot.event
async def on_ready():
  print(f"{bot.user.name} başarıyla giriş yaptı!")


# ==========================================
# 1. KAYIT SİSTEMİ (.k komutu)
# Kullanım: .k @etiket Neymar | SLK | 🇧🇷 | 1M
# ==========================================
@bot.command(name="k")
async def kayit(ctx, member: discord.Member, *, veri: str = None):
  if not veri:
    await ctx.send(
        "❌ Eksik kullanım! Örnek: `.k @etiket Neymar | SLK | 🇧🇷 | 1M`"
    )
    return

  parts = [p.strip() for p in veri.split("|")]
  if len(parts) < 4:
    await ctx.send(
        "❌ Bilgileri eksik girdiniz! `İsim | Mevki | Ülke | Değer` formatında"
        " yazın."
    )
    return

  isim, mevki, ulke, deger = parts[0], parts[1], parts[2], parts[3]

  db = load_db()
  guild_id = str(ctx.guild.id)
  if guild_id not in db:
    db[guild_id] = {}

  db[guild_id][str(member.id)] = {
      "isim": isim,
      "mevki": mevki,
      "ulke": ulke,
      "deger": deger,
  }
  save_db(db)

  yeni_isim = f"{isim} | {mevki} | {ulke} | {deger}"
  try:
    await member.edit(nick=yeni_isim)
  except:
    pass

  await ctx.send(
      f"✅ Başarıyla kaydedildi! **{member.mention}** -> `{yeni_isim}`"
  )


# ==========================================
# 2. ARAMA SİSTEMİ (.ara komutu)
# Kullanım: .ara Neymar
# ==========================================
@bot.command(name="ara")
async def ara(ctx, *, aranan: str = None):
  if not aranan:
    await ctx.send("❌ Lütfen aranacak futbolcu adını yazın. Örnek: `.ara Neymar`")
    return

  db = load_db()
  guild_id = str(ctx.guild.id)

  if guild_id not in db or not db[guild_id]:
    await ctx.send("⚠️ Bu sunucuda kayıtlı futbolcu bulunmuyor.")
    return

  bulunanlar = []
  for user_id, info in db[guild_id].items():
    if aranan.lower() in info["isim"].lower():
      member = ctx.guild.get_member(int(user_id))
      mention = member.mention if member else "Sunucudan Ayrılmış"
      nick = (
          f"{info['isim']} | {info['mevki']} | {info['ulke']} | {info['deger']}"
      )
      bulunanlar.append(f"👤 **Kullanıcı:** {mention}\n🏷️ **Bilgi:** `{nick}`")

  if bulunanlar:
    await ctx.send("\n\n".join(bulunanlar[:5]))
  else:
    await ctx.send(f"❌ '{aranan}' adında kayıtlı bir futbolcu bulunamadı.")


# ==========================================
# 3. DEĞER VERME SİSTEMİ (.dver komutu)
# Kullanım: .dver @etiket 4
# ==========================================
@bot.command(name="dver")
async def deger_ver(ctx, member: discord.Member, miktar: int):
  db = load_db()
  guild_id = str(ctx.guild.id)
  user_id = str(member.id)

  if guild_id not in db or user_id not in db[guild_id]:
    await ctx.send("❌ Bu kullanıcı sistemde kayıtlı değil.")
    return

  eski_deger_str = db[guild_id][user_id]["deger"]
  try:
    eski_sayi = int(
        eski_deger_str.upper().replace("M", "").replace("TL", "").strip()
    )
  except:
    eski_sayi = 1

  yeni_sayi = eski_sayi + miktar
  yeni_deger_str = f"{yeni_sayi}M"

  db[guild_id][user_id]["deger"] = yeni_deger_str
  save_db(db)

  info = db[guild_id][user_id]
  yeni_isim = (
      f"{info['isim']} | {info['mevki']} | {info['ulke']} | {info['deger']}"
  )
  try:
    await member.edit(nick=yeni_isim)
  except:
    pass

  await ctx.send(
      f"📈 **Değer Güncellendi!** {member.mention} yeni piyasa değeri:"
      f" **{yeni_deger_str}**"
  )


# ==========================================
# 4. ANTRENMAN SİSTEMİ (.ant komutu)
# ==========================================
class AntrenmanButtonView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=60)

  async def progress_bar(
      self, interaction: discord.Interaction, ant_adi: str
  ):
    await interaction.response.send_message(
        f"🏋️‍♂️ **{ant_adi}** antrenmanı başlatıldı...\n`█░░░░░░░░░` %10",
        ephemeral=False,
    )
    original_message = await interaction.original_response()

    adımlar = [
        ("`██░░░░░░░░`", "%20"),
        ("`███░░░░░░░`", "%30"),
        ("`████░░░░░░`", "%40"),
        ("`█████░░░░░`", "%50"),
        ("`██████░░░░`", "%60"),
        ("`███████░░░`", "%70"),
        ("`████████░░`", "%80"),
        ("`█████████░`", "%90"),
        ("`██████████`", "%100 (Tamamlandı! 🎉)"),
    ]

    for bar, yuzde in adımlar:
      await asyncio.sleep(0.6)
      await original_message.edit(
          content=f"🏋️‍♂️ **{ant_adi}** antrenmanı devam ediyor...\n{bar} {yuzde}"
      )

  @discord.ui.button(
      label="Top Sürme", style=discord.ButtonStyle.primary, emoji="⚽"
  )
  async def top_surme(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.progress_bar(interaction, "Top Sürme")

  @discord.ui.button(
      label="Çalım", style=discord.ButtonStyle.success, emoji="⚡"
  )
  async def calim(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.progress_bar(interaction, "Çalım")

  @discord.ui.button(
      label="Fizik", style=discord.ButtonStyle.danger, emoji="💪"
  )
  async def fizik(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.progress_bar(interaction, "Fizik")

  @discord.ui.button(
      label="Şut", style=discord.ButtonStyle.secondary, emoji="🎯"
  )
  async def sut(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.progress_bar(interaction, "Şut")


class RolSecimView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=30)

  @discord.ui.button(
      label="Kaleci misin?", style=discord.ButtonStyle.secondary, emoji="🧤"
  )
  async def kaleci(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_message(
        "🧤 Kaleci antrenmanları yakında eklenecektir!", ephemeral=True
    )

  @discord.ui.button(
      label="Futbolcu Musun?", style=discord.ButtonStyle.primary, emoji="🏃‍♂️"
  )
  async def futbolcu(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    view = AntrenmanButtonView()
    await interaction.response.edit_message(
        content=(
            "💪 **Futbolcu seçildi!** Geliştirmek istediğin antrenmanı seç:"
        ),
        view=view,
    )


@bot.command(name="ant")
async def antrenman(ctx):
  view = RolSecimView()
  await ctx.send("⚽ Hangisi olmak istiyorsun?", view=view)


# ==========================================
# 5. PENALTI SİSTEMİ (.pen komutu)
# ==========================================
class PenaltiRolSecimView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=30)

  @discord.ui.button(
      label="Kaleci misin?", style=discord.ButtonStyle.blurple, emoji="🧤"
  )
  async def kaleci_sec(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    sonuc = random.choice(["gol_yedi", "kurtardi"])
    if sonuc == "gol_yedi":
      await interaction.response.edit_message(
          content=(
              f"😞 **Gol Yedin!** {interaction.user.mention} rakibin şutunu"
              " çıkaramadı, üzüntüden yıkıldı..."
          ),
          view=None,
      )
    else:
      await interaction.response.edit_message(
          content=(
              f"🙌 **Harika Kurtarış!** {interaction.user.mention} topu müthiş"
              " bir refleksle tuttu ve sevinçten havalara uçtu! 🥳"
          ),
          view=None,
      )

  @discord.ui.button(
      label="Futbolcu Musun?", style=discord.ButtonStyle.green, emoji="⚽"
  )
  async def futbolcu_sec(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    sonuc = random.choice(["gol", "aut", "direk", "kurtaris"])
    if sonuc == "gol":
      metin = (
          f"🎉 **GOL!** {interaction.user.mention} muhteşem bir vuruşla topu"
          " ağlara gönderdi! 🥅⚽"
      )
    elif sonuc == "aut":
      metin = (
          f"↗️ **AUT!** {interaction.user.mention} sert vurdu ancak top dışarı"
          " gitti."
      )
    elif sonuc == "direk":
      metin = (
          f"💥 **DİREK!** {interaction.user.mention} rakip kaleye çok sert bir"
          " şut vurdu, top direkten geri döndü!"
      )
    else:
      metin = (
          f"🧤 **KURTARIŞ!** Kaleci harika bir hamleyle topu çeldi, gol izni"
          " vermedi."
      )

    await interaction.response.edit_message(content=metin, view=None)


@bot.command(name="pen")
async def penalti(ctx):
  view = PenaltiRolSecimView()
  await ctx.send("⚽ Kaleci misin? Futbolcu musun?", view=view)


# Botu Çalıştırma
bot.run(os.getenv("TOKEN"))
