import discord
from discord.ext import commands
import random
import os
import re

# Botun istemci ayarları (Üye takibi için intents.members aktif edildi)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

# Bildirim ve Kanal Sabit ID'leri
KAP_KANAL_ID = 1529080307737825391
DEGER_KANAL_ID = 1529073718595158027
ANTRENMAN_KANAL_ID = 1539313925219291146
PENALTI_KANAL_ID = 1539314055603560518
HOSGELDIN_KANAL_ID = 1529073718595158027  # Hoş geldin kanalının ID'si

# Sosyal Medya Kanal ID'leri Listesi (.post komutunun atılabileceği kanallar)
SOSYAL_MEDYA_KANALLARI = [
    1529077559839690793,  # Instagram Kanalı
    1529077593800704031,  # TikTok Kanalı
    1529077633965363320   # Facebook Kanalı
]

# Veritabanları (AFK, Bakiye, Antrenman, Post Sayacı)
afk_users = {}
user_balances = {}  # Nakit para (Cüzdan)
user_ant_count = {} # Antrenman ilerlemesi
user_post_count = {} # Kullanıcı post sayaçları

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı ve aktif!")

# ==========================================
# 0. YENİ ÜYE KARŞILAMA SİSTEMİ (Hoş Geldin)
# ==========================================
@bot.event
async def on_member_join(member):
    hedef_kanal = member.guild.get_channel(HOSGELDIN_KANAL_ID)
    if not hedef_kanal:
        return

    toplam_uye = member.guild.member_count

    embed = discord.Embed(
        title="🌟 ARION LEAGUE AİLESİNE HOŞ GELDİN! 🌟",
        description=(
            f"Hey {member.mention}, futbolun kalbinin attığı yere, **Arion League** sunucusuna hoş geldin!\n\n"
            f"🎯 Seninle birlikte kocaman ailemiz **{toplam_uye}** kişiye ulaştı!\n\n"
            "> 📌 **İlk Adımlar:**\n"
            "> • Kuralları okumayı unutma.\n"
            "> • Yetkililerden kayıt olmayı veya künyeni almayı unutma.\n"
            "> • Transfer ve piyasa piyasasında yerini al!"
        ),
        color=discord.Color.from_str("#FFD700")
    )
    
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url=member.default_avatar.url)
        
    embed.set_footer(text="Arion League • İyi Eğlenceler Dileriz!")
    
    await hedef_kanal.send(content=f"Hoş geldin {member.mention}! 🎉", embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.mentions:
        for user in message.mentions:
            if user.id in afk_users:
                sebep = afk_users[user.id]
                embed = discord.Embed(
                    title="💤 AFK BİLDİRİMİ",
                    description=f"**{user.name}** şu an AFK!\n> **Sebep:** {sebep}",
                    color=discord.Color.from_str("#E67E22")
                )
                embed.set_footer(text="Arion League")
                await message.channel.send(embed=embed)

    if message.author.id in afk_users:
        del afk_users[message.author.id]
        embed = discord.Embed(
                    title="👋 AFK MODUNDAN ÇIKIŞ",
                    description=f"Hoş geldin {message.author.mention}! AFK modundan başarıyla çıktın.",
                    color=discord.Color.from_str("#2ECC71")
                )
        embed.set_footer(text="Arion League")
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# ==========================================
# 1. YARDIM MENÜSÜ (.komutlar)
# ==========================================
@bot.command(name="komutlar")
async def komutlar(ctx):
    embed = discord.Embed(
        title="🤖 ARION LEAGUE — TÜM KOMUTLAR LİSTESİ",
        description="Sunucumuzdaki tüm güncel komutlar aşağıdadır:\n________________________________",
        color=discord.Color.from_str("#FFD700")
    )
    
    sosyal_kanallar_str = ", ".join([f"<#{kid}>" for kid in SOSYAL_MEDYA_KANALLARI])
    
    embed.add_field(
        name="⚽ Oyun, Kulüp & Ekonomi Sistemleri",
        value=(
            f"• `.ant` - Antrenman yapma komutu (Yalnızca <#{ANTRENMAN_KANAL_ID}>).\n"
            f"• `.pen` - Penaltı düellosu (Yalnızca <#{PENALTI_KANAL_ID}>).\n"
            f"• `.post [mesaj]` - Sosyal medya gönderisi atmanızı sağlar (Yalnızca {sosyal_kanallar_str}).\n"
            "• `.k @Etiket İsim | Mevki | Ülke | Değer` - Futbolcu kayıt sistemi.\n"
            "• `.ara [oyuncu adı]` - Oyuncu araması yapar.\n"
            "• `.mevkiara [mevki]` - Sunucudaki o mevkiye sahip kişileri listeler.\n"
            "• `.dver @Etiket [sayı] [sebep]` - Oyuncunun piyasa değerini artırır.\n"
            "• `.dsil @Etiket [sayı] [sebep]` - Oyuncunun piyasa değerini azaltır.\n"
            "• `.pay @Etiket [miktar]M` - Belirtilen oyuncuya nakit para gönderir.\n"
            "• `.bal [@Etiket]` - Oyuncunun piyasa değerini ve nakit parasını gösterir.\n"
            "• `.Kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde` - Resmi KAP bildirimi."
        ),
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
# 2. POST SİSTEMİ (.post) - Yalnızca Sosyal Medya Kanalları
# ==========================================
@bot.command(name="post")
async def post(ctx, *, mesaj_icerik: str = None):
    if ctx.channel.id not in SOSYAL_MEDYA_KANALLARI:
        try:
            await ctx.message.delete()
        except:
            pass
            
        kanallar_metni = ", ".join([f"<#{kid}>" for kid in SOSYAL_MEDYA_KANALLARI])
        embed = discord.Embed(
            title="❌ YANLIŞ KANAL",
            description=f"Bu komutu yalnızca şu kanallarda kullanabilirsin:\n{kanallar_metni}",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        hata_mesaji = await ctx.send(embed=embed)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        try:
            await hata_mesaji.delete()
        except:
            pass
        return

    try:
        await ctx.message.delete()
    except:
        pass

    if not mesaj_icerik:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Göndermek istediğiniz mesajı yazmalısınız!\n> **Kullanım:** `.post [Mesajınız]`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    user_id = ctx.author.id
    mevcut_post = user_post_count.get(user_id, 0) + 1
    user_post_count[user_id] = mevcut_post

    nickname = ctx.author.display_name

    baslik_metni = f"### {nickname}\n________________________________\n\n{mesaj_icerik}\n\n### Bu kullanıcının {mevcut_post}. postu"

    embed = discord.Embed(
        title=baslik_metni,
        color=discord.Color.from_str("#3498DB")
    )
    embed.set_footer(text=f"Arion League • Gönderen: {ctx.author.name}")
    
    await ctx.send(embed=embed)

# ==========================================
# 3. KAP BİLDİRİMİ (.kap)
# ==========================================
@bot.command(name="kap")
async def kap(ctx, member: discord.Member = None, eski_takim: str = None, yeni_takim: str = None, maas: str = None, sezon: str = None, bonservis: str = None, *, ek_madde: str = "Belirtilmemiş"):
    if not member or not eski_takim or not yeni_takim or not maas or not sezon or not bonservis:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Eksik bilgi girdiniz!\n> **Kullanım:** `.Kap @Etiket EskiTakım YeniTakım Maaş Sezon Bonservis EkMadde`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
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
        hata_embed = discord.Embed(
            title="⚠️ HATA",
            description="KAP kanalı sistemde bulunamadı!",
            color=discord.Color.from_str("#E74C3C")
        )
        hata_embed.set_footer(text="Arion League")
        await ctx.send(hata_embed)

# ==========================================
# 4. AFK SİSTEMİ (.afk)
# ==========================================
@bot.command(name="afk")
async def afk(ctx, *, sebep: str = "Belirtilmemiş"):
    afk_users[ctx.author.id] = sebep
    embed = discord.Embed(
        title="💤 AFK MODU AKTİF",
        description=f"{ctx.author.mention} başarıyla AFK moduna geçti.\n> **Sebep:** {sebep}",
        color=discord.Color.from_str("#3498DB")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 5. OYUNCU ARAMA SİSTEMİ (.ara)
# ==========================================
@bot.command(name="ara")
async def oyuncu_ara(ctx, *, aranan_isim: str = None):
    if not aranan_isim:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Aramak istediğiniz oyuncunun adını yazmalısınız!\n> **Kullanım:** `.Ara [Oyuncu Adı]`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    ornek_mevkiler = ["Forvet", "Merkez Orta Saha", "Stoper", "Sol Kanat", "Sağ Kanat", "Kaleci"]
    rastgele_deger = random.randint(5, 45)
    rastgele_mevki = random.choice(ornek_mevkiler)
    
    embed = discord.Embed(
        title=f"🔍 OYUNCU RAPORU — {aranan_isim.upper()}",
        description=f"Gözlemcilerimiz **{aranan_isim}** için raporu tamamladı:\n________________________________",
        color=discord.Color.from_str("#3498DB")
    )
    embed.add_field(name="👤 Oyuncu adı", value=aranan_isim, inline=True)
    embed.add_field(name="📍 Mevki", value=rastgele_mevki, inline=True)
    embed.add_field(name="💰 Piyasa değeri", value=f"{rastgele_deger}M€", inline=True)
    embed.set_footer(text="Arion League Scout Ekibi")
    
    await ctx.send(embed=embed)

# ==========================================
# 6. MEVKİ ARAMA SİSTEMİ (.mevkiara)
# ==========================================
class MevkiAramaView(discord.ui.View):
    def __init__(self, sayfalar, ctx):
        super().__init__(timeout=60)
        self.sayfalar = sayfalar
        self.ctx = ctx
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == len(self.sayfalar) - 1

    @discord.ui.button(label="◀️ Önceki", style=discord.ButtonStyle.primary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Bu menüyü kullanamazsın!", ephemeral=True)
            return
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.sayfalar[self.current_page], view=self)

    @discord.ui.button(label="Sonraki ▶️", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Bu menüyü kullanamazsın!", ephemeral=True)
            return
        if self.current_page < len(self.sayfalar) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.sayfalar[self.current_page], view=self)

@bot.command(name="mevkiara")
async def mevki_ara(ctx, *, istenen_mevki: str = None):
    if not istenen_mevki:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Aramak istediğiniz mevkiyi yazmalısınız!\n> **Kullanım:** `.Mevkiara [Stoper / Forvet / Kaleci vb.]`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    bulunan_uygular = []
    
    for member in ctx.guild.members:
        nick = member.display_name
        if istenen_mevki.lower() in nick.lower():
            match = re.search(r'(\d+)([mM]?)$', nick.strip())
            deger = int(match.group(1)) if match else 0
            deger_str = f"{match.group(1)}{match.group(2)}€" if match else "Değer Yok"
            bulunan_uygular.append({
                "member": member,
                "nick": nick,
                "deger": deger,
                "deger_str": deger_str
            })

    if not bulunan_uygular:
        embed = discord.Embed(
            title=f"❌ OYUNCU BULUNAMADI",
            description=f"Sunucuda **{istenen_mevki}** mevkisine sahip herhangi bir oyuncu bulunamadı.",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    bulunan_uygular.sort(key=lambda x: x["deger"], reverse=True)

    chunk_size = 5
    sayfalar = []
    toplam_oyuncu = len(bulunan_uygular)
    toplam_sayfa = (toplam_oyuncu + chunk_size - 1) // chunk_size

    for i in range(0, toplam_oyuncu, chunk_size):
        parca = bulunan_uygular[i:i + chunk_size]
        
        embed = discord.Embed(
            title=f"🎯 MEVKİ TARAMASI — {istenen_mevki.upper()}",
            description=f"Sunucuda bu mevkide oynayan oyuncular (En yüksek değere göre sıralı):\n________________________________",
            color=discord.Color.from_str("#2ECC71")
        )

        for idx, oyuncu in enumerate(parca, start=i+1):
            embed.add_field(
                name=f"{idx}. {oyuncu['member'].display_name}",
                value=f"• **Kullanıcı:** {oyuncu['member'].mention}\n• **Piyasa Değeri:** `{oyuncu['deger_str']}`",
                inline=False
            )

        embed.set_footer(text=f"Arion League • Sayfa {len(sayfalar)+1}/{toplam_sayfa}")
        sayfalar.append(embed)

    if len(sayfalar) == 1:
        await ctx.send(embed=sayfalar[0])
    else:
        view = MevkiAramaView(sayfalar, ctx)
        await ctx.send(embed=sayfalar[0], view=view)

# ==========================================
# 7. OYUNCU KAYIT SİSTEMİ (.k)
# ==========================================
@bot.command(name="k")
@commands.has_permissions(manage_nicknames=True)
async def futbolcu_kayit(ctx, member: discord.Member, *, veri: str = None):
    if not veri:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Eksik bilgi girdiniz!\n> **Kullanım:** `.K @Etiket Oyuncu İsmi | Mevkisi | Ülkesi | 1M`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    try:
        await member.edit(nick=veri)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ YETKİ HATASI",
            description="Botun kullanıcı adını değiştirmek için yetkisi yetersiz!",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    sunucu_kisi_sayisi = ctx.guild.member_count

    embed = discord.Embed(
        title=f"Arion League Ailesine Hoş geldin {member.mention} Seninle Birlikte Sunucudaki {sunucu_kisi_sayisi}. kişi olduk",
        description=f"• **Oyuncu Künyesi:** `{veri}`\n• **İşlemi Yapan Yetkili:** {ctx.author.mention}",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 8. PİYASA DEĞERİ ARTIRMA SİSTEMİ (.dver)
# ==========================================
@bot.command(name="dver")
@commands.has_permissions(manage_nicknames=True)
async def deger_ver(ctx, member: discord.Member, miktar: int, *, sebep: str = "Sebep belirtilmedi"):
    try:
        await ctx.message.delete()
    except:
        pass

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
        embed = discord.Embed(
            title="❌ YETKİ HATASI",
            description="Botun piyasa değerini güncellemek için yetkisi yetersiz!",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="📈 PİYASA DEĞERİ ARTIRILDI",
        description=f"• **{eski_nick}** adlı oyuncunun piyasa değeri başarıyla güncellendi!\n• **Değişim:** {eski_str} → {yeni_str} ({degisim_str})\n• **Sebep:** {sebep}",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.add_field(name="🛡️ İşlemi Yapan Yetkili", value=ctx.author.mention, inline=True)
    embed.add_field(name="📺 İşlem Yapılan Kanal", value=ctx.channel.mention, inline=True)
    embed.set_footer(text="Arion League")

    await ctx.send(embed=embed)

    deger_kanali = bot.get_channel(DEGER_KANAL_ID)
    if deger_kanali:
        form_embed = discord.Embed(
            title="🔔 Arion League Değer Bildirim Raporu",
            color=discord.Color.from_str("#2ECC71")
        )
        form_embed.add_field(name="👤 Oyuncu", value=member.mention, inline=False)
        form_embed.add_field(name="❔ Sebep", value=sebep, inline=False)
        form_embed.add_field(name="📈 Kaçtan Kaça", value=f"{eski_str} → {yeni_str} (+{miktar}M)", inline=False)
        form_embed.add_field(name="🛠️ Değeri Veren Yetkili", value=ctx.author.mention, inline=False)
        form_embed.set_footer(text="Arion League")
        
        await deger_kanali.send(embed=form_embed)

# ==========================================
# 9. PİYASA DEĞERİ AZALTMA SİSTEMİ (.dsil)
# ==========================================
@bot.command(name="dsil")
@commands.has_permissions(manage_nicknames=True)
async def deger_sil(ctx, member: discord.Member, miktar: int, *, sebep: str = "Sebep belirtilmedi"):
    try:
        await ctx.message.delete()
    except:
        pass

    eski_nick = member.display_name
    match = re.search(r'(\d+)([mM]?)$', eski_nick.strip())
    
    if match:
        eski_sayi = int(match.group(1))
        ek_harf = match.group(2)
        yeni_sayi = max(0, eski_sayi - miktar)
        yeni_nick = r
