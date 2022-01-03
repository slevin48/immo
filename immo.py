
def dvf_commune(code_postal):
    # dvf_commune(92048)
    import urllib
    import json    
    try:
        url = "http://api.cquest.org/dvf?code_commune="+str(code_postal)
        response = urllib.request.urlopen(url)
        html = response.read()
        json_data = json.loads(html)
        
    except urllib.error.URLError:
        print("Erreur")
          
    return json_data

def dvf_section(section):
    # dvf_section(92072000AH)
    # Sevres secteur gare rive gauche
    import urllib
    import json    
    try:
        url = "http://api.cquest.org/dvf?section="+section
        response = urllib.request.urlopen(url)
        html = response.read()
        json_data = json.loads(html)
        
    except urllib.error.URLError:
        print("Erreur")
          
    return json_data

def dvf_lat_lon(lat,lon):
    # dvf_lat_lon(48.814960, 2.241272)
    # Meudon gare
    import urllib
    import json    
    try:
        url = "http://api.cquest.org/dvf?lat="+str(lat)+"&lon="+str(lon)
        response = urllib.request.urlopen(url)
        html = response.read()
        json_data = json.loads(html)
        
    except urllib.error.URLError:
        print("Erreur")
          
    return json_data

def parse_dvf(json_data):
    # parse and extract json data 
    nb_res = json_data['nb_resultats']
    res = json_data['resultats']
    # create lists
    date_mutation = []
    valeur_fonciere = []
    type_voie = []
    voie = []
    surface = []
    piece = []
    lat = []
    lon = []
    
    for i in range(nb_res):
        x = res[i]
        if x['type_local'] == "Appartement":
            date_mutation.append(x['date_mutation'])
            valeur_fonciere.append(x['valeur_fonciere'])
            type_voie.append(x['type_voie'])
            voie.append(x['voie'])
            surface.append(x['surface_relle_bati'])
            piece.append(x['nombre_pieces_principales'])
            lat.append(x['lat'])
            lon.append(x['lon'])
           
    return dict(date_mutation=date_mutation,
                valeur_fonciere=valeur_fonciere,type_voie=type_voie,voie=voie,
                surface=surface,piece=piece,
                lat=lat,lon=lon)

def parse_dvf2(json_data):
    import pandas as pd
    dict_data = parse_dvf(json_data)
    df = pd.DataFrame.from_dict(dict_data)
    df = df.dropna(subset=['lat','lon'])
    df['prixm2'] = df.valeur_fonciere/df.surface
    df = df[df.prixm2<10000]
    df.prixm2 = df.prixm2.astype(int)
    df['marker_color'] = pd.cut(df['prixm2'], bins=4,labels=['blue','green', 'yellow', 'red'])
    df = df.sort_values(by='date_mutation',ascending=False)
    return df

def mapplot(df):
    import folium
    from folium import plugins
    map1 = folium.Map(
        location=[df['latitude'].iloc[0], df['longitude'].iloc[0]],
        tiles='cartodbpositron',
        zoom_start=12,
    )
    for index, row in df.iterrows():
        folium.Marker([row['latitude'], row['longitude']], 
        popup=row['type_local']+" "+str(row['date_mutation'])+" "+str(row['adresse_nom_voie'])+" "+str(row['valeur_fonciere'])+" euros / "+str(row['surface_reelle_bati'])+" m2",
        tooltip=str(row['prixm2']),
        icon=plugins.BeautifyIcon(number=index,
                                                border_color=row['marker_color'],
                                                # border_width=1,
                                                text_color='black',
                                                inner_icon_style='margin-top:0px;'
                                                )
        ).add_to(map1)
    return map1

def mapplot2(df):
    import folium
    from folium import plugins
    map1 = folium.Map(
        location=[48.653769,-2.0058249],
        tiles='cartodbpositron',
        zoom_start=14,
    )
    for index, row in df.iterrows():
        folium.Marker([row['lat'], row['lon']], 
        popup=str(row['date_mutation'])+" "+str(row['type_voie'])+" "+str(row['voie'])+" "+str(row['valeur_fonciere'])+" euros / "+str(row['surface'])+" m2",
        tooltip=str(row['prixm2']),
        icon=plugins.BeautifyIcon(number=index,
                                                border_color=row['marker_color'],
                                                # border_width=1,
                                                text_color='black',
                                                inner_icon_style='margin-top:0px;'
                                                )
        ).add_to(map1)
    return map1