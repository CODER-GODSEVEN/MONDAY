from unittest import result
import requests
import urllib3
from bs4 import BeautifulSoup
import numpy as np


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Translate: 
    def __init__(self):
        self.client_id = "PO_w88GyIIIr7Yo6mJ58"
        self.client_secret = "0pN1LQYkFE"

    def delect_lang(self, text): 
        url = "https://openapi.naver.com/v1/papago/detectLangs"

        header = {"X-Naver-Client-Id":self.client_id,
                "X-Naver-Client-Secret":self.client_secret}

        data = {'query':text}

        response = requests.post(url, headers=header, data=data)
        rescode = response.status_code

        if(rescode==200):
            t_data = response.json()
            return t_data['langCode']
        else:
            return "언어를 감지할 수 없습니다."

    def get_translate(self, text, lan='영어'):
        langCode = self.delect_lang(text)

        if langCode == 'en': 
            if lan == '영어':
                lan = 'ko'

        elif langCode != 'ko': 
            lan = 'ko'

        else: 
            if lan == '영어': 
                lan = 'en'

            elif lan == '한글' or lan == '한국어': 
                lan = 'ko'

            elif lan == '일본어': 
                lan = 'ja'


        if langCode == lan: 
            if lan == 'ko': 
                lan = 'en'

            else:
                lan = 'ko'

        data = {'text' : text,
                'source' : langCode,
                'target': lan}

        url = "https://openapi.naver.com/v1/papago/n2mt"

        header = {"X-Naver-Client-Id":self.client_id,
                "X-Naver-Client-Secret":self.client_secret}

        response = requests.post(url, headers=header, data=data)
        rescode = response.status_code

        if(rescode==200):
            t_data = response.json()
            return t_data['message']['result']['translatedText']
        else:
            return "번역할 수 없습니다."

class Crawling: 
    def find_word(self, query, option=None):
        more = False

        key = '77D3FB9B22D930A21AE855CBBB7C2B82'
        url = f'https://krdict.korean.go.kr/api/search?key={key}&part=word&q={query}'
        
        try:
            response = requests.get(url, verify=False).text #.json()['channel'] 
            #response['total'] = 1
            #response['item'] = None
            total = response.split('<total>')[1].split('</total>')[0]  

            word = response.split('<item>')[1].split('<word>')[1].split('</word>')[0]  
            pos = response.split('<pos>')[1].split('</pos>')[0] 
            definition = response.split('<definition>')[1].split('</definition>')[0] 

            results = [] 

            for x in range(0, 5): 
                try:
                    word = response.split('<item>')[1+x].split('<word>')[1].split('</word>')[0]  
                    pos = response.split('<pos>')[1].split('</pos>')[0] 
                    sense = len(response.split('<item>')[1+x].split('<sense>'))

                    for y in range(1, int(sense)): 
                        if word == query.split()[0] and pos == '명사': 
                            table = response.split('<item>')[1+x].split('<sense>')
                            definition = table[y].split('<definition>')[1].split('</definition>')[0] 
                            results.append(definition) 

                except:
                    break

        except: 
            more = True
            try:
                url = f'https://stdict.korean.go.kr/api/search.do?key={key}&req_type=json&q={query}'
                response = requests.get(url, verify=False).json()['channel'] 

            except:
                return False

        if more == True:
            total = response['total'] 
            items = response['item']

            output = []

            if int(total) >= 1: 
                for item in items: 
                    if query.split()[0] == item['word'] and item['pos'] == '명사': 
                        output.append(item['sense']['definition'])

                if option == None: 
                    if len(output) >= 1: 
                        return output
                
                else:
                    return True

            else: 
                return False

        elif more == False: 
            if option == None:
                if int(total) >= 1: 
                    return results 

                else: 
                    return False

            else: 
                return True

    def exchange(self, money): 
        url = requests.get(f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query={money}+환율')
        soup = BeautifulSoup(url.text, "html.parser")

        try:
            table = soup.find('div', class_='cs_foreigninfo').find('span', class_='spt_con up')
            exchange_rate = table.find('strong').text

            return exchange_rate 

        except: 
            try:
                table = soup.find('div', class_='c_rate')
                exchange_rate = table.find('strong').text

                return exchange_rate

            except: 
                return False

    def corona(self, date=None):
        url = requests.get("http://ncov.mohw.go.kr/")
        
        soup = BeautifulSoup(url.text, "html.parser")

        output = [] 

        if date == None:
            death, confirm = soup.find('div', class_='occur_num').find_all('div', class_='box')
            totalList = [death.text.split('(누적)사망')[1], confirm.text.split('다운로드')[0].split('(누적)확진')[1]]

            day, day7 = soup.find('div', class_='occurrenceStatus').find('tbody').find_all('tr')
            death, serious, new, confirm = day.find_all('td')

            dayResult = [death.text, serious.text, new.text, confirm.text] 

            output = [totalList, dayResult]

        elif date == 'today': 
            day, day7 = soup.find('div', class_='occurrenceStatus').find('tbody').find_all('tr')
            death, serious, new, confirm = day.find_all('td')

            dayResult = [death.text, serious.text, new.text, confirm.text]

            output = [dayResult]

        elif date == 'all': 
            death, confirm = soup.find('div', class_='occur_num').find_all('div', class_='box')
            totalList = [death.text.split('(누적)사망')[1], confirm.text.split('다운로드')[0].split('(누적)확진')[1]]

            day, day7 = soup.find('div', class_='occurrenceStatus').find('tbody').find_all('tr')
            death, serious, new, confirm = day.find_all('td')
            death7, serious7, new7, confirm7 = day7.find_all('td')

            #사망, 재원 위중증, 신규 입원, 확진 
            dayResult = [death.text, serious.text, new.text, confirm.text]
            day7Result = [death7.text, serious7.text, new7.text, confirm7.text]

            output = [totalList, dayResult, day7Result]

        elif date == 'total':
            death, confirm = soup.find('div', class_='occur_num').find_all('div', class_='box')
            totalList = [death.text.split('(누적)사망')[1], confirm.text.split('다운로드')[0].split('(누적)확진')[1]]

            output = [totalList]

        return output
            
    def weather(self, location=None, option=False): 
        if location == None: 
            location = '모현동'

        url = f'https://search.naver.com/search.naver?query={location}날씨'
        response = requests.get(url) 
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find('section', class_='sc_new cs_weather_new _cs_weather')

        location = table.find('div', class_='title_area _area_panel').find('h2', 'title').text
        temp = table.find('div', class_='weather_graphic').find('strong').text.split('현재 온도')[1]
        weatherState = table.find('div', class_='inner').find('span', class_='blind').text

        infoList = [location, temp, weatherState]

        infoTable = table.find('div', 'temperature_info')

        windDirection = infoTable.find('dl', class_='summary_list').find_all('dt', 'term')[2]
        humid, prec, wind = infoTable.find('dl', class_='summary_list').find_all('dd', 'desc') 

        #강수확률 습도 바람 바람(방향)
        sumList = [humid.text, prec.text, wind.text, windDirection.text.split('(')[1].split(')')[0]]

        outPut = infoList

        #print(f"현재 {location}의 온도는 {temp}이고, 날씨는 {weatherState}입니다.")

        if option != False: 
            outPut.extend(sumList)

            #print(f'또한, 습도는 {sumList[0]}이고, 강수확률은 {sumList[1]}이며, 바람속도는 {sumList[2]}입니다.')

        return outPut