# -*- coding: utf-8 -*-
"""
Created on Sun May  3 18:27:34 2020

@author: Eric Kasper
"""
import json
import requests
import numpy as np
import random
import vlc  

def main():
    jBoard = JeopardyBoard('Double')
    json = jBoard.getJson()
    print(json)

class JeopardyBoard:
    def __init__(self, jRound):
        self.cats = 6
        self.vals = 5
        self.jRound = jRound
        self.categoryTitles, self.values, self.questions,self.answers = self.boardIterator()
        self.playBoardBuildFX()
        self.saveBoardObjectsToTxt()
        
    def getJson(self):
        questions = {}
        i = 0 
        for iCat in range(len(self.getCategoryTitles())):
            for val in self.getValues():
                ques = {}
                ques['value'] = str(val)
                ques['category'] = self.getCategoryTitles()[iCat]
                ques['question'] = self.getQuestion(val,iCat)
                ques['answer'] = self.getAnswer(val,iCat)
                questions[i] = ques
                i = i+1
        return json.dumps(questions)
                
    def saveBoardObjectsToTxt(self):
        with open('questions.txt', 'w') as outfile1,\
             open('answers.txt', 'w') as outfile2,\
             open('categories.txt', 'w') as outfile3:
            outfile1.write('Value' +'\t\t'+ 'CategoryID' + '\t' + 'Question'+'\n')
            outfile2.write('Value' +'\t\t'+ 'CategoryID' + '\t' + 'Answer'  +'\n')
            outfile3.write('CategoryID' +'\t'+ 'Category' +'\n')
            for iCat in range(len(self.getCategoryTitles())):
                category = self.getCategoryTitles()[iCat]
                outfile3.write(str(iCat+1) + '\t\t' + category+'\n')
                for val in self.getValues():
                    outfile1.write(str(val) +'\t\t'+ str(iCat+1) + '\t\t' + self.getQuestion(val,iCat) +'\n')
                    outfile2.write(str(val) +'\t\t'+ str(iCat+1) + '\t\t' + self.getAnswer(val,iCat) +'\n')
                
    def playBoardBuildFX(self):
        p = vlc.MediaPlayer("C:\\Users\\Eric Kasper\\Jeopardy\\jeopardy-board-sms.mp3")
        print("Building Board....")
        p.play()
    
    def getCategoryTitles(self):
        return self.categoryTitles
    
    def getValues(self):
        return self.values
    
    def getQuestions(self):
        return self.questions
    
    def getQuestion(self,val,cat):
        try:
            return self.getQuestions()[cat][np.where(self.getValues() == val)[0][0]]        
        except IndexError:
            print("Out of range.  Try again")            
    
    def getAnswer(self,val,cat):
        try:
            return self.getAnswers()[cat][np.where(self.getValues() == val)[0][0]]        
        except IndexError:
            print("Out of range.  Try again")            
    
    def getAnswers(self):
        return self.answers
    
    def get_response(self,endpoint,suffix = None,parameters=None):
        api_url = 'http://jservice.io//api'
        headers = {'Content-Type': 'application/json'}
        response = requests.get(api_url+"/"+endpoint, headers=headers,params=parameters)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
    
    def get_categories_randomly(self,categoryCount):
        categoryIds = []
        randomClues = []
        
        totalClues = 156810
        for i in range(self.cats):
            while (len(categoryIds) <= i):
                countClue = {'offset':random.randint(1,totalClues)}
                randomClues = self.get_response('clues',parameters=countClue)
                for clue in randomClues:
                    if ((clue['value'] in [100,300,500]) and (self.jRound == 'Single'))\
                        or (clue['value'] in [600,800,1000] and self.jRound == 'Double'):
                        categoryIds.append(clue['category_id'])
                        break
        return categoryIds
        
    def getBoard(self,jRound,categoryIds):
        values = (np.array(range(self.vals))+1) * 100 * (2 if jRound == 'Double' else 1)
        categoryTitles = np.empty(shape=[self.cats], dtype=object)
        questions = np.empty(shape=[self.cats,self.vals], dtype=object)
        answers = np.empty(shape=[self.cats,self.vals], dtype=object)
        
        for i in range(self.cats):
            categoryId = {'id':categoryIds[i]}
            categoryTitles[i] = self.get_response('category',parameters=categoryId)['title']
        for i in range(self.cats):
            for j in range(self.vals):
                clueParams = {'value':values[j],'category':categoryIds[i]}
                clueSet = self.get_response('clues',parameters=clueParams)
                if clueSet != []:
                    clue = random.choice(clueSet)
                    questions[i][j] = clue['question']
                    answers[i][j] = clue['answer']
        return categoryTitles,values,questions,answers
        
    def boardIterator(self):
        i=1
        while True:
            print('Trial: '+str(i))
            categoryIds = self.get_categories_randomly(6)
            categoryTitles,values,questions,answers = self.getBoard(self.jRound,categoryIds)
            i = i+1
            print(str(len(questions[questions==None]))+ ' blank(s).  Trying again')
            if(not(None in questions)):
                break
        return categoryTitles,values,questions,answers

main()
