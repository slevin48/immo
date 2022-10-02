import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import folium_static
# import folium
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import immo

import ssl
# to avoid SSLCertVerificationError
ssl._create_default_https_context = ssl._create_unverified_context

# search from data.gouv.fr geo-dvf
@st.cache
def load_data(code_commune):
    # json_data = immo.dvf_commune(postcode)
    url = "https://files.data.gouv.fr/geo-dvf/latest/csv/2021/communes/"+str(code_commune)[:2]+"/"+str(code_commune)+".csv"
    df = pd.read_csv(url)
    df.date_mutation = pd.to_datetime(df.date_mutation).dt.date
    df = df.dropna(subset=['valeur_fonciere','surface_reelle_bati','longitude','latitude'])
    df['prixm2'] = df.valeur_fonciere/df.surface_reelle_bati
    df = df[df.prixm2<10000] 
    df.prixm2 = df.prixm2.astype(int)
    df['marker_color'] = pd.cut(df['prixm2'], bins=4,labels=['blue','green', 'yellow', 'red'])
    df = df.sort_values(by='date_mutation',ascending=False)
    return df

st.sidebar.title("Enter search parameters")

try:
    query_params = st.experimental_get_query_params()
    code = query_journal = query_params['code'][0]

except:
#   if no code is passed with the URL
    st.experimental_set_query_params(code="59350")
    query_params = st.experimental_get_query_params()
    query_params = st.experimental_get_query_params()
    code = query_journal = query_params['code'][0]

postcode = st.sidebar.text_input("Code Commune",code)
expander = st.sidebar.expander("Search 'Code commune' for city")
city = expander.text_input("Enter city",value="Lille")
expander.markdown("<a href='https://www.google.com/search?q=code+commune+"+city+"'>https://www.google.com/search?q=code+commune+"+city+"</a>",
unsafe_allow_html=True)
expander.write('''
(For Paris: enter 751XX, 
with XX the arrondissement)
''')

df = load_data(postcode)

price = st.sidebar.slider("Select a price range",0,1000000,(400000,600000))

since = st.sidebar.date_input("Search from",datetime.datetime.strptime('2021-01-01','%Y-%m-%d'))

# d21 = st.sidebar.checkbox("2021 data",value=True)

df1 = df[(df.valeur_fonciere>price[0]) & (df.valeur_fonciere<price[1]) & (df.date_mutation>since)]

st.sidebar.write(str(len(df1))+" results")

fig, ax = plt.subplots()
ax.hist(df1.prixm2) 

st.sidebar.write(fig)

# Body

st.title("🏠 Immo")

if st.checkbox("Display results list",False):
    # streamlit doesn't render category dtypes
    st.write(df1.astype('object'))

st.markdown("**Data source:** [Demandes de valeurs foncières géolocalisées](https://www.data.gouv.fr/fr/datasets/5cc1b94a634f4165e96436c1/)")

# if st.checkbox("Display map",True):
if st.checkbox("Display results map",True):
    map1 = immo.mapplot(df1)
    folium_static(map1)
#     st.map(df1)
