# Son gönderilen mesajları takip etmek için geçici bir hafıza
son_gonderilenler = {}

# ==========================================
# 5. DEĞER ARTIRMA SİSTEMİ (.dver)
# ==========================================
@bot.command(name="dver")
@commands.has_permissions(manage_nicknames=True)
async def deger_ver(ctx, member: discord.Member, miktar: int, *, sebep: str = "Sebep belirtilmedi"):
    # Aynı komutun 2 saniye içinde tekrar tetiklenmesini engelle
    mesaj_anahtari = (ctx.author.id, member.id, miktar, sebep)
    if mesaj_anahtari in son_gonderilenler:
        return
    son_gonderilenler[mesaj_anahtari] = True

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

    try:
        await ctx.message.delete()
    except:
        pass

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

# ==========================================
# 6. DEĞER AZALTMA SİSTEMİ (.dsil)
# ==========================================
@bot.command(name="dsil")
@commands.has_permissions(manage_nicknames=True)
async def deger_sil(ctx, member: discord.Member, miktar: int, *, sebep: str = "Sebep belirtilmedi"):
    mesaj_anahtari = (ctx.author.id, member.id, -miktar, sebep)
    if mesaj_anahtari in son_gonderilenler:
        return
    son_gonderilenler[mesaj_anahtari] = True

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
