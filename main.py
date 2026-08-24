
import discord
from discord.ext import commands
import random
import os

# Botun istemci ayarları
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# AFK olan kullanıcıları tutmak için sözlük
afk_users = {}

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı ve aktif!")

@bot.event
async def on_message(message):
    # Botun kendi mesajlarına cevap vermesini engelle (çift mesaj sorununu önler)
    if message.author.bot:
        return

    # Etiketlenen biri AFK mı kontrol et
    if message.mentions:
        for user in message.mentions:
            if user.id in afk_users:
                sebep = afk_users[user.id]
                await message.channel.send(f"💤 **{user.name}** şu an AFK!\n> **Sebep:** {sebep}")

    # AFK olan kullanıcı mesaj yazarsa AFK modundan çıkar
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"👋 Hoş geldin {message.author.mention}! AFK modundan çıktın.")

    # Komutların çalışması için bu satır şarttır
    await bot.process_commands(message)

# ==========================================
# 1. YARDIM VE TÜM KOMUTLAR MENÜSÜ (.komutlar)
# ==========================================
@bot.command(name="komutlar")
async def komutlar(ctx):
    embed = discord.Embed(
        title="🤖 FUTBOL & SUNUCU BOTU - TÜM KOMUTLAR",
        description="Sunucumuzda kullanılan tüm güncel komutlar ve sistemler aşağıda listelenmiştir:\n________________________________",
        color=discord.Color.yellow()
    )
    
    embed.add_field(
        name="⚽ Oyun & Kulüp Sistemleri",
        value="• `.ant` - Antrenman yapma komutu.\n• `.pen` - Penaltı atma komutu.\n• `.kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde` - Resmi KAP bildirimi.",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Özel & Bilgi Komutları",
        value="• `.dev` (veya `.dver`) - Botun geliştiricisini gösterir.\n• `.afk [sebep]` - AFK moduna geçer.",
        inline=False
    )
    
    embed.add_field(
        name="🔨 Moderasyon Komutları",
        value="• `.dsil [sayı]` - Belirtilen miktarda mesajı siler.\n• `.k @Kullanıcı [sebep]` - Kullanıcıyı sunucudan atar (Kick).",
        inline=False
    )
    
    embed.set_footer(text="Arion League Bot | Tüm Sistemler Aktif")
    await ctx.send(embed=embed)

# ==========================================
# 2. KAP BİLDİRİM SİSTEMİ (.kap)
# ==========================================
@bot.command(name="kap")
async def kap(ctx, member: discord.Member = None, eski_takim: str = None, yeni_takim: str = None, maas: str = None, sezon: str = None, bonservis: str = None, *, ek_madde: str = "Belirtilmemiş"):
    if not member or not eski_takim or not yeni_takim or not maas or not sezon or not bonservis:
        await ctx.send("❌ Eksik bilgi girdiniz!\n> **Kullanım:** `.kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde`")
        return

    embed = discord.Embed(
        title="🔔 K.A.P. | KAMUYU AYDINLATMA PLATFORMU BİLDİRİMİ",
        description="Şirketimiz / Kulübümüz tarafından profesyonel futbolcu transferi hakkında resmi açıklama:\n________________________________",
        color=discord.Color.yellow()
    )
    
    embed.add_field(name="👤 Futbolcu", value=member.mention, inline=False)
    embed.add_field(name="🏢 Eski Takımı", value=eski_takim, inline=True)
    embed.add_field(name="🏟️ Yeni Takımı", value=yeni_takim, inline=True)
    embed.add_field(name="💶 Maaş / Ücret", value=maas, inline=True)
    embed.add_field(name="⏳ Sözleşme Süresi", value=sezon, inline=True)
    embed.add_field(name="💰 Bonservis Bedeli", value=bonservis, inline=True)
    embed.add_field(name="📝 Özel Şartlar / Ek Madde", value=ek_madde, inline=False)
    
    embed.set_footer(text=f"KAP Transfer Sistemi | Bildiren: {ctx.author.name}")
    await ctx.send(embed=embed)

# ==========================================
# 3. DEV / DVER KOMUTU (.dev & .dver)
# ==========================================
@bot.command(name="dev", aliases=["dver"])
async def dev(ctx):
    await ctx.send("💻 **Bu bot;** Arion League projeleri ve futbol sunucuları için özel olarak geliştirilmiştir!")

# ==========================================
# 4. AFK SİSTEMİ (.afk)
# ==========================================
@bot.command(name="afk")
async def afk(ctx, *, sebep: str = "Belirtilmemiş"):
    afk_users[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention} başarıyla AFK moduna geçti.\n> **Sebep:** {sebep}")

# ==========================================
# 5. MESAJ SİLME KOMUTU (.dsil)
# ==========================================
@bot.command(name="dsil")
@commands.has_permissions(manage_messages=True)
async def dsil(ctx, amount: int = 5):
    if amount < 1:
        await ctx.send("❌ Lütfen 1'den büyük bir sayı girin!")
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Başarıyla **{amount}** adet mesaj silindi!", delete_after=3)

@dsil.error
async def dsil_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için `Mesajları Yönet` yetkisine sahip olmalısın!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Lütfen geçerli bir sayı gir! Örnek: `.dsil 10`")

# ==========================================
# 6. KICK KOMUTU (.k)
# ==========================================
@bot.command(name="k")
@commands.has_permissions(kick_members=True)
async def k(ctx, member: discord.Member, *, sebep: str = "Sebep belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"🔨 **{member.name}** sunucudan atıldı!\n> **Sebep:** {sebep}")

@k.error
async def k_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için `Üyeleri At` yetkisine sahip olmalısın!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Lütfen atılacak kişiyi etiketle! Örnek: `.k @Kullanıcı Sebep`")

# ==========================================
# 7. ANTRENMAN VE PENALTI (.ant & .pen)
# ==========================================
@bot.command(name="ant")
async def antrenman(ctx):
    await ctx.send(f"🏋️‍♂️ {ctx.author.mention} antrenman yaptı!")

@bot.command(name="pen")
async def penalti(ctx):
    await ctx.send(f"⚽ {ctx.author.mention} penaltı kullandı!")

# Botu Çalıştırma
bot.run(os.getenv("TOKEN"))
