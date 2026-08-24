

import discord
from discord.ext import commands
import random
import os
import re

# Botun istemci ayarları
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# Bildirim Kanallarının Sabit ID'leri
KAP_KANAL_ID = 1529080307737825391
DEGER_KANAL_ID = 1529073718595158027

# AFK olan kullanıcıları tutmak için sözlük
afk_users = {}

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı ve aktif!")

@bot.event
async def on_message(message):
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

    await bot.process_commands(message)

# ==========================================
# 1. YARDIM MENÜSÜ (.komutlar)
# ==========================================
@bot.command(name="komutlar")
async def komutlar(ctx):
    embed = discord.Embed(
        title="🤖 FUTBOL & SUNUCU BOTU - TÜM KOMUTLAR",
        description="Sunucumuzdaki tüm güncel komutlar aşağıdadır:\n________________________________",
        color=discord.Color.yellow()
    )
    
    embed.add_field(
        name="⚽ Oyun, Kulüp & Ekonomi Sistemleri",
        value="• `.ant` - Antrenman yapma komutu.\n• `.pen` - Penaltı atma komutu.\n• `.k @Etiket İsim | Mevki | Ülke | Değer` - Futbolcu kayıt sistemi.\n• `.dver @Etiket [sayı] [sebep]` - Oyuncunun değerini artırır.\n• `.dsil @Etiket [sayı] [sebep]` - Oyuncunun değerini azaltır.\n• `.pay @Etiket [miktar]M` - Belirtilen oyuncuya para gönderir.\n• `.bal [@Etiket]` - Oyuncunun bakiye/değer durumunu gösterir.\n• `.kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde` - Resmi KAP bildirimi.",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Özel Sistemler",
        value="• `.afk [sebep]` - AFK moduna geçer.",
        inline=False
    )
    
    embed.set_footer(text="Arion League Bot Sistemleri")
    await ctx.send(embed=embed)

# ==========================================
# 2. KAP BİLDİRİMİ (.kap)
# ==========================================
@bot.command(name="kap")
async def kap(ctx, member: discord.Member = None, eski_takim: str = None, yeni_takim: str = None, maas: str = None, sezon: str = None, bonservis: str = None, *, ek_madde: str = "Belirtilmemiş"):
    if not member or not eski_takim or not yeni_takim or not maas or not sezon or not bonservis:
        await ctx.send("❌ Eksik bilgi girdiniz!\n> **Kullanım:** `.kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde`")
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    except discord.HTTPException:
        pass

    embed = discord.Embed(
        title="🔔 K.A.P. | KAMUYU AYDINLATMA PLATFORMU BİLDİRİMİ",
        description="Profesyonel futbolcu transferi hakkında resmi açıklama:\n________________________________",
        color=discord.Color.yellow()
    )
    
    embed.add_field(name="👤 Futbolcu", value=member.mention, inline=False)
    embed.add_field(name="🏢 Eski Takımı", value=eski_takim, inline=True)
    embed.add_field(name="🏟️ Yeni Takımı", value=yeni_takim, inline=True)
    embed.add_field(name="💶 Maaş", value=maas, inline=True)
    embed.add_field(name="⏳ Süre", value=sezon, inline=True)
    embed.add_field(name="💰 Bonservis", value=bonservis, inline=True)
    embed.add_field(name="📝 Özel Şartlar", value=ek_madde, inline=False)
    
    embed.set_footer(text=f"Bildiren: {ctx.author.name}")

    hedef_kanal = bot.get_channel(KAP_KANAL_ID)

    if hedef_kanal:
        await hedef_kanal.send(embed=embed)
    else:
        await ctx.send("⚠️ KAP kanalı bulunamadı:", embed=embed)

# ==========================================
# 3. AFK SİSTEMİ (.afk)
# ==========================================
@bot.command(name="afk")
async def afk(ctx, *, sebep: str = "Belirtilmemiş"):
    afk_users[ctx.author.id] = sebep
    await ctx.send(f"💤 {ctx.author.mention} başarıyla AFK moduna geçti.\n> **Sebep:** {sebep}")

# ==========================================
# 4. OYUNCU KAYIT SİSTEMİ (.k)
# ==========================================
@bot.command(name="k")
@commands.has_permissions(manage_nicknames=True)
async def futbolcu_kayit(ctx, member: discord.Member, *, veri: str = None):
    if not veri:
        await ctx.send("❌ Eksik bilgi girdiniz!\n> **Kullanım:** `.k @etiket Oyuncu ismi | Mevkisi | Ülkesi | 1M`")
        return

    try:
        await member.edit(nick=veri)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz! Kullanıcının rolü botun rolünden üstte olabilir.")
        return

    embed = discord.Embed(
        title="⚽ Başarılı Futbolcu Kaydı",
        description="Oyuncu künyesi oluşturuldu ve ismi güncellendi.",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="👤 Oyuncu", value=member.mention, inline=False)
    embed.add_field(name="📋 Yeni Künye", value=f"`{veri}`", inline=False)
    embed.set_footer(text="Arion League Oyuncu Sistemi")
    
    await ctx.send(embed=embed)

# ==========================================
# 5. DEĞER ARTIRMA SİSTEMİ (.dver)
# ==========================================
@bot.command(name="dver")
@commands.has_permissions(manage_nicknames=True)
async def deger_ver(ctx, member: discord.Member, miktar: int, *, sebep: str = "Sebep belirtilmedi"):
    eski_nick = member.display_name
    match = re.search(r'(\d+)([mM]?)$', eski_nick.strip())
    
    if match:
        eski_sayi = int(match.group(1))
        ek_harf = match.group(2)
        yeni_sayi = eski_sayi + miktar
        yeni_nick = re.sub(r'\d+[mM]?$', f"{yeni_sayi}{ek_harf}", eski_nick)
        kac_tan_kaca_str = f"{eski_sayi}{ek_harf} --> {yeni_sayi}{ek_harf}"
    else:
        yeni_nick = f"{eski_nick} | {miktar}M"
        kac_tan_kaca_str = f"Bilinmiyor --> {miktar}M"

    try:
        await member.edit(nick=yeni_nick)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz!")
        return

    # Komut yazılan yerdeki gereksiz mesajı silmeye çalış (varsa)
    try:
        await ctx.message.delete()
    except:
        pass

    # Sadece değer bildirme kanalına tek bir blok mesaj atılır
    deger_mesaji = (
        f"> **__Arion League Değer Bildirme Formu__**\n"
        f"> 👤┇**Oyuncu:** {member.mention}\n"
        f"> \n"
        f"> ❔┇**Sebep:** {sebep}\n"
        f"> \n"
        f"> ⚡┇**Kaçtan Kaça:** {kac_tan_kaca_str}\n"
        f"> \n"
        f"> 🛠️┇**Değeri Veren Yetkili:** {ctx.author.mention}"
    )

    deger_kanali = bot.get_channel(DEGER_KANAL_ID)
    if deger_kanali:
        await deger_kanali.send(deger_mesaji)
    else:
        await ctx.send("⚠️ Değer kanalı bulunamadı!")

# ==========================================
# 6. DEĞER AZALTMA SİSTEMİ (.dsil)
# ==========================================
@bot.command(name="dsil")
@commands.has_permissions(manage_nicknames=True)
async def deger_sil(ctx, member: discord.Member, miktar: int, *, sebep: str = "Sebep belirtilmedi"):
    eski_nick = member.display_name
    match = re.search(r'(\d+)([mM]?)$', eski_nick.strip())
    
    if match:
        eski_sayi = int(match.group(1))
        ek_harf = match.group(2)
        yeni_sayi = max(0, eski_sayi - miktar)
        yeni_nick = re.sub(r'\d+[mM]?$', f"{yeni_sayi}{ek_harf}", eski_nick)
        kac_tan_kaca_str = f"{eski_sayi}{ek_harf} --> {yeni_sayi}{ek_harf}"
    else:
        yeni_nick = eski_nick
        kac_tan_kaca_str = f"Bilinmiyor --> -{miktar}M"

    try:
        await member.edit(nick=yeni_nick)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz!")
        return

    try:
        await ctx.message.delete()
    except:
        pass

    # Sadece değer bildirme kanalına tek bir blok mesaj atılır
    azaltma_mesaji = (
        f"> **__Arion League Değer Azaltma Formu__**\n"
        f"> 👤┇**Oyuncu:** {member.mention}\n"
        f"> \n"
        f"> ❔┇**Sebep:** {sebep}\n"
        f"> \n"
        f"> ⚡┇**Kaçtan Kaça:** {kac_tan_kaca_str}\n"
        f"> \n"
        f"> 🛠️┇**Değeri Silen Yetkili:** {ctx.author.mention}"
    )

    deger_kanali = bot.get_channel(DEGER_KANAL_ID)
    if deger_kanali:
        await deger_kanali.send(azaltma_mesaji)
    else:
        await ctx.send("⚠️ Değer kanalı bulunamadı!")

# ==========================================
# 7. PARA GÖNDERME SİSTEMİ (.pay @etiket 2M)
# ==========================================
@bot.command(name="pay")
async def pay(ctx, member: discord.Member, miktar_str: str):
    match_miktar = re.search(r'(\d+)', miktar_str)
    if not match_miktar:
        await ctx.send("❌ Geçersiz miktar! Örnek kullanım: `.pay @etiket 2M`")
        return
    
    gonderilecek_miktar = int(match_miktar.group(1))
    gonderen = ctx.author

    gonderen_nick = gonderen.display_name
    alicim_nick = member.display_name

    gonderen_match = re.search(r'(\d+)([mM]?)$', gonderen_nick.strip())
    if not gonderen_match or int(gonderen_match.group(1)) < gonderilecek_miktar:
        await ctx.send("❌ Yetersiz bakiye! İsminin sonundaki miktar göndermek istediğin tutardan az.")
        return

    g_mevcut = int(gonderen_match.group(1))
    g_harf = gonderen_match.group(2)
    g_yeni_sayi = g_mevcut - gonderilecek_miktar
    yeni_gonderen_nick = re.sub(r'\d+[mM]?$', f"{g_yeni_sayi}{g_harf}", gonderen_nick)

    alici_match = re.search(r'(\d+)([mM]?)$', alicim_nick.strip())
    if alici_match:
        a_mevcut = int(alici_match.group(1))
        a_harf = alici_match.group(2)
        a_yeni_sayi = a_mevcut + gonderilecek_miktar
        yeni_alici_nick = re.sub(r'\d+[mM]?$', f"{a_yeni_sayi}{a_harf}", alicim_nick)
    else:
        yeni_alici_nick = f"{alicim_nick} | {gonderilecek_miktar}M"

    try:
        await gonderen.edit(nick=yeni_gonderen_nick)
        await member.edit(nick=yeni_alici_nick)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz! Kullanıcıların rolleri botun rolünden üstte olabilir.")
        return

    embed = discord.Embed(
        title="💸 Para Transferi Başarılı",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="📤 Gönderen", value=gonderen.mention, inline=True)
    embed.add_field(name="📥 Alıcı", value=member.mention, inline=True)
    embed.add_field(name="💰 Miktar", value=f"{gonderilecek_miktar}M", inline=False)
    embed.set_footer(text="Arion League Ekonomi Sistemi")
    await ctx.send(embed=embed)

# ==========================================
# 8. BAKİYE KONTROL SİSTEMİ (.bal / .bal @etiket)
# ==========================================
@bot.command(name="bal")
async def bal(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    nick = member.display_name
    match = re.search(r'(\d+)([mM]?)$', nick.strip())

    if match:
        bakiye = f"{match.group(1)}{match.group(2)}"
    else:
        bakiye = "Bakiye bulunamadı (Format uymuyor)"

    embed = discord.Embed(
        title="💳 Bakiye / Künye Bilgisi",
        color=discord.Color.from_rgb(52, 152, 219)
    )
    embed.add_field(name="👤 Oyuncu", value=member.mention, inline=False)
    embed.add_field(name="🏷️ Mevcut Künye / Değer", value=f"`{nick}`\n💰 **Güncel Değer:** `{bakiye}`", inline=False)
    embed.set_footer(text="Arion League Ekonomi Sistemi")
    await ctx.send(embed=embed)

# ==========================================
# 9. ANTRENMAN SİSTEMİ (.ant)
# ==========================================
@bot.command(name="ant")
async def antrenman(ctx):
    embed = discord.Embed(
        title="💪 Antrenman Başarılı!",
        color=discord.Color.from_rgb(45, 185, 110)
    )
    
    embed.add_field(
        name="👤 Oyuncu",
        value=f"• {ctx.author.mention}",
        inline=False
    )
    
    embed.add_field(
        name="📊 İlerleme Durumu",
        value="• **Mevcut:** 1/5\n• **Kalan:** 4 antrenman\n• **Yüzde:** 10%",
        inline=False
    )
    
    embed.add_field(
        name="📈 Gelişim Çubuğu",
        value="█░░░░░░░░░ `10%`",
        inline=False
    )
    
    embed.add_field(
        name="⏳ Sonraki Antrenman",
        value="• 1 saat sonra",
        inline=False
    )
    
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 10. PENALTI SİSTEMİ (.pen)
# ==========================================
@bot.command(name="pen")
async def penalti(ctx):
    yuzde = random.randint(15, 95)
    dolu_sayisi = round(yuzde / 10)
    bos_sayisi = 10 - dolu_sayisi
    cubuk = ("█" * dolu_sayisi) + ("░" * bos_sayisi)

    if yuzde >= 70:
        durum_baslik = "⚽ GOL!"
        durum_aciklama = "Mükemmel bir vuruş ve top ağlarla buluştu!"
        embed_renk = discord.Color.from_rgb(46, 204, 113)
    elif yuzde >= 40:
        durum_baslik = "🪵 DİREK!"
        durum_aciklama = "Top direkten döndü! Az kalsın gol oluyordu."
        embed_renk = discord.Color.from_rgb(241, 196, 15)
    else:
        durum_baslik = "❌ KAÇTI / KURTARILDI!"
        durum_aciklama = "Kaleci mükemmel uzandı ve gole izin vermedi!"
        embed_renk = discord.Color.from_rgb(231, 76, 60)

    embed = discord.Embed(
        title=f"🥅 Penaltı — {ctx.author.name}",
        color=embed_renk
    )
    
    embed.add_field(
        name=durum_baslik,
        value=durum_aciklama,
        inline=False
    )
    
    embed.add_field(
        name="📊 Vuruş Kalitesi",
        value=f"{cubuk} %{yuzde}",
        inline=False
    )
    
    embed.add_field(
        name="👤 Atan",
        value=f"• {ctx.author.mention}",
        inline=False
    )
    
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# Botu Çalıştırma
bot.run(os.getenv("TOKEN"))
