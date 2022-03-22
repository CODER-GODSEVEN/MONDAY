import numpy as np
from numpy import dot
from numpy.linalg import norm
import json
import random

with open('data.json', 'r', encoding="UTF-8") as f:
    datas = json.load(f)

def update():
    with open('data.json', 'w', encoding='UTF-8') as f:
        json.dump(datas, f, ensure_ascii=False)

async def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))

async def cal_sim(inputLayer, hiddenLayer): 
    inLayers = [inputLayer, hiddenLayer] 

    window = inputLayer + hiddenLayer

    for class_ in window:
        if window.count(class_) > 1: 
            window.remove(class_)

    winSize = len(window) 

    resultLayer = {}

    for i in range(0, winSize): 
        if window[i] not in resultLayer:
            resultLayer[window[i]] = i 

    outputLayer = np.zeros(winSize, dtype=int) 
    compLayer = np.zeros(winSize, dtype=int) 

    outLayers = [outputLayer, compLayer] 

    index = 0

    for outLayer in outLayers: 
        for class_ in resultLayer:
            if class_ in inLayers[index]:
                outLayer[resultLayer[class_]] += 1

        index += 1

    return await cos_sim(outputLayer, compLayer)

async def tokenization(sentence, option=None):
    tokens = sentence.split()

    symbols = ['.', ',', '?', '!', '/', '\'', '\"', '$', '^', "(", ")", "#", '@']

    results = [] 

    if '먼데이' in sentence.split(' ')[0]:
        tokens = await clear("".join(sentence.split('먼데이')))

    for token in tokens:
        for symbol in symbols:
            if symbol in token:
                token = token.split(symbol)[0]

                results.append(token)

                if option == None:
                    results.append(symbol)
                    break

                else: 
                    break

        else: 
            results.append(token)

    return results

async def clear(sentence):
    return " ".join(sentence.split())

async def learn(sentence, tag): 
    with open('data.json', 'r', encoding="UTF-8") as f:
        datas = json.load(f)

        if sentence != None:  
            for data in datas: 
                if data['tag'] == tag: 
                    if 'unlearnable' in data['feature']:
                        pass

                    else:
                        txt = " ".join(await tokenization(sentence, True))
                        if txt not in data['patterns']:
                            data['patterns'].append(txt)
                            update()

                            print('updated!', txt)
                        
                        else: 
                            pass

async def get_pattern(sentence):
    if sentence != None:
        with open('data.json', 'r', encoding="UTF-8") as f:
            datas = json.load(f)

            patternList = {} 

            for data in datas: 
                if 'nonresponsible' not in data['feature']:
                    patternList[data['tag']] = 0 

                    for pattern in data['patterns']:
                        score = await cal_sim(await tokenization(sentence, True), await tokenization(pattern, True))

                        if score > patternList[data['tag']]: 
                            patternList[data['tag']] = score

            tag = max(patternList, key=patternList.get)

            if tag == '이해못함': 
                patternList[tag] = 1

            print(f'{tag} [{int(patternList[tag]*100)}%]')

            if int(patternList[tag]*100) >= 70 and int(patternList[tag]*100) < 100: 
                await learn(sentence, tag)

            return tag, sentence
    
    else: 
        return sentence

async def return_data(tag): 
    with open('data.json', 'r', encoding="UTF-8") as f:
        datas = json.load(f)

        for data in datas: 
            if data['tag'] == tag:
                return data

async def get_response(inputList):
    with open('data.json', 'r', encoding="UTF-8") as f:
        datas = json.load(f)

        if inputList != None:
            tag, sentence = inputList
            data = await return_data(tag)

        else: 
            data = await return_data("호명")

        if 'functionable' not in data['feature'] and 'nonresponsible' not in data['feature']:
            return data['responses'][random.randint(0, len(data['responses'])-1)]