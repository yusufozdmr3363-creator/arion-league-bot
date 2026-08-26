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

# Veritabanları (AFK, Bakiye, Antrenman, Post Sayaçları)
afk_users = {}
user_balances = {}  # Nakit para (Cüzdan)
user_ant_count = {} # Antrenman ilerlemesi
user_post_count = {} # Kullanıcı post sayaçları

@bot.event
async def on_ready():
    print(f"{bot.user.name} başarıyla giriş yaptı ve aktif!")

# ==========================================
# 0. YENİ ÜYE KARŞILAMA SİSTEMİ
# ==========================================
@bot.event
async def on_member_join(member):
    hedef_kanal = member.guild.get_channel(HOSGELDIN_KANAL_ID)
    if not hedef_kanal:
        return

    sunucu_kisi_sayisi = member.guild.member_count

    embed = discord.Embed(
        title=f"Arion League Ailesine Hoş geldin {member.mention} Seninle Birlikte Sunucudaki {sunucu_kisi_sayisi}. kişi olduk",
        description="• **Durum:** Sunucuya yeni katıldı!\n• **Bilgilendirme:** Lütfen yetkililerden kayıt olmayı unutma.",
        color=discord.Color.from_str("#FFD700")
    )
    
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url=member.default_avatar.url)
        
    embed.set_footer(text="Arion League")
    
    await hedef_kanal.send(content=f"{member.mention}", embed=embed)

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
            "• `.ara [oyuncu adı]` - Yazılan futbolcuyu gösterir.\n"
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
        name="🛠️ Özel & Yetkili Sistemler",
        value=(
            "• `.afk [sebep]` - AFK moduna geçer.\n"
            "• `.lock [#kanal]` - Kanalı mesaj gönderimine kapatır.\n"
            "• `.unlock [#kanal]` - Kanalın kilidini açar.\n"
            "• `.dm @Etiket [mesaj]` - Belirtilen kişiye başlıklı özel mesaj (DM) gönderir."
        ),
        inline=False
    )
    
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 2. POST SİSTEMİ (.post)
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

    embed = discord.Embed(
        title=f"👤┇Oyuncu: {nickname}",
        color=discord.Color.from_str("#3498DB")
    )
    
    embed.add_field(name="Mesajı", value=mesaj_icerik, inline=False)
    embed.add_field(name="Günün Kaçıncı Postu", value=f"__{mevcut_post}. postu__", inline=False)
    
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
# 5. OYUNCU GÖSTERME SİSTEMİ (.ara) — GÜNCELLENDİ
# ==========================================
@bot.command(name="ara")
async def oyuncu_ara(ctx, *, aranan_isim: str = None):
    if not aranan_isim:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Aramak istediğiniz futbolcunun adını yazmalısınız!\n> **Kullanım:** `.ara [Futbolcu Adı]`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title=f"⚽ FUTBOLCU BİLGİSİ",
        description=f"• **Aranan Oyuncu:** **{aranan_isim}**",
        color=discord.Color.from_str("#3498DB")
    )
    embed.set_footer(text="Arion League")
    
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
        embed = discord.Embed(
            title="❌ YETKİ HATASI",
            description="Botun piyasa değerini düşürmek için yetkisi yetersiz!",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="📉 PİYASA DEĞERİ DÜŞÜRÜLDÜ",
        description=f"• **{eski_nick}** adlı oyuncunun piyasa değeri başarıyla güncellendi!\n• **Değişim:** {eski_str} → {yeni_str} ({degisim_str})\n• **Sebep:** {sebep}",
        color=discord.Color.from_str("#E74C3C")
    )
    embed.add_field(name="🛡️ İşlemi Yapan Yetkili", value=ctx.author.mention, inline=True)
    embed.add_field(name="📺 İşlem Yapılan Kanal", value=ctx.channel.mention, inline=True)
    embed.set_footer(text="Arion League")

    await ctx.send(embed=embed)

    deger_kanali = bot.get_channel(DEGER_KANAL_ID)
    if deger_kanali:
        form_embed = discord.Embed(
            title="🔔 Arion League Değer Düşüş Raporu",
            color=discord.Color.from_str("#E74C3C")
        )
        form_embed.add_field(name="👤 Oyuncu", value=member.mention, inline=False)
        form_embed.add_field(name="❔ Sebep", value=sebep, inline=False)
        form_embed.add_field(name="📈 Kaçtan Kaça", value=f"{eski_str} → {yeni_str} (-{miktar}M)", inline=False)
        form_embed.add_field(name="🛠️ Değeri Silen Yetkili", value=ctx.author.mention, inline=False)
        form_embed.set_footer(text="Arion League")
        
        await deger_kanali.send(embed=form_embed)

# ==========================================
# 10. NAKİT PARA GÖNDERME SİSTEMİ (.pay)
# ==========================================
@bot.command(name="pay")
async def pay(ctx, member: discord.Member, miktar_str: str):
    match_miktar = re.search(r'(\d+)', miktar_str)
    if not match_miktar:
        embed = discord.Embed(
            title="❌ GEÇERSİZ MİKTAR",
            description="Geçersiz miktar! Örnek kullanım: `.Pay @Etiket 2M`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return
    
    gonderilecek_miktar = int(match_miktar.group(1))
    gonderen = ctx.author

    is_owner = ctx.guild and gonderen == ctx.guild.owner

    if not is_owner:
        gonderen_bakiye = user_balances.get(gonderen.id, 0)
        if gonderen_bakiye < gonderilecek_miktar:
            embed = discord.Embed(
                title="❌ YETERSİZ BAKİYE",
                description=f"Yetersiz bakiye! Mevcut nakit paranız: **{gonderen_bakiye}M€**",
                color=discord.Color.from_str("#E74C3C")
            )
            embed.set_footer(text="Arion League")
            await ctx.send(embed=embed)
            return
        user_balances[gonderen.id] = gonderen_bakiye - gonderilecek_miktar

    alici_bakiye = user_balances.get(member.id, 0)
    user_balances[member.id] = alici_bakiye + gonderilecek_miktar

    gonderen_gosterge = "Sınırsız (Kurucu)" if is_owner else f"{user_balances.get(gonderen.id, 0)}M€"

    embed = discord.Embed(
        title="💸 PARA TRANSFERİ BAŞARILI",
        description=f"• **Gönderen:** {gonderen.mention} (Kalan: {gonderen_gosterge})\n• **Alıcı:** {member.mention} (Yeni: {user_balances[member.id]}M€)\n• **Gönderilen Tutar:** {gonderilecek_miktar}M€",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 11. BAKİYE / KÜNYE BİLGİSİ (.bal)
# ==========================================
@bot.command(name="bal")
async def bal(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    nick = member.display_name
    match = re.search(r'(\d+)([mM]?)$', nick.strip())
    piyasa_degeri = f"{match.group(1)}{match.group(2)}€" if match else "Bulunamadı"

    nakit_para = user_balances.get(member.id, 0)

    embed = discord.Embed(
        title="💳 OYUNCU BAKİYE VE KÜNYE BİLGİSİ",
        description=f"• **Oyuncu:** {member.mention}\n• **Künye:** `{nick}`\n• **Piyasa Değeri:** `{piyasa_degeri}`\n• **Nakit Para (Cüzdan):** `{nakit_para}M€`",
        color=discord.Color.from_str("#3498DB")
    )
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 12. KANAL KİLİTLEME SİSTEMİ (.lock & .unlock)
# ==========================================
@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock(ctx, kanal: discord.TextChannel = None):
    hedef_kanal = kanal or ctx.channel
    try:
        await ctx.message.delete()
    except:
        pass

    await hedef_kanal.set_permissions(ctx.guild.default_role, send_messages=False)
    
    embed = discord.Embed(
        title="🔒 KANAL KİLİTLENDİ",
        description=f"• **{hedef_kanal.mention}** kanalı yetkili tarafından üyelerin mesaj gönderimine kapatıldı.",
        color=discord.Color.from_str("#E74C3C")
    )
    embed.add_field(name="🛡️ İşlemi Yapan Yetkili", value=ctx.author.mention, inline=False)
    embed.set_footer(text="Arion League")
    
    await ctx.send(embed=embed)

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, kanal: discord.TextChannel = None):
    hedef_kanal = kanal or ctx.channel
    try:
        await ctx.message.delete()
    except:
        pass

    await hedef_kanal.set_permissions(ctx.guild.default_role, send_messages=None)
    
    embed = discord.Embed(
        title="🔓 KANAL AÇILDI",
        description=f"• **{hedef_kanal.mention}** kanalının kilidi kaldırıldı, üyeler artık mesaj yazabilir.",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.add_field(name="🛡️ İşlemi Yapan Yetkili", value=ctx.author.mention, inline=False)
    embed.set_footer(text="Arion League")
    
    await ctx.send(embed=embed)

# ==========================================
# 13. ÖZEL MESAJ (DM) GÖNDERME SİSTEMİ (.dm)
# ==========================================
@bot.command(name="dm")
@commands.has_permissions(manage_messages=True)
async def dm_gonder(ctx, member: discord.Member, *, mesaj: str = None):
    if not mesaj:
        embed = discord.Embed(
            title="❌ EKSİK BİLGİ",
            description="Kullanıcıya göndermek istediğiniz mesajı yazmalısınız!\n> **Kullanım:** `.dm @Etiket [Mesajınız]`",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    try:
        await ctx.message.delete()
    except:
        pass

    try:
        embed = discord.Embed(
            title="📩 ARION LEAGUE — YETKİLİ BİLDİRİMİ",
            description=f"{mesaj}",
            color=discord.Color.from_str("#3498DB")
        )
        embed.set_footer(text=f"Arion League • Gönderen Yetkili: {ctx.author.name}")
        await member.send(embed=embed)

        basarili_embed = discord.Embed(
            title="✅ DM GÖNDERİLDİ",
            description=f"{member.mention} adlı kullanıcıya özel mesajı başarıyla gönderildi.",
            color=discord.Color.from_str("#2ECC71")
        )
        basarili_embed.set_footer(text="Arion League")
        temp_msg = await ctx.send(embed=basarili_embed)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=4))
        try:
            await temp_msg.delete()
        except:
            pass

    except discord.Forbidden:
        hata_embed = discord.Embed(
            title="❌ HATA",
            description=f"{member.mention} adlı kullanıcının özel mesajları (DM) kapalı olduğu için mesaj gönderilemedi.",
            color=discord.Color.from_str("#E74C3C")
        )
        hata_embed.set_footer(text="Arion League")
        await ctx.send(hata_embed)

# ==========================================
# 14. ANTRENMAN SİSTEMİ (.ant)
# ==========================================
@bot.command(name="ant")
async def antrenman(ctx):
    if ctx.channel.id != ANTRENMAN_KANAL_ID:
        embed = discord.Embed(
            title="❌ YANLIŞ KANAL",
            description=f"Bu komutu yalnızca <#{ANTRENMAN_KANAL_ID}> kanalında kullanabilirsin!",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    user_id = ctx.author.id
    
    mevcut_sayi = user_ant_count.get(user_id, 0)
    mevcut_sayi += 1
    if mevcut_sayi > 5:
        mevcut_sayi = 1
        
    user_ant_count[user_id] = mevcut_sayi
    
    yuzde = mevcut_sayi * 20
    dolu_sayisi = mevcut_sayi * 2
    bos_sayisi = 10 - dolu_sayisi
    cubuk = ("█" * dolu_sayisi) + ("░" * bos_sayisi)
    kalan = 5 - mevcut_sayi

    embed = discord.Embed(
        title="💪 ANTRENMAN TAMAMLANDI",
        color=discord.Color.from_str("#2ECC71")
    )
    embed.add_field(name="👤 Oyuncu", value=f"• {ctx.author.mention}", inline=False)
    embed.add_field(name="📊 İlerleme Durumu", value=f"• **Mevcut:** {mevcut_sayi}/5\n• **Kalan:** {kalan} antrenman\n• **Yüzde:** %{yuzde}", inline=False)
    embed.add_field(name="📈 Gelişim Çubuğu", value=f"{cubuk} `%{yuzde}`", inline=False)
    embed.add_field(name="⏳ Sonraki Antrenman", value="• 1 saat sonra", inline=False)
    embed.set_footer(text="Arion League")
    await ctx.send(embed=embed)

# ==========================================
# 15. PENALTI DÜELLOSU SİSTEMİ (.pen)
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
    if ctx.channel.id != PENALTI_KANAL_ID:
        embed = discord.Embed(
            title="❌ YANLIŞ KANAL",
            description=f"Bu komut yalnızca <#{PENALTI_KANAL_ID}> kanalında kullanılabilir!",
            color=discord.Color.from_str("#E74C3C")
        )
        embed.set_footer(text="Arion League")
        await ctx.send(embed=embed)
        return

    secim_embed = discord.Embed(
        title=f"🥅 PENALTI DÜELLOSU — {ctx.author.name}",
        description="• **Soru:** Sahada hangi rolde olmak istiyorsun?\n> Lütfen aşağıdaki butonlardan birini seç:",
        color=discord.Color.from_str("#3498DB")
    )
    secim_embed.set_footer(text="Arion League")

    view = PenaltiView(ctx)
    mesaj = await ctx.send(embed=secim_embed, view=view)

    timed_out = await view.wait()
    
    if timed_out or view.secim is None:
        try:
            timeout_embed = discord.Embed(
                title="⏳ SÜRE BİTTİ",
                description="Süre bittiği için penaltı düellosu iptal edildi.",
                color=discord.Color.from_str("#E74C3C")
            )
            timeout_embed.set_footer(text="Arion League")
            await mesaj.edit(content=None, embed=timeout_embed, view=None)
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
            title=f"🥅 PENALTI ATIŞI SONUCU — {ctx.author.name}",
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
            durum_baslik = "💥 RAKİP DİREĞE ÇARPTI"
            durum_aciklama = "Rakibin şutu direğe çarpıp dışarı çıktı, şanslısın!"
            renk = "#3498DB"
        elif yuzde >= 25:
            durum_baslik = "🚫 RAKİP AUTA ATTI!"
            durum_aciklama = "Rakibin yaptığı vuruş kaleyi bulmadı, aut!"
            renk = "#F1C40F"
        else:
            durum_baslik = "😔 GOL YEDİN!"
            durum_aciklama = "Rakip çok düzgün vurdu, kalecinin yapacak bir şeyi yoktu."
            renk = "#E74C3C"

        sonuc_embed = discord.Embed(
            title=f"🥅 KALECİ KURTARIŞ SONUCU — {ctx.author.name}",
            color=discord.Color.from_str(renk)
        )
        sonuc_embed.add_field(name=durum_baslik, value=durum_aciklama, inline=False)
        sonuc_embed.add_field(name="📊 Kurtarma Performansı", value=f"{cubuk} %{yuzde}", inline=False)
        sonuc_embed.add_field(name="🧤 Kaleci", value=f"• {ctx.author.mention}", inline=False)

    sonuc_embed.set_footer(text="Arion League")
    await mesaj.edit(content=None, embed=sonuc_embed, view=None)

# Botu Çalıştırma
bot.run(os.getenv("TOKEN"))
