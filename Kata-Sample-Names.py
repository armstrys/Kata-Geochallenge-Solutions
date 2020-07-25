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
url = 'https://kata.geosci.ai/challenge/sample-names' 
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge.', value=True):
    st.markdown(r.text)

## Set up request framework for QA
st.title('My solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.subheader('Here are the first 1000 characters of the input:')
st.text(r.text[:1000])

st.subheader('Processing into Pandas dataframe')
with st.echo():
    samples = pd.Series(r.text.split('\n')).str.title()
    samples_df = samples.str.split('_',expand=True).dropna()
    samples_df.columns = ['ID','Basin_Name','FmName','SpecType','Date','PrepCode']
    samples_df['PrepCode'] = samples_df['PrepCode'].str.upper()

st.write('First 10 rows of the dataframe:')
st.dataframe(samples_df.head(10))

## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')
st.write('How many samples in the dataframe?')

with st.echo():
    
    answer1 = len(samples_df)

st.write(f'There are {answer1} valid samples.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.markdown(result)

## Q2!
questionNum = 2
st.subheader(f'Question {questionNum}')
st.write('''
         To find all of the Ainsa Basin samples we will generate a function
         that will look for all matches of a word in the column including
         misspellings as described in the instructions.
         ''')

with st.echo():
    def df_match(samples_df,colName,match):
        '''
        Subset dataframe to rows with a column matching a given string. Item can
        be misspelled as long as first and last characters are correct and all letters
        are present

        Args:
            samples_df (dataframe): Input dataframe.
            colName (str): name of column to search for matches
            match (str): String to match in column.

        Returns:
            df (dataframe): dataframe reduced to rows that match selected column.
        '''

        ## make a forgiving regex expression to match

        firstChar, midChars, lastChar = match[0], match[1:-1], match[-1]

        regExp = re.compile(f'({firstChar}'+ # match first char
                            f'[{midChars}]{{{ len(midChars) }}}'+ # match mid chars in any order
                            f'{lastChar})', re.IGNORECASE) # match last char

        df = (samples_df.loc[samples_df[colName]
                         .str.extract(regExp).dropna().index,:])
        return df

    answer2 = len(df_match(samples_df,'Basin_Name','ainsa'))

st.write(f'There are {answer2} valid samples in the Ainsa Basin.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.markdown(result)

## Q3!
questionNum = 3
st.subheader(f'Question {questionNum}')

with st.echo():

    def isodate(x):
        ''' Check convert the date and null if cannot be converted.
        '''
        try:
            return datetime.fromisoformat(x)
        except ValueError:
            return pd.NaT

    def longest_gap(samples_df):
        '''
        Find the longest gap (on the order of days) between samples in
        the dataframe.
        '''

        samples_df['Date'] = samples_df['Date'].apply(lambda x: isodate(x))
        samples_df = samples_df.loc[samples_df['Date']>datetime(1900,1,1)]

        samples_df = samples_df.sort_values(by=['Date'], ascending=True).reset_index(drop=True)
        samples_df['Days_SincePrev'] = samples_df['Date'].diff(1)
        gap = max(samples_df['Days_SincePrev'].dropna()).days - 1
        return gap
    df_ainsa = df_match(samples_df,'Basin_Name','ainsa')
    answer3 = int(longest_gap(df_ainsa))

st.write(f'Longest gap between Ainsa Basin valid samples was {answer3} days')

if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.markdown(result)