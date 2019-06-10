#!/usr/bin/env python
# coding: utf-8

# ************** INPUTS START **************

# # <center> PV PLANTS ANALYSIS [TETTOIA FV1] </center>

#  <img src="Dataset e immagini\gfv13ds.PNG">

# In[1]:


Voc_mod=23.63 #V
Isc_mod=8.67 #A
Vmp_mod=18.93 #V
Imp_mod=8.19 #A

#Livello moduli
moduli_stringa=24

#Max power point
Vmp_str=Vmp_mod*moduli_stringa #V
Imp_str=Imp_mod #A

#Max intensity
Voc_str=Voc_mod*moduli_stringa #V
Isc_str=Isc_mod #A

#Livello stringa
n_stringhe_inverter=2

#Max power point
Vmp_to_inv=Vmp_str
Imp_to_inv=Imp_str*n_stringhe_inverter

#Max intensity
Voc_to_inv=Voc_str
Isc_to_inv=Isc_str*n_stringhe_inverter


# * **Degradation di I, V, P con T_mod**
# 
# NB: E' importante verificare le unità di misura dei coefficienti!!!

# In[2]:


y_P=-0.0044 #Degradation potenza con Temperatura moduli
coeff_beta=-0.34/100 #*Vmp_mod/Voc_mod #Coeff di V da verificare quale formula usare
coeff_alfa=0.07/100 #*Imp_mod/Isc_mod #Coeff di I modificato


# Grandezze | Livello stringa | Livello ingresso inverter
# --- | --- | ---
# Vmp | Vmp_str | Vmp_to_inv
# Imp | Imp_str | Imp_to_inv


# ************** INPUTS END **************


# ## LIBRERIE 

# In[3]:


import numpy as np
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
import matplotlib.cm as cm
from ipywidgets import widgets
from IPython.display import display


# * **Importo anche la mia libreria**

# In[4]:


import vb_cluster as vbc 


# ## Calcolo la potenza nominale

# In[5]:


Pnom=np.round(moduli_stringa*n_stringhe_inverter*Vmp_mod*Imp_mod/1000, decimals=3)
Pnom


# ##  Apertura file

# In[6]:


import os
from os import listdir


# * ### Funzione trova dati

# In[7]:


def find_csv_filenames( path_to_dir, suffix=".csv" ):
    #Funzione per trovare i file csv in un certo percorso
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]


# * ### Files disponibili nella cartella di lavoro

# In[8]:


path_to_dir=r"C:\Users\BARONE\AppData\Local\Programs\Python\Python37-32\Scripts\00-AA-Files per articolo\Dataset e immagini"
lista_impianti=find_csv_filenames(path_to_dir, suffix=".csv")
lista_impianti


# * ### Apro e sistemo la struttura del file

# In[9]:


nome_file='Tettoia FV1 All until 07062019.csv'
path_to_file=path_to_dir+r'\\'+nome_file
labels_new=['Date','Pot_ac', 'Pot_dc',
            'V1','I1','V2','I2',
            'Irr',
            'Tair','Tmod']
df=pd.read_csv(path_to_file, skiprows=6, delimiter=';', names=labels_new,)
df.head(5)


# In[10]:


df['day']=df['Date'].apply(lambda date: str(date).split('/')[:1][0])
df['month']=df['Date'].apply(lambda date: str(date).split('/')[1])
df['year']=df['Date'].apply(lambda date: str(date).split('/')[2][0:4])
df['time']=df['Date'].apply(lambda date: str(date).split('/')[2][4:])
df['hours']=df['time'].apply(lambda time: str(time).split(':')[0])
df['minutes']=df['time'].apply(lambda time: str(time).split(':')[1])
#df['seconds']=df['time'].apply(lambda time: str(time).split(':')[2])
df=df.drop(columns=['Date','time'])
df.head()


# * #### FUNZIONE FILTRO DATI NAN
# 
# 
#  * Questa funzione è indispensabile serve a eliminare dal dataframe (**panda_db**) tutte le righe dove è presente almeno un dato non numerico all'interno delle corrispondenti colonne **measures**
# 
#  * **Perchè?** A volte il sistema SCADA comunica male e invece di comunicare valori numerici, rimanda valori di tipo stringa (nel mio caso manda -->'***')

# In[11]:


label_list=df.columns
df=vbc.filter_nan(df, label_list)


# * ### Rimuovo I dati per i quali la temperatura è maggiore di 200°C:

# In[12]:


df=df[df['Tmod']<200]


# In[13]:


df.head(2)


# * #### FUNZIONE FILTRO IRR
# 
# 
#  * Con questa funzione tiro via dal dataframe (**panda_db_filtered**) tutti le righe che presentano, nella colonna con label **irr_string**, un valore di irraggiamento minore di **irr_rif**.
# 
#  * **Perchè?** *Per evitare di tenere in considerazione la notte e le prime/ultime ore del giorno         nel corso dell'analisi.*

# In[14]:


df=vbc.filter_irr(10,df, 'Irr')


# In[15]:


df.describe()


# * **CONVERTO I DATI IN FLOAT64**

# In[16]:


df[label_list]=df[label_list].astype(dtype='float64',errors='raise')


# * **QUALCHE STATISTICA IN PIU' RIGUARDO I DATI:**

# In[17]:


sns.set(style="white", palette="muted", color_codes=True)
f, axes = plt.subplots(2, 2, figsize=(20, 20), sharex=False)
sns.distplot(df['Tmod'], color="r", bins=50, ax=axes[0][0])
sns.distplot(df['Irr'], color="k", bins=50, ax=axes[0][1])
sns.distplot(df['V1'], color="b", bins=50, ax=axes[1][0])
sns.distplot(df['I1'], color="y", bins=50, ax=axes[1][1])


# * **CALCOLO IL PR CREANDO UNA NUOVA COLONNA**

# In[18]:


#df['Pot_dc']=df['V1']*df['I1']/1000
df['PR_score']=df['Pot_dc']/Pnom/df['Irr']*1000


# ------

# ##  OSSERVO I DATI

# In[19]:


measures=list(df.columns)
list(df.columns)


# * **Rimuovo i valori con PR>0.99**

# In[20]:


df=df[df['PR_score']<0.99]


# In[21]:


df.describe()


# In[22]:


df.head(2)


# * #### Inizializzo l'elenco delle figure

# In[23]:


nfig=0


# # Analisi grafica
# 
# * Questo grafico mostra due andamenti della potenza, sintomo di un guasto, probabilmente ad un inverter

# In[24]:


nfig+=1
graph_font_size=18
fig, (ax1, ax2, ax3) =plt.subplots(3,1,figsize=(18,35))
shrink_option=1.5
position_option=(0,1.15)

#Primo grafico
PR_id=1
xx=df['Irr']
yy=df['Pot_dc']
yy2=xx*PR_id*Pnom/1000
mappable_graph=ax1.scatter(xx,yy, s=20, c=df['Tmod'], cmap='plasma', edgecolor='k')
Pdc_id=ax1.scatter(xx,yy2, s=20, c='b')

#Per la colorbar:
ax1_colbar=fig.add_axes([-0.05, 0.7, 0.1, 0.1], visible=False)
temp_colorbar=fig.colorbar(mappable_graph, shrink=shrink_option, pad=-0.5)
temp_colorbar.set_label("Module \n Temp. [°C]", fontsize=18, rotation=0, position=position_option,
                        ha='right',bbox=dict(boxstyle='square', fc='w'))

ax1.set_xlabel('Irr [W/m2]',  fontsize=graph_font_size)
ax1.set_ylabel('DC Power [W]',  fontsize=graph_font_size)
ax1.grid()

#Secondo grafico
xx=df.index
yy=df['Pot_dc']

mappable_graph2=ax2.scatter(xx,yy, s=20, c=df['Tmod'], cmap='plasma')#, edgecolor='k')

ax2_colbar=fig.add_axes([-0.05, 0.45, 0.1, 0.1], visible=False)
temp_colorbar2=fig.colorbar(mappable_graph2, shrink=shrink_option, pad=0.05)
temp_colorbar2.set_label("Module \n Temp. [°C]", fontsize=18, rotation=0, position=position_option,
                        ha='right',bbox=dict(boxstyle='square', fc='w'))
ax2.set_xlabel('Time',  fontsize=graph_font_size)
ax2.set_ylabel('DC Power [W]',  fontsize=graph_font_size)
ax2.grid()

#Terzo grafico
xx=df['V1']
yy=df['I1']
mappable_graph=ax3.scatter(xx,yy, s=20, c=df['Irr'], cmap='plasma', edgecolor='k')
ax3_colbar=fig.add_axes([-0.05, 0.2, 0.1, 0.1], visible=False)
temp_colorbar2=fig.colorbar(mappable_graph2, shrink=shrink_option, pad=0.05)
temp_colorbar2.set_label("Module \n Temp. [°C]", fontsize=18, rotation=0, position=position_option,
                        ha='right',bbox=dict(boxstyle='square', fc='w'))
ax3.set_xlabel('Voltage [V]',  fontsize=graph_font_size)
ax3.set_ylabel('Current [A]',  fontsize=graph_font_size)
ax3.grid()


# # Analisi giorno
# 

# In[25]:


def day_analysis(day, month,year):

    
    graph_font_size=18
    fig, (ax1, ax2) =plt.subplots(2,1,figsize=(15,14),)
    shrink_option=5
    label_position_option=(0,1.2)
    ax1.grid()
    ax2.grid()
    
    # Ridimensiono il database
    day_df=df[df['year']==year]
    day_df=day_df[day_df['month']==month]
    day_df=day_df[day_df['day']==day]
    
    # Labels 
    # Primo grafico
    ax1.set_xlabel('Irr [W/m2]',  fontsize=graph_font_size )
    ax1.set_ylabel('Pdc [kW]',  fontsize=graph_font_size)
    daily_Irr=np.round(np.sum(10/60/60/1000*day_df['Irr']),2)
    daily_power=np.round(np.sum(10/60/60*day_df['Pot_dc']),2)
    daily_PR=np.round(daily_power/daily_Irr/Pnom,2)
    title0='Month '+str(int(month))+', Day '+str(int(day))
    title=title0+'\nGlobal Irr. :'+str(daily_Irr)+' kWh/m2  - '
    title=title+'Energy produced:'+str(daily_power)+' kWh  - '
    title=title+'PR:  '+str(daily_PR)
    ax1.set_title(title,  fontsize=graph_font_size,loc='center')
    
    # Secodo grafico
    ax2_irr=ax2.twinx()
    ax2_irr.set_ylabel('Irr [W/m2]]',  fontsize=graph_font_size )
    ax2.set_xlabel('Time [15mins]',  fontsize=graph_font_size )
    ax2.set_ylabel('Pdc [kW]',  fontsize=graph_font_size)
    try:
        start=str(int(day_df['hours'].iloc[0]))+':'+str(int(day_df['minutes'].iloc[0]))#+':'+str(int(day_df['seconds'].iloc[0]))
        end=str(int(day_df['hours'].iloc[-1]))+':'+str(int(day_df['minutes'].iloc[-1]))#+':'+str(int(day_df['seconds'].iloc[-1]))
        time_info='From '+start+' to '+ end
        ax2.set_title(time_info,  fontsize=graph_font_size,loc='left')
    except IndexError :
        ax2.set_title('No data',  fontsize=graph_font_size,loc='left')

    # Primo grafico
    xx=day_df['Irr']
    yy=day_df['Pot_dc']
    mappable_graph=ax1.scatter(xx,yy, s=20, c=day_df['Tmod'], cmap='plasma', edgecolor='k')
    ax1_PR=ax1.twinx()
    ax1_PR.scatter(xx,yy/Pnom*1000/xx, s=20, c='g')
    
    
     # Per la colorbar:
    ax1_colbar=fig.add_axes([-0.07, 0.5, 0.1, 0.1], visible=False)
    temp_colorbar=fig.colorbar(mappable_graph, shrink=shrink_option, pad=-0.5)
    temp_colorbar.set_label("Module \n Temp. [°C]", fontsize=18, rotation=0, position=label_position_option,
                            ha='right',bbox=dict(boxstyle='square', fc='w'))
    
    # Secondo grafico
    xx=day_df.index
    yy=day_df['Pot_dc']
    mappable_graph=ax2.scatter(xx,yy, s=20, c=day_df['Tmod'], cmap='plasma')#, edgecolor='k')
    ax2_irr.scatter(xx,day_df['Irr'], s=5, c='k')#, edgecolor='k')
    
time_span1=widgets.interact(day_analysis,
                            day=widgets.FloatSlider( value = 1, min = 1, max = 31, step = 1),
                            month=widgets.FloatSlider( value = 6, min = 1, max = 12, step = 1),
                            year=widgets.FloatSlider( value = 2019, min = 2016, max = 2019, step = 1),
                           )


# In[ ]:


# # Preparazione dati

# * **Imposto il nuovo database:**

# In[27]:


IV_set=df.copy()
IV_set.head(5)


# In[28]:


IV_set.describe()


# # Adesso scrivo su file csv così da avere un database da pescare facilmente!

# In[41]:


id_code='Tettoia FV1 '+str(date.today())+".csv"
path_to_dir=r"C:\Users\BARONE\AppData\Local\Programs\Python\Python37-32\Scripts\00-AA-Files per articolo\Dataset e immagini\dataset_"+id_code


# In[42]:


crea_file='no'


# In[43]:


if crea_file=='si':
    IV_set.to_csv(
        path_or_buf=path_to_dir,
        sep=';',
        na_rep='nan',
        float_format=None,
        columns=None,
        header=True,
        index=True,
        index_label=None,
        mode='w',
        encoding=None,
        chunksize=None,
        decimal='.'
             )
    print('File creato!!!!')
else:
    print('\n\nHai scelto di non creare alcun file!\n\n')


# In[ ]:
