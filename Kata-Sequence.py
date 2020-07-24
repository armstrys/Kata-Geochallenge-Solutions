import streamlit as st
import requests
import re
import itertools

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
url = 'https://kata.geosci.ai/challenge/sequence'  # <--- In week 2, you'll change the name.
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
    sequence = r.text

## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():
    def thickness(sequence,lith='S',sample=1):
        return sequence.count(lith)*1

    answer1 = thickness(sequence,lith='S',sample=1)

st.write('Total sand thickness = ',str(answer1))
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.markdown(result)


## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():
    def transition_to_lith(sequence,lith='S',thresh=1):
        regex_pattern = lith+'{'+str(thresh)+',}'
        return re.subn(regex_pattern,'',sequence)[1]

    answer2 = transition_to_lith(sequence,lith='S',thresh=1)

st.write('Total sandstone beds = ',str(answer2))
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.markdown(result)


## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():
    def common_transition(sequence):
        liths = set(sequence)
        transition_dict = {}
        for transition in itertools.permutations(liths,2):
            regex_pattern = ''.join(transition)
            transition_dict[regex_pattern] = re.subn(regex_pattern,'',sequence)[1]
        return transition_dict

    transition_dict = common_transition(sequence)
    answer3 = max(transition_dict.values())

st.write('Lithology transitions:',transition_dict)
st.write('Number of most common:',answer3)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.markdown(result)
