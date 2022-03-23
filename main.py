import nextcord
from nextcord.ext import commands
from datetime import datetime
from module import *
from pathlib import Path
from nextcord.utils import get
import json
import time
import option
import asyncio

options = ['환영메세지','서버 입장', '서버 퇴장', '메세지 삭제', '메세지 수정', '채널 생성', '채널 삭제', '유저 역할 변경', '유저 닉네임 변경', '역할 생성', '역할 삭제', '역할 이름 변경', '역할 색 변경', '유저 차단', '유저 차단 해제', '초대코드 생성', '초대코드 삭제', '보이스 채널 입장', '보이스 채널 퇴장']

#MONDAY TOKEN 
token = str(open("token.txt", "r").readline())

#Load Datas from json file
with open('data.json', 'r', encoding="UTF-8") as f:
    datas = json.load(f)

with open('guild.json', 'r', encoding="UTF-8") as g:
    guilds = json.load(g)

def update_guild():
    with open('guild.json', 'w', encoding='UTF-8') as g:
        json.dump(guilds, g, ensure_ascii=False)

#Settings of Monday 
intents = nextcord.Intents.all()
activity= [nextcord.Game, nextcord.Streaming, nextcord.Activity]
app = commands.AutoShardedBot(shard_count=1, command_prefix='', intents=intents, help_command=None)
app.version = '0.8.7'

#Colors of embed colors
colors = {'RED':0xFE0100, 
          'GREEN':0x05B430,
          'ORANGE':0xFFBF00,
          'MAIN':0x01A9DB}

#else Values 
nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

#Button 
class Confirm(nextcord.ui.View): 
    def __init__(self, user): 
        super().__init__()
        self.user = user
        self.value = None

    @nextcord.ui.button(label='수락', style=nextcord.ButtonStyle.green)
    async def confirm(self, button:nextcord.ui.Button, interacation:nextcord.Interaction): 
        if self.user == interacation.user:
            self.value = True
            self.stop()

    @nextcord.ui.button(label='거절', style=nextcord.ButtonStyle.red)
    async def cancel(self, button:nextcord.ui.Button, interacation:nextcord.Interaction): 
        if self.user == interacation.user:
            self.value = False
            self.stop()

class Dropdown(nextcord.ui.Select): 
    def __init__(self, guild): 
        self.select_option = []

        with open('guild.json', 'r', encoding="UTF-8") as g:
                data_guild = json.load(g)

        if data_guild[guild]['LOG_OPTION'][0] == True: 
                state = '🟢'
                state_ex = '클릭 시 비활성화'
        else: 
            state = '⚪'
            state_ex = '클릭 시 활성화'

        self.select_option.append(nextcord.SelectOption(label=f'{options[0]} ㅣ {state_ex}', description=f'유저가 입장 시 메세지 전송', emoji=state))

        for i in range(1, len(options)):
            with open('guild.json', 'r', encoding="UTF-8") as g:
                data_guild = json.load(g)

            if data_guild[guild]['LOG_OPTION'][i] == True: 
                state = '🟢'
                state_ex = '클릭 시 비활성화'
            else: 
                state = '⚪'
                state_ex = '클릭 시 활성화'

            self.select_option.append(nextcord.SelectOption(label=f'{options[i]} ㅣ {state_ex}', description=f'{options[i]} 시 로깅', emoji=state))
        super().__init__(placeholder='설정할 로그를 선택하세요.', min_values = 1, max_values = 1, options=self.select_option)

    async def callback(self, interaction:nextcord.Interaction): 
        guild = str(interaction.guild.id) 

        with open('guild.json', 'r', encoding="UTF-8") as g:
            data_guild = json.load(g)

        index = options.index(self.values[0].split(' ㅣ')[0]) 
        if data_guild[guild]['LOG_OPTION'][index] == True:
            guilds[guild]['LOG_OPTION'][index] = False
            state = '⚪'

        else: 
            guilds[guild]['LOG_OPTION'][index] = True
            state = '🟢'
            
        self.select_option[index] = nextcord.SelectOption(label=f'{options[index]}', description=f'{options[index]} 시 로깅', emoji=state)
        update_guild() 

        settings = "" 

        for option in options: 
            with open('guild.json', 'r', encoding="UTF-8") as g:
                data_guild = json.load(g)

            if data_guild[str(interaction.guild.id)]['LOG_OPTION'][options.index(option)] == True: 
                state = 'ON'

            else: 
                state = 'OFF'

            settings += f"**{option}** 시 로깅 : `{state}`\n"

        embed = nextcord.Embed(title='로그 설정', description=settings, color=colors['MAIN'])
        await interaction.response.edit_message(embed=embed, view=DropdownView(guild))

        if self.values[0].split(' ㅣ')[0] == '환영메세지' and data_guild[str(interaction.guild_id)]["LOG_OPTION"][0] == True: 
            embed = nextcord.Embed(title='환영메세지 설정', description='환영메세지 설정을 하시려면 `환영메세지설정`을 입력해 설정하세요.') 
            embed.add_field(name='입장 메세지 전송 채널', value=f'{app.get_channel(int(data_guild[str(interaction.guild.id)]["JOIN"]["CHANNEL"])).mention if data_guild[str(interaction.guild.id)]["JOIN"]["CHANNEL"] != None else "```설정되지 않음```"}', inline=False)
            embed.add_field(name='입장 시 메세지', value=f'```{data_guild[str(interaction.guild_id)]["JOIN"]["MESSAGE"]}```', inline=False)
            embed.add_field(name='퇴장 메세지 전송 채널', value=f'{app.get_channel(int(data_guild[str(interaction.guild.id)]["EXIT"]["CHANNEL"])).mention if data_guild[str(interaction.guild.id)]["JOIN"]["CHANNEL"] != None else "```설정되지 않음```"}', inline=False)
            embed.add_field(name='퇴장 시 메세지', value=f'```{data_guild[str(interaction.guild_id)]["EXIT"]["MESSAGE"]}```', inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)

class DropdownView(nextcord.ui.View):
    def __init__(self, guild): 
        super().__init__()
        self.add_item(Dropdown(guild))

'''
class Pet(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Your pet",
            timeout=5 * 60,  # 5 minutes
        )

        self.name = nextcord.ui.TextInput(
            label="Your pet's name",
            min_length=2,
            max_length=50,
        )
        self.add_item(self.name)

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Information that can help us recognise your pet",
            required=False,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        response = f"{interaction.user.mention}'s favourite pet's name is {self.name.value}."
        if self.description.value != "":
            response += f"\nTheir pet can be recognized by this information:\n{self.description.value}"
        await interaction.send(response)
'''

async def check_pattern(ctx, txt, tag): 
    returnValue = False

    with open('data.json', 'r', encoding="UTF-8") as f:
        data_intent = json.load(f)

    for data in data_intent: 
        if data['tag'] == tag: 
            if 'nonresponsible' in data['feature']:
                patterns = data['patterns'] 

                for pattern in patterns: 
                    if pattern in txt:
                        returnValue = True

                    else: 
                        pass

    return returnValue
            
async def check_promiss(ctx):
    if ctx.author.guild_permissions.administrator == True:
        return True

    else: 
        embed = nextcord.Embed(description='접근권한 부족', color=colors['RED']) 
        await ctx.send(embed=embed)

async def logging(guild:str, event, embed): 
    with open('guild.json', 'r', encoding="UTF-8") as g:
        data_guild = json.load(g)

    eventNum = int(options.index(event))
    if str(guild) in data_guild: 
        if data_guild[guild]["LOG_OPTION"][eventNum] == True:
            now = datetime.now()
            now = now.strftime('%Y-%m-%d %H:%M:%S')

            log = app.get_channel(int(data_guild[str(guild)]['LOG'])) 
            embed.add_field(name='TIMESTAMP', value=f'```{now}```', inline=False)
            await log.send(embed=embed)

async def send_log(guild, event, channel, user, content): 
    with open('guild.json', 'r', encoding="UTF-8") as g:
        data_guild = json.load(g)

    if str(guild) in data_guild:
        log = app.get_channel(int(data_guild[guild]['LOG']))

        embed = nextcord.Embed(title=f'{event}', color=colors['MAIN'])
        embed.add_field(name=f'**유저**', value=f'{user.mention}', inline=True)
        embed.add_field(name=f'**채널**', value=f'{channel.mention}')
        embed.add_field(name=f'**내용**', value=f'```{content}```', inline=False)
        await log.send(embed=embed)

async def stats(ctx, txt):
    dpyVersion = nextcord.__version__
    serverCount = len(app.guilds)
    memberCount = len(set(app.get_all_members()))

    shardID = ctx.guild.shard_id
    shard = app.get_shard(shardID)
    shardPING = shard.latency
    shardSERVERS = len([guild for guild in app.guilds if guild.shard_id == shardID])

    embed = nextcord.Embed(title=f'{app.user.name} - Stats')

    embed.add_field(name='Bot Version:', value=f'```{app.version}```')
    embed.add_field(name='Discord.Py Version:', value=f'```{dpyVersion}```')
    embed.add_field(name='Total Guilds:', value=f'```{serverCount}```', inline=False)
    embed.add_field(name='Total Users:', value=f'```{memberCount}```')
    embed.add_field(name='Shard ID:', value=f'```{shardID}```', inline=False)
    embed.add_field(name='Shard Ping:', value=f'```{shardPING}```')
    embed.add_field(name='Shard Servers:', value=f'```{shardSERVERS}```')

    user = app.get_user(ctx.author.id)

    #embed.set_thumbnail(url=thumbnail)
    embed.set_author(name=user.display_name, icon_url=user.avatar)

    await ctx.send(embed=embed)
        
async def cal(ctx, txt): 
    operatorsWord = ['플러스', '더하기', '빼기', '마이너스', '나누기', '곱하기']
    operators = ['+', '-', '*', '/'] 
    
    for operator in operatorsWord: 
        try: 
            if operator in '플러스' or operator in '더하기':
                replaceOper = '+'

            elif operator in '빼기' or operator in '마이너스':
                replaceOper = '-'

            elif operator in '나누기':
                replaceOper = '/'

            elif operator in '곱하기':
                replaceOper = '*'

            txt = txt.replace(operator, replaceOper) 

        except:
            pass

    txt = "".join(txt.split()) 

    expression= [] 
    numIndex = []
    
    for num in nums: 
        if num in txt: 
            index = txt.index(num) 
            numIndex.append(index)

        else: 
            pass

    if numIndex != []:
        index = min(numIndex) 

        expression.append(txt[index])
        for x in range(1, len(txt)+1): 
            if len(txt) > index+x:
                if txt[index+x] in nums: 
                    expression.append(txt[index+x]) 

                elif txt[index+x] in operators:
                    expression.append(txt[index+x])

                else:
                    break

            else:
                break

        expression = "".join(expression)

        embed = nextcord.Embed(title='계산', color=colors['GREEN']) 
        embed.add_field(name='식', value=f'```{expression}```')
        embed.add_field(name='결과', value=f'```{eval(expression)}```')
        await ctx.send(embed=embed)

async def translate(ctx, txt): 
    transOptions = ["한글로", "영어로", "일본어로", "한국어로", "잉글리쉬로", "코리안으로", "영어", "한글"]

    for transOption in transOptions:
        if transOption in txt.split():

            text = "".join("".join(txt.split()).split(transOption))
            print(text)
            if text.split('번역')[0] != '':
                text = " ".join(text.split('번역')[0].split())
            
            else: 
                text = " ".join(text.split('번역')[1].split())

            transOption = "".join(transOption.split('로')[0].split())

            break

        else: 
            transOption = 'ko'
            
            if txt.split('번역')[0] != '':
                text = " ".join(txt.split('번역')[0].split())
            
            else: 
                text = " ".join(txt.split('번역')[1].split())

    result = option.Translate().get_translate(text)
    await ctx.send(result)

async def check_ping(ctx, txt):
    try:
        ra1 = round(app.latency * 1000)

    except:
        pass

    embed = nextcord.Embed(title="Connection", color=colors['MAIN'])
    embed.add_field(name='Ping', value=f'```{str(ra1)}ms```')
    await ctx.send(embed=embed)

async def weather(ctx, txt):
    if '날씨' in txt: 
        searchOption = False
        
        scaleList = ['도', '시', '군', '구', '동', '읍', '면', '리']

        location = " ".join(txt.split('날씨')[0].split())

        #print(location)
        #print(location[-1])

        if location[-1] in scaleList:
            #print('if')
            #print(len(location.split()))
            if len(location.split()) != 1: 
                for loc in location.split(): 
                    #print(loc)
                    if loc[-1] not in scaleList: 
                        location = " ".join("".join(location.split(loc)).split())

        else:
            location = None

        if '자세히' in txt:
            searchOption = True

        info = option.Crawling().weather(location, searchOption)

        embed = nextcord.Embed(title=f'{info[0]}의 날씨', color=colors['MAIN']) 
        embed.add_field(name='온도', value=f'```{info[1]}C```')
        embed.add_field(name='설명', value=f'```{info[2]}```', inline=False)

        if len(info) > 3:
            embed.add_field(name='강수확률', value=f'```{info[3]}```')
            embed.add_field(name='습도', value=f'```{info[4]}```')
            embed.add_field(name=f'바람({info[6]})', value=f'```{info[5]}```')

        await ctx.send(embed=embed)

async def corona(ctx, txt): 
    if '모든' in txt or '모두' in txt or '자세히' in txt: 
        Outputoption = 'all' 
        size = '자세한'

    elif '오늘' in txt or '투데이' in txt or '일일' in txt: 
        Outputoption = 'today' 
        size = '오늘'

    elif '전체' in txt or '토탈' in txt or '누적' in txt: 
        Outputoption = 'total' 
        size = '누적'

    else: 
        size = '오늘/누적'
        Outputoption = None

    output = option.Crawling().corona(Outputoption)

    embed = nextcord.Embed(title=f'{size} 코로나 현황', description='```코로나 현황입니다.```',color=colors['MAIN']) 
    await ctx.send(embed=embed)

    if Outputoption == None: 
        day_embed = nextcord.Embed(title='오늘', color=colors['MAIN']) 
        day_embed.add_field(name='사망자', value=f'```{output[1][0]}명```')
        day_embed.add_field(name='재원 위중증', value=f'```{output[1][1]}명```')
        day_embed.add_field(name='신규 입원', value=f'```{output[1][2]}명```')
        day_embed.add_field(name='확진자', value=f'```{output[1][3]}명```')
        await ctx.send(embed=day_embed)

        total_embed = nextcord.Embed(title='누적', color=colors['MAIN']) 
        total_embed.add_field(name='사망자', value=f'```{output[0][0]}명```')
        total_embed.add_field(name='확진자', value=f'```{output[0][1]}명```')
        await ctx.send(embed=total_embed)

    elif Outputoption == 'today': 
        #사망, 재원 위중증, 신규 입원, 확진 
        day_embed = nextcord.Embed(title='오늘', color=colors['MAIN']) 
        day_embed.add_field(name='사망자', value=f'```{output[0][0]} 명```')
        day_embed.add_field(name='재원 위중증', value=f'```{output[0][1]} 명```')
        day_embed.add_field(name='신규 입원', value=f'```{output[0][2]} 명```')
        day_embed.add_field(name='확진자', value=f'```{output[0][3]} 명```')
        await ctx.send(embed=day_embed)

    elif Outputoption == 'total': 
        total_embed = nextcord.Embed(title='누적', color=colors['MAIN']) 
        total_embed.add_field(name='사망자', value=f'```{output[0][0]} 명```')
        total_embed.add_field(name='확진자', value=f'```{output[0][1]} 명```')
        await ctx.send(embed=total_embed)

    elif Outputoption == 'all': 
        day_embed = nextcord.Embed(title='오늘', color=colors['MAIN']) 
        day_embed.add_field(name='사망자', value=f'```{output[1][0]} 명```')
        day_embed.add_field(name='재원 위중증', value=f'```{output[1][1]} 명```')
        day_embed.add_field(name='신규 입원', value=f'```{output[1][2]} 명```')
        day_embed.add_field(name='확진자', value=f'```{output[1][3]} 명```')
        await ctx.send(embed=day_embed)

        day7_embed = nextcord.Embed(title='7일 평균', color=colors['MAIN']) 
        day7_embed.add_field(name='사망자', value=f'```{output[2][0]} 명```')
        day7_embed.add_field(name='재원 위중증', value=f'```{output[2][1]} 명```')
        day7_embed.add_field(name='신규 입원', value=f'```{output[2][2]} 명```')
        day7_embed.add_field(name='확진자', value=f'```{output[2][3]} 명```')
        await ctx.send(embed=day7_embed)

        total_embed = nextcord.Embed(title='누적', color=colors['MAIN']) 
        total_embed.add_field(name='사망자', value=f'```{output[0][0]} 명```')
        total_embed.add_field(name='확진자', value=f'```{output[0][1]} 명```')
        await ctx.send(embed=total_embed)

async def exchange(ctx, txt): 
    moneys = ['엔', '호주달러', '호주 달러', '위안', '유로', '파운드', '앤', '달러'] 
    
    for money in moneys: 
        if money in txt: 
            break

        else: 
            money = '달러'

    exchange = option.Crawling().exchange(money) 

    if exchange != False: 
        embed = nextcord.Embed(title=f'{money}의 환율', description=f'```{exchange}원```', color=colors['MAIN'])

    else: 
        embed = nextcord.Embed(title='환율', description=f'{money}의 화폐 가치를 파악할 수 없습니다.', color=colors['RED'])

    await ctx.send(embed=embed)
    #url = f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query={money}+환율'

#Utility function
async def purge_all(ctx, txt): 
    amount = 1000000
    all = True
    cancel = False
    whe = Confirm(ctx.author)

    processOption = '' 

    if await check_pattern(ctx, txt, '즉시') == True:
        processOption = '즉시'

    embed = nextcord.Embed(title='삭제', description=f'모든 메세지를 {processOption} 삭제하시겠습니까?', color=colors['MAIN']) 
    msg = await ctx.send(embed=embed, view=whe)

    await whe.wait()
    await msg.delete()

    if whe.value == True:
        if processOption != '즉시':
            embed = nextcord.Embed(title='수락됨', description='5초 후 청소가 진행됩니다. 취소를 원하시면 `취소`를 입력하세요.', color=colors['GREEN'])
            embed.set_footer(text='오류 메세지가 뜨지 않다면 실행 중인 뜻 입니다!')
            notice = await ctx.send(embed=embed)
        
            embed = nextcord.Embed(title='카운트다운', description='5초 후 진행됨', color=colors['GREEN']) 
            msg = await ctx.send(embed=embed) 

            await asyncio.sleep(1.2)

            def check(message):
                return message.content == "취소" and message.channel == ctx.channel and message.author == ctx.author

            for x in range(1, 5):
                if 5-x <= 2: 
                    color = colors['RED']

                elif 5-x <= 4: 
                    color = colors['ORANGE']

                try:
                    embed = nextcord.Embed(title='카운트다운', description=f'{5-x}초 후 진행됨', color=color)
                    await msg.edit(embed=embed)

                    event = await app.wait_for("message", timeout= 1.2, check=check)

                    if event:
                        cancel = True
                        break

                except asyncio.exceptions.TimeoutError:
                    pass
            
            await msg.delete()
            await notice.delete()

        if cancel == False: 
            try: 
                times = int(amount/100) + 1 
                elseValue = amount-(100*times)
                
                await ctx.channel.purge(limit=1) 
                await ctx.channel.purge(limit=elseValue) 

                for x in range(0, int(times)):
                    try:
                        try:
                            await ctx.channel.purge(limit=100)

                        except: 
                            break
                    
                    except: 
                        embed = nextcord.Embed(title='오류', description=f'예기치 못한 오류가 발생하였습니다.', color=colors['RED'])
                        await ctx.send(embed=embed)
                        break

            except: 
                embed = nextcord.Embed(title='오류', description=f'예기치 못한 오류가 발생하였습니다.', color=colors['RED'])
                await ctx.send(embed=embed)

            if all == True:
                embed = nextcord.Embed(title='삭제됨', description='모든 메세지를 삭제했습니다.', color=colors['GREEN'])
                embed.add_field(name='이벤트', value='```삭제```')
                embed.add_field(name='개수', value=f'```{amount}```')
                await ctx.send(embed=embed)

        else: 
            embed = nextcord.Embed(title='거절됨', description=f'메세지 삭제가 취소되었습니다.', color=colors['RED'])
            await ctx.send(embed=embed)

async def purge(ctx, txt):
    if await check_promiss(ctx) == True:
        if '청소' or '삭제' in txt:
            if '개' in txt: 
                for line in txt.split(): 
                    if '개' in line: 
                        if int(line.index('개')) != 0:
                            amount = int(line.split('개')[0])+1

            elif await check_pattern(ctx, txt, '전체') == True:
                amount = 1000000

            else: 
                output = []
                for num in nums: 
                    if num in txt: 
                        index = txt.index(num) 
                        output.append(index)

                    else: 
                        pass

                if output != []:
                    index = min(output) 
                    output = []
                    output.append(txt[index])
                    for x in range(1, len(txt)+1): 
                        if len(txt) > index+x:
                            if txt[index+x] in nums: 
                                output.append(txt[index+1]) 
                            else:
                                break

                        else:
                            break

                    amount = int("".join(output))

                else: 
                    amount = 1

            if amount == 1000000: 
                await purge_all(ctx, txt) 

            else: 
                whe = Confirm(ctx.author)
                processOption = '' 
                cancel = False

                if await check_pattern(ctx, txt, '즉시') == True:
                    processOption = '즉시'

                embed = nextcord.Embed(title='삭제', description=f'메세지 `{amount}`개를 {processOption} 삭제하시겠습니까?', color=colors['MAIN']) 
                msg = await ctx.send(embed=embed, view=whe)

                await whe.wait()

                await msg.delete()

                if whe.value == True:
                    if processOption != '즉시':
                        embed = nextcord.Embed(title='수락됨', description='5초 후 청소가 진행됩니다. 취소를 원하시면 취소를 입력하세요.', color=colors['GREEN'])
                        embed.set_footer(text='오류 메세지가 뜨지 않다면 실행 중인 뜻 입니다!')
                        notice = await ctx.send(embed=embed)
                    
                        embed = nextcord.Embed(title='카운트다운', description='5초 후 진행됨', color=colors['GREEN']) 
                        msg = await ctx.send(embed=embed) 

                        await asyncio.sleep(1.2)

                        def check(message):
                            return message.content == "취소" and message.channel == ctx.channel and message.author == ctx.author

                        for x in range(1, 5):
                            if 5-x <= 2: 
                                color = colors['RED']

                            elif 5-x <= 4: 
                                color = colors['ORANGE']

                            try:
                                embed = nextcord.Embed(title='카운트다운', description=f'{5-x}초 후 진행됨', color=color)
                                await msg.edit(embed=embed)

                                event = await app.wait_for("message", timeout=1.2, check=check)

                                if event:
                                    cancel = True
                                    break

                            except asyncio.exceptions.TimeoutError:
                                pass
                        
                        await msg.delete()
                        await notice.delete()   

                    if cancel == False:
                        amount = len(await ctx.channel.history(limit=amount+1).flatten())-1

                        if amount > 100:
                            try: 
                                times = int(amount/100) + 1 
                                elseValue = amount-(100*times)

                                await ctx.channel.purge(limit=1) 
                                await ctx.channel.purge(limit=elseValue) 

                                for x in range(0, int(times)):
                                    try:
                                        try:
                                            await ctx.channel.purge(limit=100)
                                        except: 
                                            break
                                    
                                    except: 
                                        embed = nextcord.Embed(title='오류', description=f'예기치 못한 오류가 발생하였습니다.', color=colors['GREEN'])
                                        embed.add_field(name='이벤트', value='```삭제```')
                                        embed.add_field(name='개수', value=f'```{amount}```')
                                        await ctx.send(embed=embed)

                                        break

                            except: 
                                pass

                        elif amount <= 100:
                            await ctx.channel.purge(limit=amount+1) 

                        embed = nextcord.Embed(title='삭제됨', description=f'메세지를 삭제했습니다.', color=colors['GREEN'])
                        embed.add_field(name='이벤트', value='```삭제```')
                        embed.add_field(name='개수', value=f'```{amount}```')
                        await ctx.send(embed=embed)

                    else:        
                        embed = nextcord.Embed(description='메세지 삭제를 거절했습니다.', color=colors['RED']) 
                        await ctx.send(embed=embed)
                else:
                    embed = nextcord.Embed(description='메세지 삭제를 거절했습니다.', color=colors['RED']) 
                    await ctx.send(embed=embed)

async def kick(ctx, txt):
    if await check_promiss(ctx) == True:
        for line in txt.split():
            if '<@!' in line: 
                user_id = line.split('<@!')[1].split('>')[0] 
                user = ctx.guild.get_member(int(user_id))
                break
            
            else: 
                user = None

        if user != None: 
            whe = Confirm(ctx.author)
            embed = nextcord.Embed(title='추방', description=f'{user.mention}님을 추방하시겠습니까?', color=colors['MAIN']) 
            msg = await ctx.send(embed=embed, view=whe)

            await whe.wait()

            if whe.value == True:
                await msg.delete()
                await user.kick()
                embed = nextcord.Embed(title='추방됨', description=f'유저를 삭제했습니다.', color=colors['GREEN'])
                embed.add_field(name='이벤트', value='```추방```')
                embed.add_field(name='유저', value=f'```{user}```')
                await ctx.send(embed=embed)

            else:
                await msg.delete()
                embed = nextcord.Embed(description='추방을 거절했습니다.', color=colors['RED']) 
                await ctx.send(embed=embed)

async def set_slow_mode_delay(ctx, txt): 
    if await check_promiss(ctx) == True:
        time_scare = ['초', '분', '시간']

        if '삭제' in txt or '없애' in txt or '갖다버려' in txt: 
            await del_slow_mode_delay(ctx, txt)

        else:
            sec = None

            for time in time_scare:
                if time in txt: 
                    index = txt.index(time) 

                    for line in txt.split(): 
                        if time in line: 
                            print(line)
                            sec = int(line.split(time)[0]) 

                            if time == '초': 
                                sec = sec * 1

                            elif time == '분': 
                                sec = sec * 60

                            elif time == '시간': 
                                sec = sec * 3600

                            timeset = time

                            print(sec) 
                            break

            if sec == None:
                txt = "".join(txt.split()) 

                expression= [] 
                numIndex = []
                
                for num in nums: 
                    if num in txt: 
                        index = txt.index(num) 
                        numIndex.append(index)

                    else: 
                        pass

                if numIndex != []:
                    index = min(numIndex) 

                    expression.append(txt[index])
                    for x in range(1, len(txt)+1): 
                        if len(txt) > index+x:
                            if txt[index+x] in nums: 
                                expression.append(txt[index+x]) 
                                
                            else:
                                break

                        else:
                            break

                    sec = int("".join(expression)) 
                    timeset = '초'
            
            if timeset == '초': 
                sec_for = sec
            elif timeset == '분': 
                sec_for = int(sec/60)
                timeset = '분'
            elif timeset == '시간': 
                sec_for = int(sec/3600)
                timeset = '시간'

            if int(sec_for) > 21600: 
                sec = 21600
                sec_for = int(21600/3600) 
                timeset = '시간'

            elif int(sec) > 21600: 
                sec = 21600
                sec_for = int(21600/3600) 
                timeset = '시간'

            notify = nextcord.Embed(title='슬로우 모드 설정', color=colors['GREEN'])
            notify.add_field(name=f'{timeset}', value=f'```{sec_for}{timeset}```')
            if timeset != '초':
                notify.add_field(name=f'초', value=f'```{sec}초```')

            await ctx.send(embed=notify)

            if sec > 21600: 
                sec = 21600
                embed = nextcord.Embed(title='알림', description=f'값이 최대값인 6시간을 초과하여 슬로우 모드가 6시간으로 하향 설정되었습니다.', color=colors['ORANGE'])
                await ctx.send(embed=embed)
                
            await ctx.channel.edit(slowmode_delay=sec)

async def del_slow_mode_delay(ctx, txt): 
    if await check_promiss(ctx) == True:
        notify = nextcord.Embed(title='슬로우 모드 제거', description='슬로우 모드가 제거되었습니다.',color=colors['RED'])
        await ctx.send(embed=notify)

        await ctx.channel.edit(slowmode_delay=0)

#etc. Funchtion
async def check_time_mornig(ctx, txt): 
    now = datetime.now()
    now = int(now.strftime('%H')) 

    if now < 12:
        inputLayer = ('대답_평범_아침인사', 'MORNING')

    else: 
        inputLayer = ('대답_이상한_아침인사', 'MORNING')

    response = await get_response(inputLayer)
    await ctx.send(response)

async def check_time_night(ctx, txt): 
    now = datetime.now()
    now = int(now.strftime('%H')) 
    if now >= 21:
        inputLayer = ('대답_평범_저녁인사', 'NIGHT')

    else: 
        inputLayer = ('대답_이상한_저녁인사', 'NIGHT')

    response = await get_response(inputLayer)
    await ctx.send(response)

async def check_time(ctx, txt): 
    now = datetime.now()
    now = int(now.strftime('%H'))

    #morning 
    if now >= 17: 
        return 'night' 

    elif now >= 12 and now < 16: 
        return 'lunch'

    elif now >= 8 and now <= 11:  
        return 'morning'

async def repeat(ctx, txt): 
    words = ['따라해', '이라고 해봐', '라고 해봐']

    for word in words: 
        if word in txt: 
            table = txt.split(word)  
            if table[0] == '': 
                sentence = table[1]

            elif table[1] == '': 
                sentence = table[0] 

            else: 
                sentence = '뭘 따라해야 하는건가요?'

            break


    await ctx.send(sentence)

async def count_line(ctx, txt): 
    lines = 0  

    files = ['main', 'option', 'module']
    for file in files:
        for line in open(f"{file}.py"):  
            lines += 1     

    return lines

async def check_learn_file(ctx, txt): 
    with open('data.json', 'r', encoding="UTF-8") as f:
        data_intents = json.load(f) 
    file_size = Path('/mnt/c/Users/ychje/Desktop/WORKSPACE/DISCORD/data.json').stat().st_size

    embed = nextcord.Embed(title='학습 데이터 현황', description='학습 데이터는 다음과 같습니다.') 
    embed.add_field(name='intents', value=f'```{len(data_intents)}개```')
    embed.add_field(name='mappings', value=f'```{len(mappings)}개```')
    embed.add_field(name='code', value=f'```{await count_line(ctx, txt)}줄```', inline=False)
    embed.add_field(name='file size', value=f'```{round(file_size/1024, 1)}KB```')
    await ctx.send(embed=embed)

async def find_word(ctx, txt):
    index = 0 
    
    if "\"" in txt or "\'" in txt: 
        try:
            word = txt.split('\"') 

        except:
            word = txt.split('\'') 

        for letter in word: 
            if letter != "": 
                word = letter
                break

    else:
        for line in txt.split(): 
            if '뜻' == line[0] or '뜻' == line[-1] or '알려줘' in line: 
                break

            else: 
                index += 1 

        if '뜻' == txt.split()[index-1]: 
            word == txt.split()[index-2] 

        else: 
            word = txt.split()[index-1]

    results = option.Crawling().find_word(word) 

    if results != False: 
        definitions = '' 
        
        for x in range(1, len(results)): 
            definitions += f'{x}. {results[x]}\n' 

        embed = nextcord.Embed(title=f'{word} : ', description=f'```{results[0]}```', color=colors['MAIN'])
        if len(results) > 1:
            embed.add_field(name='또 다른 뜻', value=f'```{definitions}```')
            embed.set_footer(text='사용자님이 생각하던 단어가 아니라면 \" \" (따옴표) 안에 넣어서 입력해주세요.')
        await ctx.send(embed=embed) 

    else:
        embed = nextcord.Embed(title='검색 실패', description=f'```먼데이가 {word}에 대한 결과를 찾지 못 했습니다.', color=colors['RED'])
        embed.set_footer(text='사용자님이 생각하던 단어가 아니라면 \" \" (따옴표) 안에 넣어서 입력해주세요.')
        await ctx.send(embed=embed)  

async def check_word(ctx, txt):
    index = 0 
    
    if "\"" in txt or "\'" in txt: 
        try:
            word = txt.split('\"') 

        except:
            word = txt.split('\'') 

        for letter in word: 
            if letter != "": 
                result = letter
                break

    else:
        index = 0 
        find_stat = False
        result = None


        for line in txt.split(): 
            words = ['이', '가', '이가', '라는', '이라는', '란']
            
            for word in words: 
                if word in line:  
                    if line.split(word)[0] == '': 
                        line.split(word)[0]
                        result = txt.split()[index-1]

                    elif line.split(word)[0] != '': 
                        result = line.split(word)[0] 

                    if result != None: 
                        results = option.Crawling().find_word(result, '존재유무')

                        if results == True: 
                            break

            index += 1

    if result != None: 
        results = option.Crawling().find_word(result, '존재유무')

        if results == True: 
            inputLayer = ('대답_단어_존재유', 'True')

        elif results == False: 
            inputLayer = ('대답_단어_존재무', 'False')

        response = await get_response(inputLayer)
        
        await ctx.send(f'흠.. {result}.. {response}')

    else: 
        await ctx.send('어떤 단어를 말씀하시는지 모르겠어요 \" \" 사이에 넣어서 바로 이해할 수 있게 해주세요.')

async def cal_time(ctx, txt): 
    timescare = ['시', '시간', '분', '초', '전', '후', '뒤'] 

    time_expression = ''
    index = 0 

    for scare in timescare: 
        for line in txt.split():
            if scare in line: 

                time = line.split(scare)[0] if line.split(scare)[0] != '' else line.split(scare)[1] 
                
                if time_expression != '': 
                    if scare == '전': 
                        time_expression += '#-'
                        
                    elif scare == '후' or scare == '뒤': 
                        time_expression += '#+' 

                if scare == '시' or scare == '시간':
                    if 'h' in time_expression and '/' not in time_expression: 
                        time_expression += f'/{time}h'                
                    
                    else: 
                        time_expression += f'{time}h' 

                elif scare == '분':
                    if 'm' in time_expression and '/' not in time_expression: 
                        time_expression += f'/{time}m'

                    else: 
                        time_expression += f'{time}m'

                elif scare == '초':
                    if 's' in time_expression and '/' not in time_expression: 
                        time_expression += f'/{time}s' 

                    else: 
                        time_expression += f'{time}s'

            #if index != 0 and time_expression != '' or time_expression == 1: 
            #    index += 1

    timeValue = [0, 0] 
    index = 0 
    print(time_expression) 

    expressions = time_expression.split('#')[0].split('/') 
    signs = time_expression.split('#')[1:]

    print(expressions)
    print(signs)

    for expression in expressions: 
        if 'h' in expression: 
            print('h', expression)
            timeValue[index] += int(expression.split('h')[0])*3600
            expression = expression.split('h')[1]
            print('fh', expression)

        if 'm' in expression: 
            print('m', expression)
            timeValue[index] += int(expression.split('m')[0])*60
            expression = expression.split('m')[1] 
            print('fm', expression)

        if 's' in expression: 
            print('s', expression)
            timeValue[index] += int(expression.split('s')[1]) 
            print('fs', expression)
            continue

        index += 1

    print(timeValue) 
    print(timeValue[0]) 
    print(timeValue[1])
       
async def reminder(ctx, txt): 
    timescares = ['시', '시간', '분', '초'] 

    time_expression = ''

    for timescare in timescares: 
        if timescare in txt: 

            for line in txt.split():
                if timescare in line: 

                    time = line.split(timescare)[0] if line.split(timescare)[0] != '' else line.split(timescare)[1] 
                    
                    if time_expression != '': 
                        if timescare == '전': 
                            time_expression += '#-'
                            
                        elif timescare == '후' or timescare == '뒤': 
                            time_expression += '#+' 

                    if timescare == '시' or timescare == '시간':
                        if 'h' in time_expression and '/' not in time_expression: 
                            time_expression += f'/{time}h'                
                        
                        else: 
                            time_expression += f'{time}h' 

                    elif timescare == '분':
                        if 'm' in time_expression and '/' not in time_expression: 
                            time_expression += f'/{time}m'

                        else: 
                            time_expression += f'{time}m'

                    elif timescare == '초':
                        if 's' in time_expression and '/' not in time_expression: 
                            time_expression += f'/{time}s' 

                        else: 
                            time_expression += f'{time}s'
    
    scares = ['h', 'm', 's'] 

    time = []
    time_set = ""
    for scare in scares:
        if scare in time_expression:
            time.append(int(time_expression.split(scare)[0]))
            time_expression = time_expression.split(scare)[1]

            if scare == 'h': 
                if time_set != '':
                    time_set += f' {time[0]}시간'
                
                else: 
                    time_set += f'{time[0]}시간'

            elif scare == 'm':
                if time_set != '':
                    time_set += f' {time[1]}분'
                
                else: 
                    time_set += f'{time[1]}분'

            elif scare == 's':
                if time_set != '':
                    time_set += f' {time[2]}초'
                
                else: 
                    time_set += f'{time[2]}초'

        else: 
            time.append(0) 

    hour = 0 if time[0] == 0 else time[0] 
    minute = 0 if time[1] == 0 else time[1] 
    second = 0 if time[2] == 0 else time[2] 

    embed = nextcord.Embed(title='알람 설정', description=f'{ctx.author.mention}님! `{time_set} 후`에 알려드릴게요!', color=colors['MAIN'])
    embed.add_field(name='알람 설정 시간', value=f'```{time_set} 후```')
    reminder = await ctx.send(embed=embed) 

    await asyncio.sleep(hour*3600+minute*60+second) 

    await reminder.delete()

    embed = nextcord.Embed(title=f'{ctx.author.name}님의 알람', description=f'{ctx.author.mention}님! 말씀하신 `{time_set}`이 지났습니다.' if time_set[-1] != '초' else f'{ctx.author.mention}님! 말씀하신 `{time_set}`가 지났습니다.', color=colors['GREEN'])
    await ctx.send(embed=embed)

#Notification when the bot has been activated
@app.event
async def on_ready():
    #await app.change_presence(status=nextcord.Status.online)
    #await app.change_presence(status=nextcord.Game(name="게임 하는중"))
    #await app.change_presence(status=nextcord.Streaming(name="스트림 방송중", url='링크'))
    #await app.change_presence(status=nextcord.Activity(type=nextcord.ActivityType.listening, name="노래 듣는중"))
    await app.change_presence(status=nextcord.Activity(type=nextcord.ActivityType.watching, name="영상 시청중"))
    print(f'[*] Connected with {app.user}')

@app.command()
async def userinfo(ctx, *, user: nextcord.Member = None):
    if user is None:
        user = ctx.author   
    """
    print(type(ctx.author))
    date_format = "%Y-%m-%d(%a) %I:%M %p"
    embed = nextcord.Embed(color=0xdfa3ff, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar)
    embed.set_thumbnail(url=user.avatar)
    embed.add_field(name="길드 가입일", value=f'```{user.joined_at.strftime(date_format)}```', inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join position", value=f'```{str(members.index(user)+1)}```', inline=False)
    embed.add_field(name="계정 생성일", value=f'```{user.created_at.strftime(date_format)}```', inline=False)
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name=f"역할 [{len(user.roles)-1}개]", value=role_string, inline=False)
    perm_string = '\n'.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
    embed.add_field(name="길드 권한", value=f'```{perm_string}```', inline=False)
    embed.set_footer(text='ID: ' + str(user.id))
    return await ctx.send(embed=embed)"""
    await get_user_info(ctx, ctx.message.content, user)

@app.command()
async def serverinfo(ctx, guild:nextcord.Guild=None):

    if guild == None: 
        guild = ctx.guild

    await get_guild_info(ctx, ctx.message.content, guild)

async def get_user_info(ctx, txt, user): 
    date_format = "%Y-%m-%d %H:%M:%S"

    if str(user.status) == 'online': 
        status = '🟢'

    elif str(user.status) == 'offline':
        status = '⚫'

    elif str(user.status) == 'dnd' or user.status == 'do_not_disturb': 
        status = '🔴'

    elif str(user.status) == 'idle': 
        status = '🟡'

    elif str(user.status) == 'invisible': 
        status = '오프라인으로 표시'
        print(user.status)

    else: 
        status = ''

    connectStatus = ''

    if str(user.desktop_status) != 'offline':
        connectStatus = '데스크탑'

    if str(user.web_status) != 'offline':
        if connectStatus != '':
            connectStatus += ', 웹'

        else: 
            connectStatus = '웹'

    if str(user.mobile_status) != 'offline':
        if connectStatus != '':
            connectStatus += ', 모바일(휴대폰)'

        else: 
            connectStatus = '모바일(휴대폰)'

    if connectStatus == '':
        connectStatus = '미접속'
    
    if status == '' and connectStatus != '미접속':
        status = '미확인'

    activity = ''

    try:
        if str(user.activity.type) == 'Spotify':
            title = user.activity.title
            
            if len(user.activity.artists) > 1: 
                artists = "".join(user.activity.artists)

            else: 
                artists = user.activity.artist

            activity = f'Spotify에서 {title} - {artists} 듣는 중'

        elif str(user.activity.type) == 'ActivityType.playing': 
            application = user.activity.name 

            activity = f'{application} 하는 중'

        elif str(user.activity.type) == 'ActivityType.streaming': 
            name = user.activity.name 

            print(user.activity)
            activity = f'{name} 방송 중'

        elif str(user.activity.type) == 'ActivityType.custom':
            print(user.activity) 
            activity = user.activity

        else: 
            if activity == '':
                activity = '없음'

    except:
        if activity == '': 
            activity = '없음' 

    embed = nextcord.Embed(title=f'{user}님의 정보' if user.bot != True else f'**{user}**봇의 정보', color=colors['MAIN'])
    embed.set_author(name=f'{user}', icon_url=user.avatar if user.avatar != None else user.display_avatar) 
    embed.set_thumbnail(url=user.display_avatar)
    embed.add_field(name='유저', value=f'```{user.name}```')
    embed.add_field(name='별명', value=f'```{user.display_name}```')
    embed.add_field(name='상태', value=f'```{status}```')
    embed.add_field(name='접속 플랫폼', value=f'```{connectStatus}```')
    embed.add_field(name='활동', value=f'```{activity}```', inline=False)
    embed.add_field(name="계정 생성일", value=f'```{user.created_at.strftime(date_format)}```')
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    joinPosition = str(members.index(user)+1)
    embed.add_field(name=f'길드 가입일 ({ctx.guild.member_count}명 중 {joinPosition}번째 유저)', value=f'```{user.joined_at.strftime(date_format)}```', inline=True) 
    if len(user.roles) > 1:
        role_string = '\n'.join([r.mention for r in user.roles][1:])
        embed.add_field(name=f"역할 ({len(user.roles)-1}개)", value=f'{role_string}', inline=False)
    else: 
        embed.add_field(name=f"역할", value='```부여받은 역할이 없습니다.```', inline=False)
    await ctx.send(embed=embed)

async def get_guild_info(ctx, txt, guild): 
    date_format = "%Y-%m-%d %H:%M:%S"

    if guild.rules_channel != None and guild.public_updates_channel != None: 
        guild_community = True
    else:
        guild_community = False

    embed = nextcord.Embed(title=f'{guild} 정보', color=colors['MAIN'])
    embed.set_thumbnail(url=guild.icon)
    print(guild.max_members)
    print(guild.max_presences) 
    print(guild.verification_level)
    print(guild.features)

    embed.add_field(name='서버', value=f'```{guild.name}```') 
    embed.add_field(name='지역', value=f'```{guild.region}```', inline=True)
    embed.add_field(name='오너', value=f'```{guild.owner}```', inline=True)
    embed.add_field(name='서버 생성일', value=f'```{guild.created_at.strftime(date_format)}```', inline=False)
    embed.add_field(name='총 유저', value=f'```{len(guild.members)}명```', inline=True)
    embed.add_field(name='유저', value=f'```{len(guild.humans)}명```', inline=True)
    embed.add_field(name='봇', value=f'```{len(guild.bots)}개```', inline=True)
    embed.add_field(name='부스트 레벨', value=f'```{guild.premium_tier}레벨```', inline=True)
    embed.add_field(name='부스트 횟수', value=f'```{guild.premium_subscription_count}회```', inline=True)
    embed.add_field(name='부스터', value=f'```{len(guild.premium_subscribers)}명```', inline=True)
    embed.add_field(name='커뮤니티', value=f'```활성화```' if guild_community == True else '```비활성화```', inline=True)
    embed.add_field(name='규칙 채널', value=f'{guild.rules_channel.mention}' if guild.rules_channel != None else '```설정되지 않음```', inline=True)
    embed.add_field(name='공지 채널', value=f'{guild.public_updates_channel.mention}' if guild.public_updates_channel != None else '```설정되지 않음```', inline=True)
    embed.add_field(name='시스템 채널', value=f'{guild.system_channel.mention}' if guild.system_channel != None else '```설정되지 않음```', inline=True)
    embed.add_field(name='잠수 채널', value=f'{guild.afk_channel.mention}' if guild.afk_channel != None else '```설정되지 않음```')
    embed.add_field(name='잠수 간주 시간', value=f'```{int(int(guild.afk_timeout)/60)}분```') 
    embed.add_field(name='모든 채널', value=f'```{len(guild.channels)}개```', inline=False)
    embed.add_field(name='카테고리', value=f'```{len(guild.categories)}개```', inline=False)
    embed.add_field(name='채팅 채널', value=f'```{len(guild.text_channels)}개```', inline=True)
    embed.add_field(name='스테이지 채널', value=f'```{len(guild.stage_channels)}개```', inline=True)
    embed.add_field(name='보이스 채널', value=f'```{len(guild.voice_channels)}개```', inline=True)
    embed.add_field(name='역할', value=f'```{len(guild.roles)}개```', inline=True)
    embed.add_field(name='이모지', value=f'```{len(guild.emojis)}개```', inline=True)
    embed.add_field(name='스티커', value=f'```{len(guild.stickers)}개```', inline=True)

    if guild.banner != None: 
        embed.set_image(url=guild.banner)
    await ctx.send(embed=embed) 

async def check_time_site(ctx, txt): 
    sitePointers = ['https', 'http', 'www'] 

    for sitePointer in sitePointers: 
        if sitePointer in sitePointers: 
            break

    index = txt.find(sitePointer)

    site = ''

    for x in range(index, len(txt)):
        if txt[x] != ' ': 
            site += f'{txt[x]}'

        elif txt[x] != '': 
            site += f'{txt[x]}'


    #파인드로 바꾸고 여기서 나온 인덱스 값을 시작으로 띄여쓰기 나올 대까지 사이트 주소로 간주
    #여백이 나오면 사이트 끝 간주

    time = option.Crawling().check_time_site(site)  

    embed = nextcord.Embed(title=f'[사이트](<{site}>) 서버시간', color=colors['MAIN'])
    embed.add_field(name='사이트', value=f'```{site}```')
    embed.add_field(name='서버시간', value=f'{time}')
    clock = await ctx.send(embed=embed)

    await asyncio.sleep(1) 

    for x in range(0, 60*5):
        embed = nextcord.Embed(title=f'서버시간', description=f'[사이트]'+site ,color=colors['MAIN'])
        sec = int(time.split('분')[1].split('초')[0]) + 1 
        timeStamp = time.split('분')[0]
        
        if sec == 60: 
            min = int(time.split('시')[1].split('분')[0]) + 1
            timeStamp = f"{time.split('시')[1]}시 {min}분"
            sec = 0 

        time = f'{timeStamp}분 {sec}초'

        embed.add_field(name='서버시간', value=f'{time}', inline=False)
        await asyncio.sleep(1) 
        await clock.edit(embed=embed)

#Func for some has script
mappings = {"메세지청소":'purge',
            "메세지청소_모두":'purge',
            "추방":'kick', 
            "아침인사":'check_time_mornig',
            "저녁인사":'check_time_night', 
            "질문_핑":'check_ping', 
            "상태":'stats',
            "계산":'cal', 
            "번역":'translate', 
            "날씨":'weather',
            "코로나":'corona', 
            "환율":'exchange', 
            "따라하기":'repeat', 
            "슬로우다운모드설정":'set_slow_mode_delay',
            "슬로우다운모드설정_제거":'del_slow_mode_delay', 
            "학습현황확인":'check_learn_file', 
            "질문_단어_뜻":'find_word', 
            "질문_단어_존재유무":'check_word', 
            "시간계산":'cal_time', 
            "리마인더":'reminder', 
            "사이트시간":'check_time_site'}

#@app.command()
#async def 테스트(ctx): 
    #view = Pet() 
    #msg = await ctx.send('테스트', view=view)

    #await view.wait()

    #await msg.edit(view=None)

@app.command()
async def 로그설정(ctx):
    if ctx.author.guild_permissions.administrator == True:
        settings = "" 

        for option in options: 
            if guilds[str(ctx.guild.id)]['LOG_OPTION'][options.index(option)] == True: 
                state = 'ON'

            else: 
                state = 'OFF'

            settings += f"**{option}** 시 로깅 : `{state}`\n"

        embed = nextcord.Embed(title='로그 설정', description=settings, color=colors['MAIN'])
        await ctx.send(embed=embed, view=DropdownView(str(ctx.guild.id)))

@app.command()
async def 셋업(ctx): 
    if ctx.author.guild_permissions.administrator == True:
        with open('guild.json', 'r', encoding="UTF-8") as g:
            data_guild = json.load(g)
            a = data_guild

        guild = str(ctx.guild.id)

        if guild not in data_guild:
            view = Confirm(ctx.author) 

            embed = nextcord.Embed(title='시스템 다운로드', description='시스템을 다운로드하시겠습니까?', color=colors['MAIN']) 
            msg = await ctx.send(embed=embed, view=view)

            await view.wait()

            await msg.delete()

            if view.value == True: 
                guilds[str(guild)] = 0
                update_guild()

                embed = nextcord.Embed(description=f'```시스템 다운로드되었습니다.```', color=colors['GREEN'])
                await ctx.send(embed=embed)

            else:
                embed = nextcord.Embed(description=f'```시스템 셋업이 취소되었습니다.```', color=colors['RED'])
                await ctx.send(embed=embed)

        else: 
                embed = nextcord.Embed(description=f'```이미 시스템이 다운로드되어 있습니다.```', color=colors['RED'])
                await ctx.send(embed=embed)

@app.command()
async def 로그셋업(ctx):  
    if ctx.author.guild_permissions.administrator == True:
        with open('guild.json', 'r', encoding="UTF-8") as g:
            data_guild = json.load(g)

        guild = str(ctx.guild.id)

        if guild in data_guild:
            if get(ctx.guild.categories, name='MONDAY').name != 'MONDAY':
                view = Confirm(ctx.author)

                embed = nextcord.Embed(title='로그 활성화', description='로그를 활성화하시겠습니까?', color=colors['MAIN']) 
                msg = await ctx.send(embed=embed, view=view)

                await view.wait()

                await msg.delete()
                
                if view.value == True: 
                    category = await ctx.guild.create_category("MONDAY")
                    await ctx.guild.create_text_channel(name='로그', category=category)
                    channel = get(ctx.guild.channels, name="로그")

                    #guilds[guild]['join']['message']
                    #join left message_delete message_edit channel_create channel_delete user_role_change user_nick_change role_create role_delete guild_role_name_change guild_role_color_change user_ban user_unban create_invite delete_invite
                    LOG_OPTION = [True for i in range(len(options))]
                    LOG_OPTION[0] = False
                    guilds[guild] = {'LOG':channel.id, 'LOG_OPTION':LOG_OPTION, 'CATEGORY':category.id, 'JOIN':{'CHANNEL':None, 'MESSAGE':'{user.mention}님이 서버에 입장하셨습니다. (기본값)'}, 'EXIT':{'CHANNEL':None, 'MESSAGE':'{user}님이 서버에 떠나셨습니다. (기본값)'}} 
                    update_guild()

                    embed = nextcord.Embed(description=f'```로그 설정이 완료되었습니다.```', color=colors['GREEN'])
                    await ctx.send(embed=embed)

                else: 
                        embed = nextcord.Embed(description=f'```로그 설정을 취소했습니다.```', color=colors['RED'])
                        await ctx.send(embed=embed)

            else: 
                embed = nextcord.Embed(description=f'```이미 로그 설정이 완료되어 있습니다.```', color=colors['RED'])
                await ctx.send(embed=embed)

        else: 
                embed = nextcord.Embed(description=f'```시스템이 다운로드되어있지 않습니다.```', color=colors['RED'])
                await ctx.send(embed=embed)

@app.command()
async def 삭제(ctx): 
    if ctx.author.guild_permissions.administrator == True:
        with open('guild.json', 'r', encoding="UTF-8") as g:
            data_guild = json.load(g)

        guild = str(ctx.guild.id)

        if guild in data_guild:

            if get(ctx.guild.categories, name='MONDAY') != None:
                
                view = Confirm(ctx.author) 

                embed = nextcord.Embed(title='먼데이 삭제', description='먼데이 시스템을 삭제하시겠습니까?', color=colors['MAIN']) 
                msg = await ctx.send(embed=embed, view=view)

                await view.wait()

                await msg.delete()

                if view.value == True:
                    category = get(ctx.guild.categories, name='MONDAY')


                    for channel in category.text_channels:
                        await channel.delete()
                    await category.delete()

                    del guilds[guild] 
                    update_guild()

                    embed = nextcord.Embed(description=f'```시스템이 삭제되었습니다.```', color=colors['GREEN'])
                    await ctx.send(embed=embed)
                else: 
                    embed = nextcord.Embed(description=f'```시스템이 삭제가 취소되었습니다.```', color=colors['RED'])
                    await ctx.send(embed=embed)


        else:
            embed = nextcord.Embed(description=f'```시스템이 다운로드되어 있습니다.```', color=colors['RED'])
            await ctx.send(embed=embed)

@app.command()
async def 먼데이(ctx, *, text=None):
    if text != None:
        tag, txt = await get_pattern(text)
        inputValue = tag, txt

    else: 
        inputValue = None
        tag = None

    msg = await get_response(inputValue)

    if tag not in mappings:
        await ctx.send(msg)

    if tag in mappings: 
        code = f'{mappings[tag]}(ctx,txt)'
        await eval(code)

#Check Unknown command and Handler error command
@app.event
async def on_command_error(ctx, error):
    if type(error) == nextcord.ext.commands.errors.CommandNotFound: 
        pass
    else: 
        print(error)

@app.event
async def on_member_join(user): 
    with open('guild.json', 'r', encoding="UTF-8") as g:
            data_guild = json.load(g)

    if data_guild[str(user.guild.id)]["JOIN"]["CHANNEL"] != None:
        txt = data_guild[str(user.guild.id)]["JOIN"]["MESSAGE"]

        if '(기본값)' in txt: 
            txt = txt.split(' (기본값)')[0]

        channel = app.get_channel(int(data_guild[str(user.guild.id)]['JOIN']["CHANNEL"]))
        #await channel.send(f'{user.mention}님 안녕하세요')
        await channel.send(eval("f\'"+f'{txt}'+"\'"))

        embed = nextcord.Embed(title="입장", description='서버에 입장하셨습니다.')
        embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
        embed.set_author(name=f'{user}', icon_url=user.display_avatar)   
        embed.set_footer(text=f"{user.guild.name} | ID : {user.id}")
        await logging(str(user.guild.id), embed=embed, event='서버 입장')

@app.event
async def on_member_remove(user): 
    with open('guild.json', 'r', encoding="UTF-8") as g:
            data_guild = json.load(g)

    if data_guild[str(user.guild.id)]["EXIT"]["CHANNEL"] != None:
        txt = data_guild[str(user.guild.id)]["EXIT"]["MESSAGE"]

        if '(기본값)' in txt: 
            txt = txt.split(' (기본값)')[0]

        channel = app.get_channel(int(data_guild[str(user.guild.id)]['EXIT']["CHANNEL"]))
        #await channel.send(f'{user.mention}님 안녕히 가세요')
        await channel.send(eval("f\'"+f'{txt}'+"\'"))

        embed = nextcord.Embed(title="퇴장", description='서버에서 퇴장하셨습니다.')
        embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
        embed.set_author(name=f'{user}', icon_url=user.display_avatar)   
        embed.set_footer(text=f"{user.guild.name} | ID : {user.id}")
        await logging(str(user.guild.id), '서버 퇴장', embed=embed)

@app.event
async def on_voice_state_update(member, before, after): 
    if before.channel == None:
        beforeMembers = 0

    else: 
        beforeMembers = len(before.channel.members)

    if after.channel == None:
        afterMembers = 0

    else:
        afterMembers = len(after.channel.members)

    if afterMembers > beforeMembers:
        event = 'join'

    
    elif afterMembers < beforeMembers:
        event = 'leave'

    elif afterMembers == 0: 
        event = 'leave'
        
    if event == 'join':
        embed = nextcord.Embed(title="입장", description='보이스 채널에 입장하셨습니다.')
        embed.add_field(name='**유저**', value=f'```{member}```', inline=True)
        embed.add_field(name='**채널**', value=f'{after.channel.mention if after.channel != None else before.channel.mention}', inline=True)
        embed.set_author(name=f'{member}', icon_url=member.avatar if member.avatar != None else member.display_avatar)   
        embed.set_footer(text=f"{member.guild.name} | ID : {member.id}")
        await logging(str(member.guild.id), '보이스 채널 입장', embed=embed)

    else: 
        embed = nextcord.Embed(title="퇴장", description='보이스 채널에서 퇴장하셨습니다.')
        embed.add_field(name='**유저**', value=f'```{member}```', inline=True)
        embed.add_field(name='**채널**', value=f'{before.channel.mention if before.channel != None else after.channel.mention}', inline=True)
        embed.set_author(name=f'{member}', icon_url=member.avatar if member.avatar != None else member.display_avatar)   
        embed.set_footer(text=f"{member.guild.name} | ID : {member.id}")
        await logging(str(member.guild.id), '보이스 채널 퇴장', embed=embed)

@app.event
async def on_message_delete(message): 
    entry = await message.guild.audit_logs(action=nextcord.AuditLogAction.message_delete, limit=1).get()

    if message.author.bot != True:
        embed = nextcord.Embed(title="메세지 삭제", description='메세지가 삭제되었습니다.')
        embed.add_field(name='**전송한 유저**', value=f'```{message.author}```', inline=True)
        embed.add_field(name='**채널**', value=f'{message.channel.mention}', inline=True)
        embed.add_field(name='**삭제된 메세지**', value=f'```{message.content}```', inline=False)
        embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar if entry.user.avatar != None else entry.user.display_avatar)   
        embed.set_footer(text=f"{entry.guild.name} | ID : {entry.user.id}")
        await logging(str(entry.guild.id), '메세지 삭제', embed=embed)

@app.event
async def on_message_edit(before, after): 
    if after.author.bot != True:
        embed = nextcord.Embed(title="메세지 수정", description='메세지가 수정되었습니다.')
        embed.add_field(name='**수정한 유저**', value=f'```{after.author}```', inline=True)
        embed.add_field(name='**채널**', value=f'{after.channel.mention}', inline=True)
        embed.add_field(name='**변경 전 메세지**', value=f'```{before.content}```', inline=False)
        embed.add_field(name='**변경 후 메세지**', value=f'```{after.content}```', inline=False)
        embed.set_author(name=f'{after.author}', icon_url=after.author.avatar if after.author.avatar != None else after.author.display_avatar)   
        embed.set_footer(text=f"{after.guild.name} | ID : {after.author.id}")
        await logging(str(after.guild.id), '메세지 수정', embed=embed)

@app.event
async def on_guild_channel_create(channel):
    entry = await channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_create, limit=1).get()
    if entry.user.bot != True:
        embed = nextcord.Embed(title="채널 생성", description='채널이 생성되었습니다.')
        embed.add_field(name='**유저**', value=f'```{entry.user}```', inline=True)
        embed.add_field(name='**채널**', value=f'{channel.mention}', inline=True)
        embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar if entry.user.avatar != None else entry.user.display_avatar)   
        embed.set_footer(text=f"{channel.guild.name} | ID : {entry.user.id}")
        await logging(str(channel.guild.id), '채널 생성', embed=embed)

@app.event
async def on_guild_channel_delete(channel): 
    entry = await channel.guild.audit_logs(action=nextcord.AuditLogAction.channel_delete, limit=1).get()
    if entry.user.bot != True:
        embed = nextcord.Embed(title="채널 삭제", description='채널이 삭제되었습니다.')
        embed.add_field(name='**유저**', value=f'```{entry.user}```', inline=True)
        embed.add_field(name='**채널**', value=f'```{channel}```', inline=True)
        embed.set_author(name=f'{entry.user}', icon_url=entry.user.avatar if entry.user.avatar != None else entry.user.display_avatar)   
        embed.set_footer(text=f"{channel.guild.name} | ID : {entry.user.id}")
        await logging(str(channel.guild.id), '채널 삭제', embed=embed)

@app.event
async def on_member_update(before, after): 
    user = after
    log = await after.guild.audit_logs(action=nextcord.AuditLogAction.member_update, limit=1).get()

    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)

        embed = nextcord.Embed(title="역할 추가", description='역할이 추가되었습니다.')
        embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
        embed.add_field(name='**역할**', value=f'```{newRole}```', inline=True)
        embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
        embed.set_footer(text=f"{after.guild.name} | ID : {log.user.id}")
        await logging(str(after.guild.id), '유저 역할 변경', embed=embed)

    elif len(before.roles) > len(after.roles): 
        oldRole = next(role for role in before.roles if role not in after.roles)

        embed = nextcord.Embed(title="역할 제거", description='역할이 제거되었습니다.')
        embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
        embed.add_field(name='**역할**', value=f'```{oldRole}```', inline=True)
        embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
        embed.set_footer(text=f"{after.guild.name} | ID : {log.user.id}")
        await logging(str(after.guild.id), '유저 역할 변경', embed=embed)

    elif before.nick != after.nick: 
        if after.nick == None: 
            after.nick = after.name

        if before.nick == None:
            before.nick = before.name

        embed = nextcord.Embed(title="별명 변경", description='별명이 변경되었습니다.')
        embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
        embed.add_field(name='**변경 전 별명**', value=f'```{before.nick}```', inline=False)
        embed.add_field(name='**변경 후 별명**', value=f'```{after.nick}```', inline=True)
        embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
        embed.set_footer(text=f"{after.guild.name} | ID : {log.user.id}")
        await logging(str(after.guild.id), '유저 닉네임 변경', embed=embed)

@app.event
async def on_guild_role_create(role):
    log = await role.guild.audit_logs(action=nextcord.AuditLogAction.role_create, limit=1).get()

    embed = nextcord.Embed(title="역할 생성", description='역할이 생성되었습니다.')
    embed.add_field(name='**역할**', value=f'```{role}```', inline=True)
    embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
    embed.set_footer(text=f"{role.guild.name} | ID : {log.user.id}")
    await logging(str(role.guild.id), '역할 생성', embed=embed)

@app.event
async def on_guild_role_delete(role):
    log = await role.guild.audit_logs(action=nextcord.AuditLogAction.role_delete, limit=1).get()

    embed = nextcord.Embed(title="역할 삭제", description='역할이 삭제되었습니다.')
    embed.add_field(name='**역할**', value=f'```{role}```', inline=True)
    embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
    embed.set_footer(text=f"{role.guild.name} | ID : {log.user.id}")
    await logging(str(role.guild.id), '역할 삭제', embed=embed)

@app.event
async def on_guild_role_update(before, after):
    log = await after.guild.audit_logs(action=nextcord.AuditLogAction.role_update, limit=1).get()

    if before.name != after.name: 
        embed = nextcord.Embed(title="역할 이름 변경", description='역할 이름이 변경되었습니다.')
        embed.add_field(name='**변경 전 이름**', value=f'```{before.name}```', inline=True)
        embed.add_field(name='**변경 후 이름**', value=f'```{after.name}```', inline=True)
        embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
        embed.set_footer(text=f"{after.guild.name} | ID : {log.user.id}")
        await logging(str(after.guild.id), '역할 이름 변경',  embed=embed)

    elif before.colour != after.colour:
        embed = nextcord.Embed(title="역할 색상 변경", description='역할 색상이 변경되었습니다.')
        embed.add_field(name='**변경 전 색상**', value=f'```{before.colour}```', inline=True)
        embed.add_field(name='**변경 후 색상**', value=f'```{after.colour}```', inline=True)
        embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
        embed.set_footer(text=f"{log.guild.name} | ID : {log.user.id}")
        await logging(str(log.guild.id), '역할 색상 변경', embed=embed)

@app.event
async def on_member_ban(guild, user):
    log = await guild.audit_logs(action=nextcord.AuditLogAction.ban, limit=1).get()

    embed = nextcord.Embed(title="유저 차단", description='유저가 차단되었습니다.')
    embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
    embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
    embed.set_footer(text=f"{log.guild.name} | ID : {log.user.id}")
    await logging(str(log.guild.id), '유저 차단',  embed=embed)

@app.event
async def on_member_unban(guild, user): 
    log = await guild.audit_logs(action=nextcord.AuditLogAction.unban, limit=1).get()

    embed = nextcord.Embed(title="유저 차단 해제", description='유저의 차단이 해제되었습니다.')
    embed.add_field(name='**유저**', value=f'```{user}```', inline=True)
    embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
    embed.set_footer(text=f"{log.guild.name} | ID : {log.user.id}")
    await logging(str(log.guild.id), '유저 차단 해제', embed=embed)

@app.event
async def on_invite_create(invite):
    log = await invite.guild.audit_logs(action=nextcord.AuditLogAction.invite_create, limit=1).get()

    date_diff = invite.expires_at - invite.created_at
    day = int(date_diff.days)	
    hour = int(date_diff.seconds / 3600)
    minute = int(date_diff.seconds / 60)
    sec = int(date_diff.seconds) - minute*60 

    if day != 0 and hour != 0:
        date = f'{day}일 {hour}시간 후'

    else: 
        date = f'{minute}분 {sec}초 후'

    embed = nextcord.Embed(title="초대코드 생성", description='초대코드가 생성되었습니다.')
    embed.add_field(name='**생성 유저**', value=f'```{log.user}```', inline=True)
    embed.add_field(name='**채널**', value=f'```{invite.channel}```', inline=True)
    embed.add_field(name='**만료**', value=f'```{date}```', inline=False)
    embed.add_field(name='**초대코드**', value=f'```{invite}```', inline=False)
    embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
    embed.set_footer(text=f"{log.guild.name} | ID : {log.user.id}")
    await logging(str(log.guild.id), '초대코드 생성', embed=embed)
   
@app.event
async def on_invite_delete(invite):
    log = await invite.guild.audit_logs(action=nextcord.AuditLogAction.invite_delete, limit=1).get()

    embed = nextcord.Embed(title="초대코드 삭제", description='초대코드가 삭제되었습니다.')
    embed.add_field(name='**채널**', value=f'```{invite.channel}```', inline=True)
    embed.add_field(name='**사용**', value=f'```{invite.uses if invite.uses != None else 0}회```', inline=True)
    embed.add_field(name='**초대코드**', value=f'```{invite}```', inline=False)
    embed.set_author(name=f'{log.user}', icon_url=log.user.avatar if log.user.avatar != None else log.user.display_avatar)   
    embed.set_footer(text=f"{log.guild.name} | ID : {log.user.id}")
    await logging(str(log.guild.id), '초대코드 삭제', embed=embed)

@app.event
async def on_message(message):
    if str(message.channel.type) == 'private':
        embed = nextcord.Embed(title='오류', description='```개인적인 대화는 곤란해요!```', color=colors['RED'])
        user = message.author
        try:
            await user.send(embed=embed)  
        
        except: 
            pass

    else:
        if message.author.bot == False:
            if str(message.guild.id) in guilds: 
                badwords = ['시발', '씨발', '존나']

                for badword in badwords:
                    if message.content.find(badword) != -1:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention} 욕은 나쁜겁니다!")
                        return # So that it doesn't try to delete the message again.

                await app.process_commands(message)

            else: 
                if '셋업' == message.content: 
                    await app.process_commands(message)

                try:
                    if '먼데이' in str(message.content).split()[0]:
                        embed = nextcord.Embed(description='시스템이 다운로드되어 있지 않은 서버입니다. 먼데이를 이용하시려면 `셋업`을 통해 활성화해주세요', color=colors['RED'])
                        await message.channel.send(embed=embed)

                except IndexError: 
                    if '먼데이' == str(message.content).split()[0]:
                        embed = nextcord.Embed(description='시스템이 다운로드되어 있지 않은 서버입니다. 먼데이를 이용하시려면 `셋업`을 통해 활성화해주세요', color=colors['RED'])
                        await message.channel.send(embed=embed)

#activate
app.run(token)