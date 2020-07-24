import streamlit as st
import requests
import re

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
url = 'https://kata.geosci.ai/challenge/fossil-hunting'  # <--- In week 2, you'll change the name.
r = get_question(url)
st.markdown(r.text)

## Set up request framework for QA
st.header('Solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.header('The first 400 input data:')
st.markdown(r.text[:400])

st.header('Making the text meaningful')
with st.echo():
    @st.cache()
    def process_text(text):
        '''
        Take repeating pattern of numbers and emoji and create an abundance dict.
        We can then process this abundance dictionary ({Age: {fossil: count}}) to answer the questions. 
        '''
        # Find all instances of 1-precision numbers followed by non-digits
        samples = re.findall(pattern=r'[0-9.]{1,5}[^0-9.]+', string=text)

        abundance_dict = {}
        for sample in samples:
            sample_dict = {}
            # separate numbers from emojis
            age = float(re.search(pattern=r'[0-9.]{1,5}', string=sample).group(0))
            # separate emojis
            fossils = re.search(pattern=r'[^0-9.]+', string=sample).group(0)
            for fossil in fossils:
                if fossil not in sample_dict.keys():
                    sample_dict.update({fossil:1})
                else:
                    sample_dict[fossil] += 1

            abundance_dict.update({age:sample_dict})
        return abundance_dict

    abundance_dict = process_text(r.text)
    st.write('Here are the first 5 entries in our new dictionary!')
    st.write(dict(list(abundance_dict.items())[:5]))

## Q1!
questionNum = 1
st.header(f'Question {questionNum}')

with st.echo():
    @st.cache()
    def total_abundance(abundance_dict):
        '''
        Take the detailed abundance dictionary and calculate total abundance of each fossil.
        '''
        total_dict = {}
        for fossils in abundance_dict.values():
            for fossil, abund in fossils.items():
                if fossil not in total_dict.keys():
                    total_dict.update({fossil:abund})
                else:
                    total_dict[fossil] += abund
        return total_dict
    total_dict = total_abundance(abundance_dict)
    st.write(total_dict)

    mostID = max(total_dict.keys(), key=(lambda k: total_dict[k]))
    answer1 = max(total_dict.values())

st.write('Number of records: ', answer1)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.header(f'Question {questionNum}')

with st.echo():
    @st.cache()
    def oldest_max_diversity(abundance_dict):
        '''
        Find the oldest year with the maximum amount of diversity seen.
        '''
        omd = 0
        omd_year = 0
        for year, fossils in abundance_dict.items():
            if len(fossils) > omd:
                omd = len(fossils)
                omd_year = year
            elif len(fossils) == omd and year > omd_year:
                omd = len(fossils)
                omd_year = year

        return omd_year, omd
    omd_year, omd = oldest_max_diversity(abundance_dict)
    st.write(f'{omd_year} mya there was a diversity of {omd}!')

    answer2 = float(omd_year)

st.write('Oldest year of max diversity: ', answer2)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.header(f'Question {questionNum}')

with st.echo():
    @st.cache()
    def span_ID(id, abundance_dict):
        '''
        Find the first an last appearance of a given fossil.
        '''
        first = 0
        last = 99999999
        for year, fossils in abundance_dict.items():
            if id in fossils.keys() and year > first:
                first = year
                
            if id in fossils.keys() and year < last:
                last = year

        return first, last
    first, last = span_ID(mostID, abundance_dict)
    st.write(f'{mostID} first appeared {first} mya and was last seen {last} mya!')

    answer3 = float(f'{(first-last):.1f}')


st.write(f'Span of {mostID}: ', answer3)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.header(f'Question {questionNum}')
st.write('First let\'s organize the years of appearance by fossil...')

with st.echo():
    @st.cache()
    def switchKeysValues(abundance_dict):
        '''
        Make the fossils the keys and a list of years the values.
        '''
        fossilYear_dict = {}
        for year, fossils in abundance_dict.items():
            for fossil in fossils:
                if fossil not in fossilYear_dict.keys():
                    fossilYear_dict.update({fossil:[year]})
                else:
                    fossilYear_dict[fossil].append(year)

        return fossilYear_dict
    
    fossilYear_dict = switchKeysValues(abundance_dict)
    
st.write(fossilYear_dict)

st.write('Next we can find the fossil with the youngest appearance and calculate it\'s last appearance')

with st.echo():
    @st.cache()
    def findLatecomer(fossilYear_dict):
        '''
        Find the the last fossil to the party'
        '''
        late_year = 1e5
        for fossil, years in fossilYear_dict.items():
            if max(years) < late_year:
                idFossil = fossil
        return idFossil

    idFossil = findLatecomer(fossilYear_dict)
    first_appear = max(fossilYear_dict[idFossil])
    answer4 = min(fossilYear_dict[idFossil])

st.write(f'The first appearance of {idFossil} was {first_appear} mya.')

st.write(f'The last appearance was: ', answer4)
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)