import streamlit as st
import requests
import numpy as np
import pandas as pd
import io

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
url = 'https://kata.geosci.ai/challenge/true-vertical-depth'  # <--- In week 2, you'll change the name.
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge?', value=True):
    st.markdown(r.text, unsafe_allow_html=True)

## Set up request framework for QA
st.header('Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.header('Let\'s throw the text in a dataframe')

with st.echo():
    cols = [
            'X',
            'Y',
            'Datum',
            'Kickoff',
            'Inclination',
            'Azimuth',
            'MD'
            ]
    
    data = pd.read_csv(io.StringIO(r.text),sep=',',names=cols, na_values=-999.25) #load text to pandas
    data = data[~(data['Datum'] == 'UNK')]
    data['Datum'] = data['Datum'].astype(int)
    data['Inclination'].fillna(0,inplace=True)
    data['Kickoff'].fillna(0,inplace=True)
    
st.dataframe(data.head())
st.write(data.info())

## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():

    answer1 = int(data['Datum'].max())

st.write('The highest datum of all wells is ', answer1)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():

    lowerLength = data['MD'] - data['Kickoff']
    data['TD_Offset'] = np.sin(np.radians(data['Inclination'])) * lowerLength


    answer2 = round(data['TD_Offset'].max())

st.dataframe(data[['Kickoff','MD','Inclination','TD_Offset']]
                        .sort_values('TD_Offset', ascending=False).head())


st.write(f'The maximum offset is {answer2} m.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():

    lowerLength = data['MD'] - data['Kickoff']
    lowerVertical = np.cos(np.radians(data['Inclination'])) * lowerLength
    data['TVDSS'] = data['Datum'] - data['Kickoff'] - lowerVertical 


    answer3 = round(data['TVDSS'].min())

st.dataframe(data[['Datum','Kickoff','MD','Inclination','TVDSS']]
                        .sort_values('TVDSS', ascending=True))


st.write(f'The largest total vertical depth is {answer3} m.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q3!
questionNum = 4
st.header(f'Question {questionNum}')

st.write('''We need to drop some wells. Wells that don\'t reach 2000 m tvdss won\'t be counted,
            and neither will wells that have no deviation. Null azimuths will break
            the function and we know those wells won\'t have a y-offset > 100 m anyway.
         ''')

with st.echo():
    sliceSS = st.slider(label='Depth slice to determine offset:',
                        min_value=-4000, max_value=0, value=-2000)
    # sliceSS = -2000
    
    # Remove wells that don't hit the depth slice or don't kave a kickoff point above
    data_subset = data[data['TVDSS'] < sliceSS].dropna()
    mask_devAbove2000 = ~((data_subset['Datum'] - data_subset['Kickoff']) <= sliceSS)
    data_subset = (data_subset[mask_devAbove2000].dropna())
    
    # Calculate the Y offset between kickoff and depth slice!
    upperSectionSS = data_subset['Datum'] - data_subset['Kickoff']
    lowerVertical = upperSectionSS - sliceSS
    offset2000 = np.tan(np.radians(data_subset['Inclination'])) * lowerVertical
    data_subset['YOffset2000'] = np.abs(np.cos(np.radians(data_subset['Azimuth'])) * offset2000)

    answer4 = len(data_subset.loc[data_subset['YOffset2000']>100,'YOffset2000'])

st.dataframe(data_subset[['Datum','Kickoff','MD','Inclination','TVDSS','YOffset2000']]
                        .sort_values('YOffset2000', ascending=False).head())


st.write(f'{answer4} wells with y offset > 100m at {sliceSS} m depth.')
st.info('Before you check... remember the question asks for offset at -2000 m depth!')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)