import streamlit as st
import requests
import io
import itertools
import numpy as np
import pandas as pd

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
url = 'https://kata.geosci.ai/challenge/birthquakes'  # <--- In week 2, you'll change the name.
r = get_question(url)
st.markdown(r.text)

## Set up request framework for QA
st.header('Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='1990-08-27')

## Input
r = get_data(url, my_key)

st.header('The first 1000 input data:')
st.text(r.text[:1000])
with st.echo():
    
    data = pd.read_csv(io.StringIO(r.text),sep='|') #load text to pandas
    cols = data.columns
    data.columns = [c.strip('#') for c in cols] # strip comment characters out of columns

st.dataframe(data)

## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():
    answer1 = int(len(data))

st.write('Number of records: ', answer1)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():
    data.sort_values(by=['Magnitude','Depth/km'], ascending=False, inplace=True)
    data.reset_index(inplace=True)
    depth = data.loc[0,'Depth/km']*1e3

st.dataframe(data.head())

answer2 = int(depth)

st.write('Depth of largest earthquake in meters: ', answer2)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():
    def haversine(loc1, loc2, r=6371.0):
        '''
        Takes lat/lons in degrees and gives the distance between two points.
        '''
        lat1, lon1 = np.radians(loc1.astype(float))
        lat2, lon2 = np.radians(loc2.astype(float))
        a = np.sin((lat2-lat1)/2)**2
        b = np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
        d = 2*r*np.arcsin(np.sqrt(a+b))
        return round(d)

loc1 = data.loc[0,['Latitude','Longitude']].values
loc2 = data.loc[1,['Latitude','Longitude']].values
answer3 = int(haversine(loc1, loc2))

st.write('Distance between two largest quakes in km: ', answer3)
if st.button('Check question '+str(questionNum)):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.header(f'Question {questionNum}')

with st.echo():
    count = 0
    for loc1, loc2 in itertools.combinations(data.loc[:,['Latitude','Longitude']].values,2):
        if haversine(loc1,loc2) < 100:
            count += 1

answer4 = int(count)

st.write('Pairs of earthquakes within 100 km: ', answer4)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)