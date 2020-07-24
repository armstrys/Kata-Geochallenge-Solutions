import streamlit as st
import matplotlib.pyplot as plt
import requests
import numpy as np
from scipy.ndimage import measurements as measure

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
url = 'https://kata.geosci.ai/challenge/prospecting'  # <--- In week 2, you'll change the name.
r = get_question(url)
st.markdown(r.text)

## Set up request framework for QA
st.header('Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.header('Here is a look at our maps:')

with st.echo():

    maps = []
    for l in r.text.split('\n'):
        maps.append(np.resize(np.fromstring(l,sep=','),(64,64)))
    maps = np.array(maps)

    map_names = ['Reliability of well data',
                'Reliability of seismic data',
                'Porosity from wells and conceptual models',
                'Fracture density from wells and seismic',
                'Our land position (1 denotes \'our land\').']

    name = st.selectbox('Select map to show',options=map_names)
    plt.imshow(maps[map_names.index(name),:,:])
    plt.title(name)
    plt.colorbar()
    st.pyplot()

## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():
    def zeroReliable(maps):
        rmaps = maps[:2,:,:]
        rmap_comb = np.sum(rmaps, axis=0) == 0

        plt.imshow(rmap_comb)
        plt.title('Total reliability')
        plt.colorbar()
        st.pyplot()

        return rmap_comb

    zrmap = zeroReliable(maps)
    answer1 = int(np.sum(zrmap==1))

st.write('Pixels with zero reliability in wells and seismic: ', answer1)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():
    def aboveP50(maps):
        p50maps = maps[2:4,:,:]
        p50maps[0,:,:] = p50maps[0,:,:] > np.percentile(p50maps[0,:,:],50)
        p50maps[1,:,:] = p50maps[1,:,:] > np.percentile(p50maps[1,:,:],50)
        p50maps_comb = np.prod(p50maps, axis=0)
        count = np.sum(p50maps_comb==1)

        plt.imshow(p50maps_comb)
        plt.title('Por and fracture density both > P50')
        plt.colorbar()
        st.pyplot()

        return p50maps_comb
    

    a50map = aboveP50(maps)
    answer2 = int(np.sum(a50map==1))

st.write('Count of >P50 vals: ', answer2)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():
    def prospects(maps):
        maps_comb = maps[-1,:,:] * ~zrmap * a50map

        plt.imshow(maps_comb)
        plt.title('Prospects')
        plt.colorbar()
        st.pyplot()

        return maps_comb
    pmap = prospects(maps)
    answer3 = int(np.sum(pmap==1))

st.write('Count of >P50 vals: ', answer3)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.header(f'Question {questionNum}')

with st.echo():
    def com(pmap):
        label, numFeat = measure.label(pmap)
        counts = np.bincount(label.ravel())
        label_big = np.argmax(counts[1:])+1
        lat, lon = measure.center_of_mass(input=pmap, labels=label, index=label_big)

        plt.imshow(pmap)
        plt.title('Prospect Center of Mass')
        plt.scatter(lon, lat, s=125, c='red', marker='x')        
        plt.colorbar()
        st.pyplot()

        return lat, lon

    lat, lon = com(pmap)
    answer4 = int(np.floor(lat) * np.floor(lon))

st.write('Product of largest prospect coordinates: ', answer4)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)