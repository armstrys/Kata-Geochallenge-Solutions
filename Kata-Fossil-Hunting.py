import streamlit as st
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
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
url = 'https://kata.geosci.ai/challenge/fossil-hunting'
r = get_question(url)

if st.checkbox('**Check to show instructions from Agile for this challenge.**', value=False):
    st.markdown(r.text)

## Set up request framework for QA
st.title('My solution')
st.markdown('The data for this Kata challenge will be randomized based upon the key below. Feel free to change it to check the consistency of answers!')
my_key = st.text_input(label='Enter a key to initiate request (any string of characters)',value='armstrys')

## Input
r = get_data(url, my_key)

st.subheader('The first 400 input data:')
st.markdown(r.text[:400])

st.subheader('Making the text meaningful')
st.write('''
         The input text to this challenge is complicated. We don't have any sort
         of delimiting characters. Both the ages and the content of the samples vary
         in length. We even have samples (at least 1) that don't contain any fossils.
         To extract the samples we are going to use a find all and look for a set of
         4 digits(`0-9`) or a decimal point (`.`) followed by 1 or more of any other character.
         Fortunately, `re` will have no problem recognizing the emojis as other characters!
         
         We'll then create a nested dictionary that is organized first by ages and then
         by fossil. Each fossil will then have a count of it's abundance during that year.
         Later we will need to reorganize this dictionary to be more easily keyed into by
         fossil types, but this initial organization will get us through a few questions.
         ''')

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
            
            ## Assign the sample dictionary to the appropriate age
            abundance_dict.update({age:sample_dict})
        return abundance_dict

    abundance_dict = process_text(r.text)

## Create select box to check abundance
abundance_select = st.selectbox('Choose an age to see the fossil counts!',
                                options=sorted(list(abundance_dict.keys())))
st.write(abundance_dict[abundance_select])

## Q1!
questionNum = 1
st.subheader(f'Question {questionNum}')
st.write('''
         To find the most abundant fossil, just loop through our ages and create
         a new dictionary that stores total abundance counts by fossil type.
         ''')

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

    ## retrieve the most abundant id (for later use) and it's abundance.
    answer1 = max(total_dict.values())
    mostID = max(total_dict.keys(), key=(lambda k: total_dict[k]))

st.write('Here are the abundances of each fossil:')
st.write(total_dict)

st.write(f'The most abundant fossil, {mostID}, was counted **{answer1}** times!')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer1)
    st.write(result)


## Q2!
questionNum = 2
st.subheader(f'Question {questionNum}')
st.write('''
         According to these fossil records, there were some years that had more diversity
         than others. We are going to loop through our dictionary and store the the year that
         has the highest diversity we've seen. If two years have the same diversity, we will
         take the oldest year.
         ''')

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

    answer2 = float(omd_year)

st.write(f'''
         Oldest year of maximum diversity was **{answer2} mya** with all these fossils:
         {''.join((abundance_dict[omd_year].keys()))}
         ''')
if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer2)
    st.write(result)


## Q3!
questionNum = 3
st.subheader(f'Question {questionNum}')
st.write(f'''
         Below we calculate the span (first to last appearance) of the most abundant
         fossil, {mostID}. There is a select box so that you can check the span of other
         fossils as well, but the select box will default to the appropriate fossil to answer
         the question.
         ''')

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

    # Create a select box to calculate span.
    # Make sure most abundant fossil is first in list.
    all_fossils = list(total_dict.keys())
    all_fossils.remove(mostID)
    all_fossils.insert(0,mostID)
    span_select = st.selectbox(label='Calculate the span for which fossil? '+
                                     'The first option is the most abundant.',
                               options=all_fossils)
   
    first, last = span_ID(span_select, abundance_dict)

    answer3 = float(f'{(first-last):.1f}')

st.write(f'''
         {span_select} first appeared {first} mya and was last seen {last} mya.
         That gives a span of **{answer3:.1f} million years**!
         ''')

if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer3)
    st.write(result)


## Q4!
questionNum = 4
st.subheader(f'Question {questionNum}')
st.write('''
         First let\'s organize the years of appearance by fossil. This is
         basically a swap of the keys and values from the first dictionary
         we created.
         ''')

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

legend = ''
for i, items in enumerate(fossilYear_dict.items()):
    fossil, years = items
    sns.distplot(years, label=i, norm_hist=False, kde=True)
    plt.xlim(max(abundance_dict.keys())+10, min(abundance_dict.keys())-10)
    plt.xlabel('Million years ago')
    plt.ylabel('Realtive Abundance')
    plt.title('Relative abundance of fossils through time')
    legend += f'{i}:{fossil}  '
st.write('Key for plot legend below',legend)
plt.legend()
st.pyplot()

st.write('''
         Next we can find the fossil with the youngest appearance and calculate it\'s last appearance.
         You can probably spot this fossil in the chart above.
         ''')

with st.echo():
    @st.cache()
    def findLatecomer(fossilYear_dict):
        '''
        Find the the last fossil to the party'
        '''
        late_year = 1e5
        for fossil, years in fossilYear_dict.items():
            if max(years) < late_year:
                late_year = max(years)
                idFossil = fossil
        return idFossil

    idFossil = findLatecomer(fossilYear_dict)
    first_appear = max(fossilYear_dict[idFossil])
    answer4 = min(fossilYear_dict[idFossil])

st.write(f'''
         The fossil {idFossil} first appeared {first_appear} mya and was present
         until **{answer4} mya**.
         ''')

if st.button(f'Check question {questionNum}'):
    result = check_answer(questionNum,answer4)
    st.write(result)