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
    
    # 📌 En kritik nokta burası: Yeni mesaj atmak yerine eski mesajı güncelliyoruz.
    await mesaj.edit(content=None, embed=sonuc_embed, view=None)
