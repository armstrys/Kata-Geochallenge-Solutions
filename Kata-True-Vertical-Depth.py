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
url = 'https://kata.geosci.ai/challenge/true-vertical-depth'
r = get_question(url)

if st.checkbox('**Check to show instructions from Agile for this challenge.**', value=False):
    st.markdown(r.text, unsafe_allow_html=True)

## Set up request framework for QA
st.title('My solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.subheader('Let\'s throw the text in a dataframe')
st.write('''
         The input text is relatively tame in this case. We can just pass the text
         through `io.StringIO` and into `pandas.read_csv`. We'll then eliminate some
         unknown and `NaN` values.
         ''')

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


## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')
st.write('For question 1, all we need to do is find the max of our `Datum` column.')

with st.echo():

    answer1 = data['Datum'].max()

st.write(f'The highest elevation well is at **{answer1} m** elevation.)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.subheader(f'Question {questionNum}')
st.write('''
         The horizontal offset of each well can be calculated using simple
         trigonometry from the length of the deviated section of the well
         and the deviation inclination. Azimuth is irrelevant here since we are
         calculating radial offset. 
         ''')

with st.echo():

    # length of lower section - possibly deviated
    lowerLength = data['MD'] - data['Kickoff']

    # calculating horizontal offset down to TD
    data['TD_Offset'] = np.sin(np.radians(data['Inclination'])) * lowerLength

    answer2 = round(data['TD_Offset'].max())

st.dataframe(data[['Kickoff','MD','Inclination','TD_Offset']]
                        .sort_values('TD_Offset', ascending=False).head())


st.write(f'The maximum offset is **{answer2} m**.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.subheader(f'Question {questionNum}')
st.write('''
         For question 3, we'll be calculating the total vertical depth (subsea).
         This calculation will be similar to the calcation for question 2, but
         will also need to take into account the datum of the well. The question
         asks for the offset at -2000 m subsea, but you can adjust the slider to
         see how things change.
         ''')

with st.echo():

    # length of lower section - possibly deviated
    lowerLength = data['MD'] - data['Kickoff']

    # use trig to calculate vertical component of deviation
    lowerVertical = np.cos(np.radians(data['Inclination'])) * lowerLength

    # add upper and lower sections of well and adjust for datum
    data['TVDSS'] = data['Datum'] - data['Kickoff'] - lowerVertical 

    answer3 = round(data['TVDSS'].min())

st.dataframe(data[['Datum','Kickoff','MD','Inclination','TVDSS']]
                        .sort_values('TVDSS', ascending=True).head())


st.write(f'The largest total vertical depth is **{answer3} m**.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.subheader(f'Question {questionNum}')

st.write('''We need to drop some wells. Wells that don\'t reach 2000 m tvdss won\'t be counted,
            and neither will wells that have no deviation. Null azimuths will break
            the function and we know those wells won\'t have a y-offset > 100 m anyway.
         ''')

with st.echo():
    sliceSS = st.slider(label='Subsea depth slice to determine offset:',
                        min_value=-4000, max_value=0, value=-2000)
    
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


st.write(f'There are **{answer4}** wells with y-offset greater than 100m at {sliceSS} m depth.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)