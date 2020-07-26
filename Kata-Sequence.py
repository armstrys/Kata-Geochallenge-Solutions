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

## Cached helper functions to limit requests
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
url = 'https://kata.geosci.ai/challenge/sequence'
r = get_question(url)

if st.checkbox('**Check to show instructions from Agile for this challenge.**', value=False):
    st.markdown(r.text)


## Set up key to generate data for questions.
st.title('My Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')


## Process input text
r = get_data(url, my_key)

st.subheader('Here is the input:')
st.text(r.text)

st.write('''
         We should be able to do most of what we need
         directly with the string. No real processing needed yet.
         ''')
with st.echo():
    sequence = r.text

## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')
st.write('''
         We want to get the total thickess of the sandstone facies 'S'.
         Luckily, there is already a function for that. We just need to count
         the number of occurences and multiply by the sample rate, 1 meter.
         Use the select box to see the other facies thicknesses.
         ''')

with st.echo():

    ## create widget
    facies = list(set(sequence))
    facies.remove('S')         # removing sandstone
    facies = ['S'] + facies    # to put it at the front so it's default

    sample = 1       # 1 meter per count / sample rate
    lith_thick = st.selectbox(label='Total thickness of which facies?',
                        options= facies
                        )
    ## calculate thickness
    answer1 = sequence.count(lith_thick)*sample   #counting occurences in str

st.write(f'Total thickness of facies {lith_thick} is **{answer1} m**.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.markdown(result)


## Q2!
questionNum = 2
st.subheader(f'Question {questionNum}')
st.write('''
         We want to count the total number of beds of a given facies, in this
         case, sandstone, 'S'. We can do this by using a regex pattern.
         Try playing around with the slider and select box to see how counts change.
         ''')

with st.echo():
    
    ## create widgets
    thresh = st.slider(label='Minimum consecutive samples to count a bed',
                       min_value=1, max_value=10, value=1)
    
    lith_count = st.selectbox(label='Count beds of which facies?',
                        options= facies
                        )

    ## find repeating occurences of lith and count
    regex_pattern = lith_count+'{'+str(thresh)+',}'
    answer2 = re.subn(regex_pattern,'',sequence)[1]

st.write(f'''There are **{answer2} beds** of facies {lith_count}
             with a sample threshold of {thresh}''')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.markdown(result)


## Q3!
questionNum = 3
st.subheader(f'Question {questionNum}')
st.write('''
         To calculate the most common facies transition, we will just create a dictionary
         to count all facies transitions and then take the maximum. We can iterate over all
         permutations of the facies list that we created earlier and use regex to flag
         all occurences of that facies change. For example, a sand to mud (`S` -> `M`) transition
         will find all occurences of `SM` in our sequence.
         ''')
with st.echo():
    transition_dict = {}
    for transition in itertools.permutations(facies,2):
        regex_pattern = ''.join(transition)
        transition_dict[regex_pattern] = re.subn(regex_pattern,'',sequence)[1]

    answer3 = max(transition_dict.values())
    answer3ID = max(transition_dict.keys(), key=(lambda k: transition_dict[k]))

st.write('Lithology transitions:',transition_dict)
st.write(f'The most common transision is {answer3ID} and occurs **{answer3}** times!')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.markdown(result)
