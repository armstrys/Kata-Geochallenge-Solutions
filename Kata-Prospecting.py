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
url = 'https://kata.geosci.ai/challenge/prospecting'  
r = get_question(url)

if st.checkbox('Uncheck to hide instructions for this challenge.', value=True):
    st.markdown(r.text)

## Set up request framework for QA
st.title('My solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.subheader('Input data')
st.write('''
         Let's take a look at the maps. We make a list of the map values by splitting
         our text by `\n` and then by `,`. Each line gets resized to a 64x64 np.array
         and appended to the list. We'll also generate a list of titles so we can keep
         track of the maps using the list indices. Use the selectbox below to take a
         look at our maps.
         ''')

with st.echo():

    maps = []
    for l in r.text.split('\n'):
        maps.append(np.resize(np.fromstring(l,sep=','),(64,64)))
    maps = np.array(maps)

    map_names = ['Reliability of well data',
                 'Reliability of seismic data',
                 'Porosity from wells and conceptual models',
                 'Fracture density from wells and seismic',
                 'Our land position (1 denotes \'our land\').'
                 ]

    name = st.selectbox('Select map to show',options=map_names)
    plt.imshow(maps[map_names.index(name),:,:])
    plt.title(name)
    plt.colorbar()
    st.pyplot()

## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')
st.write('''
         To find the pixels with zero total reliability we need to combine the
         first two maps we were provided. Any pixels that are zero in both the well
         and seismic reliability maps will be labeled as unreliable.
         ''')

with st.echo():
    def zeroReliable(maps):
        '''
        Use our maps to generate a new map that has a True label for any pixel that
        has zero reliability in both of our well and seismic reliability maps (these
        are the first two maps in the array).
        '''

        ## define reliability maps
        rmaps = maps[:2,:,:]

        ## combine maps and check if equal to 0
        rmap_comb = np.sum(rmaps, axis=0) == 0

        ## Plot new map - True is unrealiable here
        plt.imshow(rmap_comb)
        plt.title('Unreliable Data')
        plt.colorbar()
        st.pyplot()

        return rmap_comb

    zrmap = zeroReliable(maps)
    answer1 = int(np.sum(zrmap==1))

st.write(f'There are {answer1} pixels with zero reliability.')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.header(f'Question {questionNum}')
st.write('''
         Now that we know where we can trust our data, we can move on to the
         subsurface properties. The code block below combines a >P50 porosity map
         and a >P50 fracture density map to high-grade the best areas on our map.
         Try playing with the sliders to see how things change if you favor porosity
         over fracture density and vice versa.
         ''')

with st.echo():
    def abovePXX(maps,porThresh,fracThresh):
        '''
        Take porosity and fracture density maps to generate a map of combined over
        a threshold for each
        '''
        pmaps = maps[2:4,:,:]
        pmaps[0,:,:] = pmaps[0,:,:] > np.percentile(pmaps[0,:,:],porThresh)
        pmaps[1,:,:] = pmaps[1,:,:] > np.percentile(pmaps[1,:,:],fracThresh)
        pmaps_comb = np.prod(pmaps, axis=0)
        count = np.sum(pmaps_comb==1)

        plt.imshow(pmaps_comb)
        plt.title('Por and fracture density both > P50')
        plt.colorbar()
        st.pyplot()

        return pmaps_comb
    
    porThresh = st.slider(label='Porosity percentile threshold',
                          min_value=0, max_value=100, value=50, step=5)
    fracThresh = st.slider(label='Fracture density percentile threshold',
                           min_value=0, max_value=100, value=50, step=5)

    aXXmap = abovePXX(maps, porThresh, fracThresh)
    answer2 = int(np.sum(aXXmap==1))

st.write(f'''
          There are {answer2} pixels with porosity >P{porThresh}
          and fracture density >P{fracThresh}!
          ''')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.header(f'Question {questionNum}')
st.write('''
         Finally, let's stack our reliability map and the subsurface property
         map to see which areas stand out.
         ''')

with st.echo():

    pmap = maps[-1,:,:] * ~zrmap * aXXmap

    plt.imshow(pmap)
    plt.title('Prospects')
    plt.colorbar()
    st.pyplot()

    answer3 = int(np.sum(pmap==1))

st.write(f'''
         There are {answer3} prospective pixels on this map
         using the cut-offs assigned above.
         ''')

if porThresh!=50 or fracThresh!=50:
    st.warning('''
               **Warning!** The current cut-offs don't match
               the official answer to the question. Check sliders for
               question 2 if you are testing the accuracy of the solution.
               ''')

if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.header(f'Question {questionNum}')
st.write('''
         X marks the spot! Let's calculate the center of mass of the largest
         'prospect' or continuous blob of pixels.
         ''')

with st.echo():
    def com(pmap):
        '''
        Find the center of mass of the largest blob on our binary map.
        Return the coordinates of this point.
        '''
        ## find discrete blobs of pixels and label
        label, numFeat = measure.label(pmap)
        counts = np.bincount(label.ravel())
        label_big = np.argmax(counts[1:])+1

        ## get the center of mass using the label of the largest prospect
        lat, lon = measure.center_of_mass(input=pmap, labels=label, index=label_big)

        ## plot the prospect labels and an x on the center of mass for the largest
        plt.imshow(label, cmap='tab20')
        plt.title('Prospect Center of Mass')
        plt.scatter(lon, lat, s=125, c='red', marker='x')        
        st.pyplot()

        return lat, lon

    lat, lon = com(pmap)
    answer4 = int(np.floor(lat) * np.floor(lon))

st.write(f'The product of largest prospect coordinates is {answer4}.')

if porThresh!=50 or fracThresh!=50:
    st.warning('''
               **Warning!** The current cut-offs don't match
               the official answer to the question. Check sliders for
               question 2 if you are testing the accuracy of the solution.
               ''')

if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)