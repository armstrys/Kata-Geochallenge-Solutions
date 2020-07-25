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
    if 'correct' in result[0:8].lower():
        st.balloons()
    return result


## Request Challenge Description
url = 'https://kata.geosci.ai/challenge/birthquakes' 
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge.', value=True):
    st.markdown(r.text)

## Set up request framework for QA
st.title('My solution')
st.markdown('''For this challenge, the data will come from a date if entered in the same format as the date below.
               Feel free to change it to check the consistency of answers!
            ''')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='1990-08-27')

## Input
r = get_data(url, my_key)

st.subheader('The first 1000 input data:')
st.text(r.text[:1000])
st.write('''
        These text records are separated by `\\n` and `|` and therefore should
        be handled pretty nicely by the `pandas.read_csv`. We just need use `io.StringIO`
        to convert the text to something Pandas can read.
        ''')
with st.echo():

    ## read text to pandas
    data = pd.read_csv(io.StringIO(r.text),sep='|') #load text to pandas

    ## Strip comment character out of headers
    cols = data.columns
    data.columns = [c.strip('#') for c in cols] # strip comment characters out of columns

st.write('First 10 rows of the dataframe:')
st.dataframe(data.head(10))

## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')
st.write('How many records do we have?')

with st.echo():

    answer1 = len(data)

st.write(f'There are **{answer1} records**.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.subheader(f'Question {questionNum}')
st.write('What is the depth of the largest earthquake?')

with st.echo():
    ## Sort by magnitude and depth to make sure we match the right criteria
    data.sort_values(by=['Magnitude','Depth/km'], ascending=False, inplace=True)

    ## Pull the top record and get the depth in meters.
    depth = data.iloc[0]['Depth/km']*1e3
    answer2 = round(depth)

st.dataframe(data.head())

st.write(f'The largest earthquake on this day was **{answer2:.0f} meters** deep!')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.subheader(f'Question {questionNum}')
st.write('''
         Now we will define the Haversin formula, which Streamlit unfortunately didn't
         render correctly in the instructions. [Here is the wikipedia entry.](https://en.wikipedia.org/wiki/Haversine_formula)
         We then use this formula to calculate the distance between the two
         largest earthquakes from the datafrane we sorted in question 2.
         ''')

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

    loc1 = data.iloc[0][['Latitude','Longitude']].values
    loc2 = data.iloc[1][['Latitude','Longitude']].values
    answer3 = int(haversine(loc1, loc2))

st.write(f'The epicenters of the two largest earthquakes were ~**{answer3} km** apart.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.subheader(f'Question {questionNum}')
st.write('''
         Lastly, let's check how many pairs of earthquakes were within 100 km
         of each other on this day.
         ''')

with st.echo():
    count = 0
    comb = itertools.combinations(data.loc[:,['Latitude','Longitude']].values,2)

    for loc1, loc2 in comb:
        if haversine(loc1,loc2) < 100:
            count += 1

answer4 = int(count)

st.write(f'There were **{answer4}** pairs of earthquakes within 100 km of each other.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)
