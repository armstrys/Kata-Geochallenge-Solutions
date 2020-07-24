import streamlit as st
import requests
import re
import itertools
import numpy as np

st.warning('''
           **Warning!** This is a soultion. If you are looking to do these 
           [Agile Geosciences](https://agilescientific.com/blog/2020/4/16/geoscientist-challenge-thyself) 
           challenges on your own then please visit this
           [Jupyter Notebook](https://colab.research.google.com/drive/1eP68NTV-GA3R-BYUh-CUxcgYDQ5IuetS)
           to get started.
           ''')

## Cached functions to limit requests
@st.cache()
def get_data(url, key):
    params = {'key':my_key}
    r = requests.get(url, params)
    return r

@st.cache()
def get_question(url):
    r = requests.get(url)
    return r

@st.cache(suppress_st_warning=True)
def check_answer(questionNum,answer):
    params = {'key':my_key,
              'question':questionNum,
              'answer':answer
             }
    result = requests.get(url, params).text
    if 'correct'  in result[0:8].lower():
        st.balloons()
    return result

## Request Challenge Description
url = 'https://kata.geosci.ai/challenge/boreholes'  # <--- In week 2, you'll change the name.
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge?', value=True):
    st.markdown(r.text)

## Set up request framework for QA
st.header('Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)
st.header('Here is the input:')
st.text(r.text)

with st.echo():
    boreholes = np.array(eval(r.text))


## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():
    def how_many(boreholes):
        return len(boreholes[:,0])

    answer1 = int(how_many(boreholes))

st.write('Number of boreholes = ', answer1)
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer1))

## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():
    def distance(boreholes,bID1,bID2):
        borehole1 = boreholes[bID1] 
        borehole2 = boreholes[bID2]
        d = np.sqrt(np.sum((borehole1 - borehole2)**2))
        return d

    answer2 = int(round(distance(boreholes,0,1)))

st.write('Total sandstone beds = ', answer2)
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer2))

## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():
    def mean_distance(boreholes):
        count = 0
        sumDistance = 0
        for i in itertools.combinations(list(range(len(boreholes[:,0]))),2):
            sumDistance += distance(boreholes,i[0],i[1])
            count+=1
        return sumDistance/count

    answer3 = int(round(mean_distance(boreholes)))

st.write('Mean distance between boreholes:',answer3)
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer3))


## Q4!
questionNum = 4
st.header(f'Question {questionNum}')

with st.echo():
    def clump(boreholes, number, distance_thresh):
        clump = np.zeros(len(boreholes[:,0]))
        for i in range(len(boreholes[:,0])):
            dx = np.zeros(len(boreholes[:,0]))
            for j in range(len(boreholes[:,0])):
                dx[j] = distance(boreholes,i,j)
            dx.sort()
            clump[i] = (np.mean(dx[1:int(number)+1]) < distance_thresh)
        return sum(clump)

    answer4 = int(clump(boreholes,answer1/5,answer3/4))

st.write('Number in clump:',answer4)
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer4))    