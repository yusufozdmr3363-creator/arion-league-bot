import discord
from discord.ext import commands
import random
import os

# Botun istemci (client/bot) ayarları (Intents açık)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı ve aktif!")

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
        name="🏟️ Canlı Maç & Simülasyon",
        value="• `.maç @EvSahibi @Deplasman` - 90 dakikalık canlı maç başlatır.",
        inline=False
    )
    
    embed.add_field(
        name="⚽ Bireysel Oyunlar & Kulüp Sistemleri",
        value="• `.pen` - Tek başına penaltı atıp gol arama mini oyunu.\n• `.ant` - Tek başına antrenman yapıp kondisyon kasma komutu.\n• `.kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde` - Resmi KAP transfer bildirimi.",
        inline=False
    )
    
    embed.add_field(
        name="📋 Kadro & Takım Sistemleri",
        value="• `.kadro @TakımRolü` - Takımın ana kadrosunu listeler.\n• `.yedekler @YedekRolü` - Yedek kulübesindeki oyuncuları gösterir.",
        inline=False
    )
    
    embed.add_field(
        name="✉️ Yönetim & Moderasyon",
        value="• `.dm [mesajın]` - Üyelere toplu duyuru gönderir *(Yönetici)*.\n• `.ban` / `.kick` / `.mute` / `.temizle` - Moderasyon komutları.",
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
# 3. PENALTI OYUNU SİSTEMİ (.pen)
# ==========================================
@bot.command(name="pen")
async def penaltı(ctx):
    sonuclar = ["gol", "gol", "gol", "kaleci kurtardı!", "direkten dışarı çıktı!", "üstten auta gitti!"]
     sonuc = random.choice(sonuclar)
    
    if sonuc == "gol":
        mesaj = f"⚽ **GOL!** Beyaz noktadan harika bir vuruş ve meşin yuvarlak ağlarla buluştu! Tebrikler {ctx.author.mention}! 🎯"
    else:
        mesaj = f"❌ **KAÇTI!** Penaltı atışında {sonuc} {ctx.author.mention}, şansını tekrar dene!"
        
    await ctx.send(mesaj)

# ==========================================
# 4. ANTRENMAN SİSTEMİ (.ant)
# ==========================================
@bot.command(name="ant")
async def antrenman(ctx):
    kazanc = random.randint(50, 200)
    await ctx.send(f"🏋️‍♂️ {ctx.author.mention} sahaya indi ve yoğun bir kondisyon antrenmanı gerçekleştirdi!\n> ⚡ Kazanılan Performans / Prim: **+{kazanc} Puan**")

# ==========================================
# 5. DİĞER TEMEL KOMUTLAR
# ==========================================
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Gecikme süresi: `{round(bot.latency * 1000)}ms`")

@bot.command(name="espri")
async def espri(ctx):
    await ctx.send("Geçen sünnetçi tıraşı oldum, kafadan 5 yaş gençleştim! 😄")

# Botu Çalıştırma (Railway Token Değişkeni)
bot.run(os.getenv("TOKEN"))
