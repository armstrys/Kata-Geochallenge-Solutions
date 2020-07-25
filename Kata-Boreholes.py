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
url = 'https://kata.geosci.ai/challenge/boreholes'  
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge.', value=True):
    st.markdown(r.text)

## Set up request framework for QA
st.title('My solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)
st.subheader('Here is the input:')
st.text(r.text)

st.write('''
         Our text is very conveniently written in python-friendly syntax.
         We can directly evaluate the text using `eval()` to form couples and
         then cast to a numpy array.
         ''')
with st.echo():
    boreholes = np.array(eval(r.text))

st.write('First 5 boreholes of new format:',boreholes[:5,:])

## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')

st.write('How many boreholes do we have? Let\'s take the length.')
with st.echo():

    answer1 = len(boreholes)

st.write(f'There are {answer1} boreholes.')
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer1))

## Q2!
questionNum = 2
st.subheader(f'Question {questionNum}')

st.write('''
         To get the distance between the first two boreholes we will create a simple
         function to calculate the distance given our boreholes list and two IDs. In
         Streamlit we will also add a decorator to cache functions so they don't have
         to rerun every time the applet updates. This will be more important later.
         ''')
with st.echo():
    # @st.cache()
    def distance(boreholes,bID1,bID2):
        borehole1 = boreholes[bID1] 
        borehole2 = boreholes[bID2]
        d = np.sqrt(np.sum((borehole1 - borehole2)**2))
        return d

    answer2 = int(round(distance(boreholes,0,1)))

st.write(f'The distance between the first two boreholes is ~{answer2} m.')
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer2))

## Q3!
questionNum = 3
st.subheader(f'Question {questionNum}')

st.write('''
         Glad we created the function above! We will create a new function to loop
         through all combinations of borehole pairs and calculate a mean distance.
         Again, we will cache this function so it doesn't have to rerun frequently.
         ''')
with st.echo():
    @st.cache(suppress_st_warning=True)
    def mean_distance(boreholes):
        '''
        Calculates mean distance between boreholes.

        Args:
            boreholes (array): the coordinate array of the boreholes - our data.
        
        Returns:
            meanDist (float): mean distance of all well coordinates listed in boreholes.

        '''
        funcprogress = st.progress(0)
        distances = []
        comb = itertools.combinations(list(range(len(boreholes))),2)
        comb, comb_count = itertools.tee(comb)
        numComb = sum(1 for ignore in comb_count)

        for i, pair in enumerate(comb):
            x, y = pair
            distances.append(distance(boreholes,x,y))
            funcprogress.progress(i/numComb)

        meanDist = np.mean(distances)

        return meanDist

    answer3 = int(round(mean_distance(boreholes)))

st.write(f'The mean distance between boreholes is {answer3} m.')
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer3))


## Q4!
questionNum = 4
st.subheader(f'Question {questionNum}')

st.write('''
         Time to find some clumps of boreholes! The method below is likely not the
         most efficient, but it will get the job done. The function loops through
         all possible combination of boreholes i and j. We then check the closest
         boreholes to see how many of them are close enough and whether the well
         is considered to be in a clump.
         ''')
with st.echo():
    @st.cache(suppress_st_warning=True)
    def flag_clump(boreholes, number, distance_thresh):
        '''
        Determine whether each well is in a clump as defined by a distance threshold
        for a certain number of neighboring wells to be within.

        Args:
            boreholes (array): the coordinate array of the boreholes - our data.
            number (int): number of wells that need to be within x distance to
                be considered a neighbor.
            distance_thresh (float): distance cutoff to determine number of
                neighboring wells to count.
        
        Returns:
            clump (array): a flag array with the same dimensions as the first
                dimension of the boreholes array. Flag is True for well being in
                clump and false if well is not in a clump.
        '''
        funcprogress = st.progress(0)
        clump = np.zeros(len(boreholes))
        for i in range(len(boreholes)):
            dx = np.zeros(len(boreholes))
            for j in range(len(boreholes)):
                if i==j:  # comparison to itself
                    dx[j]=np.nan
                else:
                    dx[j] = distance(boreholes,i,j)
            dx.sort()
            clump[i] = (np.mean(dx[0:round(number)]) < distance_thresh)
            funcprogress.progress(i/len(boreholes))
        return clump

    answer4 = int(sum(flag_clump(boreholes,answer1/5,answer3/4)))

st.write(f'There are {answer4} wells that are considered in a clump.')
if st.button(f'Check question {questionNum}'):
    st.markdown(check_answer(questionNum,answer4))    