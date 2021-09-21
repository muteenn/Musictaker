import discord
import asyncio
import youtube_dl
from discord.ext import tasks
import re
import subprocess

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'preferredcodec': 'm4a',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

AUDIO_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class set_source(discord.PCMVolumeTransformer):
    def __init__(self, source, *, volume=0.5):
        super().__init__(source, volume)

    async def set(url, loop = None):
        if not "m3u8" in url:
            print(url)
            loop = loop or asyncio.get_event_loop()
            music = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            return discord.FFmpegPCMAudio(music["url"], **AUDIO_OPTIONS)
        else:

            return discord.FFmpegPCMAudio(url, **AUDIO_OPTIONS)

#サーバーデータ保管用クラス 
#Vcli=ボイスクライアント id=鯖id plist=プレイリスト 
#np=現在再生中曲の情報 flag=鯖におけるbotの状態 mesid=embed編集時など保存しておきたいメッセージID
class svdata:
    def __init__(self,Vcli,id):
        self.Vcli = Vcli
        self.id = id
        self.plist = []
        self.np = []
        self.flag = 0
    
    def adplist(self,adlist):
        if adlist != None:
            self.plist.append(adlist)
    

#TOKENにbotのトークン
TOKEN = ""
#Vclients = [svdata]*鯖の数
Vclients = []
# 接続
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
dclient = discord.Client(intents=intents)

#起動
@dclient.event
async def on_ready():
    print("kidou simasita")
    await playplist.start()


#メッセージを受け取ったときのあれこれ
@dclient.event
async def on_message(message):
    print(str(message.author) + " : " + str(message.content))

#どのサーバーでメッセージが送られたのかの判別
    global Vclients
    ordsvid = None
    if len(Vclients) != 0:
        print(Vclients)
        for i,j in enumerate(Vclients):
            if str(j.id) in str(message.guild.id):
                #orderserverid オーダー出した鯖の配列番号
                ordsvid = i

    #botなら無視
    if message.author.bot:
        return

    #clearコマンド時用
    if ordsvid != None and Vclients[ordsvid].flag == 1 and not re.search(r"[yYnN]", message.content):
            await message.channel.send("YかNかでお願いします")
            return
    #ボイスチャンネルへの接続
    if re.search(r"(\$join)", message.content):
        if message.author.voice == None:
            await message.channel.send("ボイスチャンネル入ってね")
            return

        if await joindef(message) == -1:
            await message.channel.send("もう入ってます！")
            return
        else:
            return

    #再生リストへの追加
    if re.search(r"(\$play)", message.content):

        if ordsvid == None:
            if message.author.voice == None:
                await message.channel.send("先にボイスチャンネル入ってね")
                return
            else:
                ordsvid = await joindef(message)

        result = re.search(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]+", message.content)
        if result:
            #先にユーザー名を取得しておく
            if message.author.nick == None:
                disname = message.author.name + "#" + message.author.discriminator
            else:
                disname = message.author.nick + "(" + message.author.name + "#" + message.author.discriminator + ")"


            #youtubeリストを投げられた時の処理
            url = result.group()
            if "soundcloud" in url:
                youdata = ytdl.extract_info(url=url, download = False)
                Vclients[ordsvid].adplist([youdata["url"],disname,youdata["title"],youdata["uploader"],round(youdata["duration"]) if youdata["url"][-5:] != ".m3u8" else 0,False])
                embed = discord.Embed(title="Soundcloud - " + youdata["title"],description=youdata["uploader"])
                embed.add_field(name = "Added by ", value = disname)
                embed.add_field(name = "Song Duration", value = str(int(youdata["duration"] // 60)) + ":" + '{:02d}'.format(int(youdata["duration"]) % 60))
                est = sum([i[4] for i in Vclients[ordsvid].plist])
                embed.add_field(name = "List Duration",value = str(int(est // 60)) + ":" + '{:02d}'.format(int(est) % 60))

                await message.channel.send(embed = embed)
            elif ".m3u8" in url:
                Vclients[ordsvid].adplist([url,disname,"unknown(m3u8直指定)",disname,0,False])

                embed = discord.Embed(title="ライブストリーム？",description="m3u8直指定")
                embed.add_field(name = "Added by ", value = disname)
                embed.add_field(name = "type", value = "Live stream?")
                await message.channel.send(embed = embed)
        else:
            await message.channel.send("URL指定してね")
        return

    #nowplaying表示
    if re.search(r"(\$now)", message.content):
        if Vclients[ordsvid].Vcli.is_playing():

            await message.channel.send("なう：" + Vclients[ordsvid].np[3] + " - " + Vclients[ordsvid].np[2] + " by " + Vclients[ordsvid].np[1])
        else:
            await message.channel.send("何も流してないです")
        return
    #queue表示
    if re.search(r"(\$queue)", message.content):
        text = ""
        maxpage = 0
        if Vclients[ordsvid].Vcli.is_playing():
            text = "なう：" + Vclients[ordsvid].np[2] + " by " + Vclients[ordsvid].np[3]
        if len(Vclients[ordsvid].plist) >= 1:
            for i in range(len(Vclients[ordsvid].plist)):
                text += "\n\n" + str(i+1) + "：" + Vclients[ordsvid].plist[i][2] + " by " + Vclients[ordsvid].plist[i][3]
                if i == 9:
                    break
            descript = text
            if len(Vclients[ordsvid].plist) >= 10:
                descript += "\n\n +" + str(len(Vclients[ordsvid].plist) - 10) + "songs"
            embed = discord.Embed(title="曲リスト",description=descript)
            await message.channel.send(embed = embed)

        elif Vclients[ordsvid].Vcli.is_playing():
            if text[0] != "":
                embed = discord.Embed(title="曲リスト",description=text)
                await message.channel.send(embed = embed)            
            else:
                await message.channel.send("なにもないです")
        return

    #曲スキップ
    if re.search(r"(\$skip)", message.content):
        if Vclients[ordsvid].Vcli.is_playing():
            Vclients[ordsvid].Vcli.stop()
        elif len(Vclients[ordsvid].plist) >= 1:
            Vclients[ordsvid].plist.pop(0)
        else:
            await message.channel.send("queueにも何も残ってないです")
        await message.channel.send("Skipしました")
        return
    #曲削除
    if re.search(r"(\$remove)", message.content):
        result = re.search(r"[0-9]+", message.content)
        if result and int(result.group()) <= len(Vclients[ordsvid].plist):
            popped = Vclients[ordsvid].plist.pop(int(result.group())-1)
            await message.channel.send(result.group() + "：" + popped[3] + " - " + popped[2] + "を削除しました")
        else:
            await message.channel.send("なんか変な入力っぽいのでもう一度確かめてください")
        return
    #切断
    if re.search(r"(\$disconnect)", message.content):
        if Vclients[ordsvid].Vcli == None:
            await message.channel.send("誰もいないです")
            return
        await message.channel.send("離脱します")

        await Vclients[ordsvid].Vcli.disconnect()
        popped = Vclients.pop(ordsvid)
        print(popped)
        return
    #queue全消し
    if re.search(r"(\$clear)", message.content):
        if len(Vclients[ordsvid].plist) >= 1:
            await message.channel.send("本当にqueue全消ししますか？Y/N")
            Vclients[ordsvid].flag = 1
        else:
            await message.channel.send("リストに曲入ってないです")   
        return


    #clear用
    if (message.content == "n" or message.content == "N")and Vclients[ordsvid].flag == 1:
        Vclients[ordsvid].flag = 0
        await message.channel.send("操作取り消しました")
        return

    if (message.content == "y" or message.content == "Y")and Vclients[ordsvid].flag == 1:
        Vclients[ordsvid].plist = []
        Vclients[ordsvid].flag = 0
        await message.channel.send("全消ししました")
        return
            
    #起床チェック（開発用）
    if re.search(r"(\$check)", message.content):
        await message.channel.send("起きてます")
        return
    #キャッシュクリア（開発用）
    if re.search(r"(\$cacheclear)", message.content):
        arg = ["youtube-dl", "--rm-cache-dir"]
        subprocess.check_call(arg)
        await message.channel.send("キャッシュクリアしました")
        return

    if re.search(r"(\$help)", message.content):
        text = "$join:join打った人と同じチャンネルに参加します\n" \
        "$play [URL]:soundcloudの音楽に対応している他、m3u8直接指定でも可能です\n" \
        "$skip:今再生してるやつをスキップします\n" \
        "$now:再生中のものを表示します\n" \
        "$remove:queueの番号指定で取り消すやつ\n" \
        "$queue:再生リスト一覧表示します\n" \
        "$disconnect:ボイスチャンネルから離脱します \n" \
        "$clear:queueを全消しします"
        embed = discord.Embed(title="コマンドリスト",description=text)
        await message.channel.send(embed = embed)
        return


#join機能
async def joindef(mess):

    if mess.author.voice == None:
        return -2 #発言者がボイチャ入ってないよ

    for i in Vclients:
        if str(mess.guild.id) in str(i.id):
            return -1 #もう既に登録されてるよ

    Vclients.append(svdata(Vcli=await mess.author.voice.channel.connect(),id=mess.guild.id))
    for i,j in enumerate(Vclients):
        if str(mess.guild.id) in str(j.id):
            #order server id オーダー出した鯖の配列番号
            return i

#play機能
@tasks.loop(seconds = 2)
async def playplist():
    for nu, Vcli in enumerate(Vclients):
        if len(Vclients[nu].plist) >= 1 and Vclients[nu].Vcli.is_playing() == False:
            Vclients[nu].np = Vclients[nu].plist.pop(0)
            source = await set_source.set(Vclients[nu].np[0], loop = dclient.loop)
            print(source)
            Vclients[nu].Vcli.play(source)

#起動
dclient.run(TOKEN)
