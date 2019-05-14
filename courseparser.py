import requests
import os
from bs4 import BeautifulSoup
from time import sleep
from platform import system

#Global constants
enumHeader = {
    'Field'  : 0,
    'Grade'  : 1,
    'Average': 2
}


def getIntegerNumber(type):
    courseNumber = input("\nPlease enter required " + type+ ": ")
    while True:
        try:
            courseNumber = int(courseNumber)
            return courseNumber
        except ValueError:
            print(type+" number must be an integer!\n")
            courseNumber = input("Please re-enter required" + type)


def printGradesFromCSV(filename):
        print("\n")
        command = 'csvlook '+filename+'.csv'
        os.system(command)


def getGrades(postPackage):
    with requests.Session() as session:
        get = session.post(
            'https://grades.cs.technion.ac.il/grades.cgi', data=postPackage)
        soup = BeautifulSoup(get.content, features="html5lib")
        tables = soup.find_all("table",{"bgcolor": "#112244"})
        if tables == None:
            return [[],[],[]]
        grades = [[],[],[]]
        gotFirstTable=False
        for table in tables:
            counter=0
            foundHeader = False
            for table_row in table.findAll('tr'):
                if not foundHeader:
                    th = table_row.findAll('th')
                    for column in th:
                        if gotFirstTable and column.text=='':
                            continue
                        grades[0].append(column.text)
                    foundHeader = True
                    continue
                columns = table_row.findAll('td')
                counter=0
                for column in columns:
                    if counter == 0 and gotFirstTable:
                        counter = 1
                        continue
                    if(column.text.startswith("(*)")):
                        continue
                    if counter == 0:
                        grades[1].append(column.text)
                    else:
                        grades[2].append(column.text)
                counter += 1
            gotFirstTable=True
        result = []
        for grade in grades:
            if len(grade) > 0:
                result.append(grade)
        return result



def createCSVfile(filename, grades):
    try:
        filename = filename + ".csv"
        csvfile = open(filename, "w")
        csvfile.write('Field:, Grade:, Average:\n')
        for grade in range(0, len(grades[0])):
            csvfile.write(grades[enumHeader['Field']][grade])
            csvfile.write(",")
            csvfile.write(grades[enumHeader['Grade']][grade])
            csvfile.write(",")
            csvfile.write(grades[enumHeader['Average']][grade])
            csvfile.write("\n")
        csvfile.close()
    except IOError:
        print("Couldn't create " + filename + ".csv file")
        raise SystemExit


def csvToList(filename):
    try:
        grades = [[], [], []]
        filename = filename + ".csv"
        csvfile = open(filename, "r")
        nextLine = csvfile.readline()
        counter = 0
        while len(nextLine) != 0:
            for value in range(0, len(nextLine.split(","))):
                grades[value].append(nextLine.split(",")[value])
            nextLine = csvfile.readline()
        csvfile.close()
        return grades
    except IOError:
        print("Couldn't create " + filename + ".csv file")
        raise SystemExit


def updateGrades(newGrades, oldGrades):
    grades = [[], [], []]
    for grade in range(0, len(newGrades[0])):
        grades[0].append(newGrades[0][grade])
        if newGrades[1][grade] not in oldGrades[1] or newGrades[0][grade] not in oldGrades[0] :
            grades[1].append(newGrades[1][grade]+"<-NEW GRADE")
        else:
            grades[1].append(newGrades[1][grade])
        grades[2].append(newGrades[2][grade])
    return grades


def makeSound(duration, frequency):
    if system() == 'Linux':
        os.system('play -nq -t alsa synth {} sine {}'.format(duration, frequency))
    elif system() == 'Windows':
        from winsound import Beep
        Beep(frequency=800, duration=0.5)



def trackGrades(frequency, currentGradesFileName, postPackage):

    counter = 0
    while True:
        print(str(counter//60) + " minutes passed", end='\r')
        sleep(frequency)
        grades = getGrades(postPackage)
        previousGrades = csvToList(currentGradesFileName)
        for grade in range(0, len(grades[0])):
            newGradesGrade = grades[enumHeader['Grade']][grade]
            if newGradesGrade not in previousGrades[enumHeader['Grade']]:
                createCSVfile(currentGradesFileName, 
                            updateGrades(grades, previousGrades))
                makeSound(duration=0.5, frequency=800)
                printGradesFromCSV(currentGradesFileName)
                return
        counter += frequency


def preparePackage(course, ID, password, date):
    postPackage={
        'Login':    '1',
        'Page':     'grades.html',
        'SEM':      '201801',
        'FromLock': '1',
        'submit':   'proceed'
    }
    postPackage['Course']= str(course)
    postPackage['ID']= str(ID)
    postPackage['Password']= str(password)
    postPackage['SEM'] = date
    return postPackage
