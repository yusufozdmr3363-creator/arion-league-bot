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
son_gonderilenler = {}

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı ve aktif!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.mentions:
        for user in message.mentions:
            if user.id in afk_users:
                sebep = afk_users[user.id]
                await message.channel.send(f"💤 **{user.name}** şu an AFK!\n> **Sebep:** {sebep}")

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
        color=discord.Color.from_str("#FFD700")
    )
    
    embed.add_field(
        name="⚽ Oyun, Kulüp & Ekonomi Sistemleri",
        value="• `.ant` - Antrenman yapma komutu.\n• `.pen` - Penaltı düellosu (Futbolcu/Kaleci seçimi).\n• `.k @Etiket İsim | Mevki | Ülke | Değer` - Futbolcu kayıt sistemi.\n• `.dver @Etiket [sayı] [sebep]` - Oyuncunun değerini artırır.\n• `.dsil @Etiket [sayı] [sebep]` - Oyuncunun değerini azaltır.\n• `.pay @Etiket [miktar]M` - Belirtilen oyuncuya para gönderir.\n• `.bal [@Etiket]` - Oyuncunun bakiye/değer durumunu gösterir.\n• `.kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde` - Resmi KAP bildirimi.",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Özel Sistemler",
        value="• `.afk [sebep]` - AFK moduna geçer.",
        inline=False
    )
    
    embed.set_footer(text="Arion League")
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
    except:
        pass

    embed = discord.Embed(
        title="🔔 K.A.P. | KAMUYU AYDINLATMA PLATFORMU BİLDİRİMİ",
        description="Profesyonel futbolcu transferi hakkında resmi açıklama:\n________________________________",
        color=discord.Color.from_str("#FFD700")
    )
    
    embed.add_field(name="👤 Futbolcu", value=member.mention, inline=False)
    embed.add_field(name="🏢 Eski Takımı", value=eski_takim, inline=True)
    embed.add_field(name="🏟️ Yeni Takımı", value=yeni_takim, inline=True)
    embed.add_field(name="💶 Maaş", value=maas, inline=True)
    embed.add_field(name="⏳ Süre", value=sezon, inline=True)
    embed.add_field(name="💰 Bonservis", value=bonservis, inline=True)
    embed.add_field(name="📝 Özel Şartlar", value=ek_madde, inline=False)
    
    embed.set_footer(text="Arion League")

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
    embed = discord.Embed(
        title="💤 AFK Modu",
        description=f"{ctx.author.mention} başarıyla AFK moduna geçti.\n> **Sebep:** {sebep}",
        color=discord.Color.from_str("#3498DB")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

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
        await ctx.send("❌ Botun yetkisi yetersiz!")
        return

    embed = discord.Embed(
        title="✅ İşlem Başarılı",
        description=f"• **{member.mention}** adlı oyuncunun künyesi oluşturuldu ve ismi güncellendi!\n• **Yeni Künye:** `{veri}`",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.set_footer(text="Arion League")
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
        eski_str = f"{eski_sayi}{ek_harf}€"
        yeni_str = f"{yeni_sayi}{ek_harf}€"
        degisim_str = f"+{miktar}{ek_harf}€"
    else:
        yeni_nick = f"{eski_nick} | {miktar}M"
        eski_str = "Bilinmiyor"
        yeni_str = f"{miktar}M€"
        degisim_str = f"+{miktar}M€"

    try:
        await member.edit(nick=yeni_nick)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz!")
        return

    embed = discord.Embed(
        title="✅ İşlem Başarılı",
        description=f"• **{eski_nick}** adlı oyuncunun değeri başarıyla güncellendi!\n• **Değişim:** {eski_str} → {yeni_str} ({degisim_str})\n• **Sebep:** {sebep}",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.set_footer(text="Arion League")

    deger_kanali = bot.get_channel(DEGER_KANAL_ID)
    if deger_kanali:
        await deger_kanali.send(embed=embed)

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
        eski_str = f"{eski_sayi}{ek_harf}€"
        yeni_str = f"{yeni_sayi}{ek_harf}€"
        degisim_str = f"-{miktar}{ek_harf}€"
    else:
        yeni_nick = eski_nick
        eski_str = "Bilinmiyor"
        yeni_str = f"-{miktar}M€"
        degisim_str = f"-{miktar}M€"

    try:
        await member.edit(nick=yeni_nick)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz!")
        return

    embed = discord.Embed(
        title="✅ İşlem Başarılı",
        description=f"• **{eski_nick}** adlı oyuncunun değeri başarıyla güncellendi!\n• **Değişim:** {eski_str} → {yeni_str} ({degisim_str})\n• **Sebep:** {sebep}",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.set_footer(text="Arion League")

    deger_kanali = bot.get_channel(DEGER_KANAL_ID)
    if deger_kanali:
        await deger_kanali.send(embed=embed)

# ==========================================
# 7. PARA GÖNDERME SİSTEMİ (.pay)
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
        await ctx.send("❌ Yetersiz bakiye!")
        return

    g_mevcut = int(gonderen_match.group(1))
    g_harf = gonderen_match.group(2)
    yeni_gonderen_nick = re.sub(r'\d+[mM]?$', f"{g_mevcut - gonderilecek_miktar}{g_harf}", gonderen_nick)

    alici_match = re.search(r'(\d+)([mM]?)$', alicim_nick.strip())
    if alici_match:
        a_mevcut = int(alici_match.group(1))
        a_harf = alici_match.group(2)
        yeni_alici_nick = re.sub(r'\d+[mM]?$', f"{a_mevcut + gonderilecek_miktar}{a_harf}", alicim_nick)
    else:
        yeni_alici_nick = f"{alicim_nick} | {gonderilecek_miktar}M"

    try:
        await gonderen.edit(nick=yeni_gonderen_nick)
        await member.edit(nick=yeni_alici_nick)
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz!")
        return

    embed = discord.Embed(
        title="✅ İşlem Başarılı",
        description=f"• **Gönderen:** {gonderen.mention}\n• **Alıcı:** {member.mention}\n• **Miktar:** {gonderilecek_miktar}M€ transfer edildi!",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 8. BAKİYE KONTROL SİSTEMİ (.bal)
# ==========================================
@bot.command(name="bal")
async def bal(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    nick = member.display_name
    match = re.search(r'(\d+)([mM]?)$', nick.strip())
    bakiye = f"{match.group(1)}{match.group(2)}" if match else "Bakiye bulunamadı"

    embed = discord.Embed(
        title="💳 Bakiye / Künye Bilgisi",
        description=f"• **Oyuncu:** {member.mention}\n• **Mevcut Künye:** `{nick}`\n• **Güncel Değer:** `{bakiye}€`",
        color=discord.Color.from_str("#3498DB")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 9. ANTRENMAN SİSTEMİ (.ant)
# ==========================================
@bot.command(name="ant")
async def antrenman(ctx):
    embed = discord.Embed(
        title="💪 Antrenman Başarılı!",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.add_field(name="👤 Oyuncu", value=f"• {ctx.author.mention}", inline=False)
    embed.add_field(name="📊 İlerleme Durumu", value="• **Mevcut:** 1/5\n• **Kalan:** 4 antrenman\n• **Yüzde:** 10%", inline=False)
    embed.add_field(name="📈 Gelişim Çubuğu", value="█░░░░░░░░░ `10%`", inline=False)
    embed.add_field(name="⏳ Sonraki Antrenman", value="• 1 saat sonra", inline=False)
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 10. PENALTI DÜELLOSU SİSTEMİ (.pen)
# ==========================================
class PenaltiView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.secim = None

    @discord.ui.button(label="⚽ Futbolcu (Penaltı At)", style=discord.ButtonStyle.success)
    async def futbolcu_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Bu penaltıyı sen kullanamazsın!", ephemeral=True)
            return
        self.secim = "futbolcu"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🧤 Kaleci (Penaltı Kurtar)", style=discord.ButtonStyle.primary)
    async def kaleci_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Bu penaltıya müdahale edemezsin!", ephemeral=True)
            return
        self.secim = "kaleci"
        self.stop()
        await interaction.response.defer()

@bot.command(name="pen")
async def penalti(ctx):
    secim_embed = discord.Embed(
        title=f"🥅 Penaltı Düellosu — {ctx.author.name}",
        description="• **Soru:** Sahada hangi rolde olmak istiyorsun?\n> Lütfen aşağıdaki butonlardan birini seç:",
        color=discord.Color.from_str("#3498DB")
    )
    secim_embed.set_footer(text="Arion League")

    view = PenaltiView(ctx)
    mesaj = await ctx.send(embed=secim_embed, view=view)

    timed_out = await view.wait()
    
    if timed_out or view.secim is None:
        try:
            await mesaj.edit(content="⏳ Süre bittiği için penaltı iptal edildi.", embed=None, view=None)
        except:
            pass
        return

    yuzde = random.randint(10, 95)
    dolu_sayisi = round(yuzde / 10)
    bos_sayisi = 10 - dolu_sayisi
    cubuk = ("█" * dolu_sayisi) + ("░" * bos_sayisi)

    if view.secim == "futbolcu":
        if yuzde >= 75:
            durum_baslik = "⚽ GOL!"
            durum_aciklama = "Mükemmel bir vuruş ve top ağlarla buluştu!"
            renk = "#2ECC71"
        elif yuzde >= 50:
            durum_baslik = "💥 DİREK!"
            durum_aciklama = "Top direkten döndü! Az kalsın gol oluyordu."
            renk = "#F1C40F"
        elif yuzde >= 30:
            durum_baslik = "🚫 AUT!"
            durum_aciklama = "Vuruş dışarı gitti, top auta çıktı."
            renk = "#E67E22"
        else:
            durum_baslik = "🧤 KURTARILDI!"
            durum_aciklama = "Kaleci mükemmel uzandı ve şutunu çıkardı!"
            renk = "#E74C3C"

        sonuc_embed = discord.Embed(
            title=f"🥅 Penaltı Atışı — {ctx.author.name}",
            color=discord.Color.from_str(renk)
        )
        sonuc_embed.add_field(name=durum_baslik, value=durum_aciklama, inline=False)
        sonuc_embed.add_field(name="📊 Vuruş Kalitesi", value=f"{cubuk} %{yuzde}", inline=False)
        sonuc_embed.add_field(name="👤 Futbolcu", value=f"• {ctx.author.mention}", inline=False)

    else:
        if yuzde >= 70:
            durum_baslik = "🧤 İNANILMAZ BİR ŞUT KURTARDIN!"
            durum_aciklama = "Harika bir refleksle köşeden topu çeldin!"
            renk = "#2ECC71"
        elif yuzde >= 45:
            durum_baslik = "💥 RAKİP DİREKİ ÇELDİ"
            durum_aciklama = "Rakibin şutu direğe çarpıp dışarı çıktı, şanslısın!"
            renk = "#3498DB"
        elif yuzde >= 25:
            durum_baslik = "🚫 RAKİP AUTA ATTİ!"
            durum_aciklama = "Rakibin yaptığı vuruş kaleyi bulmadı, aut!"
            renk = "#F1C40F"
        else:
            durum_baslik = "😔 GOL YEDİN!"
            durum_aciklama = "Rakip çok düzgün vurdu, kalecinin yapacak bir şeyi yoktu."
            renk = "#E74C3C"

        sonuc_embed = discord.Embed(
            title=f"🥅 Kaleci Kurtarışı — {ctx.author.name}",
            color=discord.Color.from_str(renk)
        )
        sonuc_embed.add_field(name=durum_baslik, value=durum_aciklama, inline=False)
        sonuc_embed.add_field(name="📊 Kurtarma Performansı", value=f"{cubuk} %{yuzde}", inline=False)
        sonuc_embed.add_field(name="🧤 Kaleci", value=f"• {ctx.author.mention}", inline=False)

    sonuc_embed.set_footer(text="Arion League")
    
    # Burada yeni mesaj atmak yerine orijinal soru mesajını güncelliyoruz, böylece çift mesaj atmaz!
    await mesaj.edit(content=None, embed=sonuc_embed, view=None)

# Botu Çalıştırma
bot.run(os.getenv("TOKEN"))
