#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
from bs4 import BeautifulSoup
import requests


# # Postal Code extraction

# In[50]:


link = "https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M"
get_text = requests.get(link).text
xml = BeautifulSoup(get_text, 'xml')
table=xml.find('table')
columns = ['Postalcode','Borough','Neighborhood']
df = pd.DataFrame(columns = columns)

# Search for postcodes, borough and neighborhood 
for tr_cell in table.find_all('tr'):
    row_data=[]
    for td_cell in tr_cell.find_all('td'):
        row_data.append(td_cell.text.strip())
    if len(row_data)==3:
        df.loc[len(df)] = row_data


# In[51]:


df.head(12)


# # Data treatment

# In[52]:


#1)Bring just rows where Borough is diferent from 'Not assigned'
df = df[df.Borough != 'Not assigned']

#2)If a cell has a borough but a Not assigned neighborhood, then the neighborhood will be the same as the borough. So for the 9th cell in the table on the Wikipedia page, the value of the Borough and the Neighborhood columns will be Queen's Park.
for index, row in df.iterrows():
    if row['Neighborhood'] == 'Not assigned':
        row['Neighborhood'] = row['Borough']

#3)Grouping per postcode and bringing neighborhoods and boroughs to the same line  
df=df.groupby(['Postalcode','Borough'])['Neighborhood'].apply(','.join).reset_index()
df.head(15)


# In[53]:


df.shape


# # Geting geo data

# In[54]:


geo_data=pd.read_csv('http://cocl.us/Geospatial_data')


# In[55]:


geo_data.head(10)


# In[62]:


geo_data.rename(columns={'Postal Code':'Postalcode'},inplace=True)
df_geo = pd.merge(geo_data, df, on='Postalcode')


# In[63]:


df_geo


# In[108]:


# create map of New York using latitude and longitude values
map = folium.Map(location=[43.806686, -79.194353], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(df_geo['Latitude'], df_geo['Longitude'], df_geo['Borough'], df_geo['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='green',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map) 
map

