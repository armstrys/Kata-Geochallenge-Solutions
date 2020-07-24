import streamlit as st
import requests
import re
import numpy as np
import pandas as pd
from datetime import datetime

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
url = 'https://kata.geosci.ai/challenge/sample-names'  # <--- In week 2, you'll change the name.
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge?', value=True):
    st.markdown(r.text)

## Set up request framework for QA
st.header('Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.header('Here are the first 1000 characters of the input:')
st.text(r.text[:1000])

st.header('Formatted:')
with st.echo():
    samples = pd.Series(r.text.split('\n'))
    samples_df = samples.str.split('_',expand=True).dropna()
    samples_df.columns = ['ID','Basin_Name','FmName','SpecType','Date','PrepCode']

    st.dataframe(samples_df)

## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():
    def numSamples(samples_df):
        return len(samples_df)

    answer1 = int(numSamples(samples_df))

st.write('Number of valid samples = ', answer1)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.markdown(result)

## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():
    def numSamplesBasin(samples_df,colName,match):
        regExp = re.compile('(' + match[0]+ '['+match[1:-1]+']{3}' + match[-1] + ')', re.IGNORECASE)
        return samples_df.loc[samples_df[colName].str.extract(regExp).dropna().index,:]

    answer2 = len(numSamplesBasin(samples_df,'Basin_Name','ainsa'))

st.write('Number of valid samples in Ainsa basin = ', answer2)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.markdown(result)

## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():
    def longest_gap(samples_df):

        def isodate(x):
            try:
                return datetime.fromisoformat(x)
            except:
                return pd.NaT

        samples_df['Date'] = samples_df['Date'].apply(lambda x: isodate(x))
        samples_df = samples_df.loc[samples_df['Date']>datetime(1900,1,1)]

        samples_df = samples_df.sort_values(by=['Date'], ascending=True).reset_index(drop=True)
        samples_df['Days_SincePrev'] = samples_df['Date'].diff(1)
        gap = max(samples_df['Days_SincePrev'].dropna()).days - 1
        return gap

    answer3 = int(longest_gap(numSamplesBasin(samples_df,'Basin_Name','ainsa')))

st.write('Longest gap between Ainsa Basin valid samples:',answer3)

if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.markdown(result)