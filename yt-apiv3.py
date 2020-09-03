#CARGO LAS LIBRERIAS QUE VOY A NECESITAR 
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from apiclient.discovery import build
import json
import pandas as pd
from pyyoutube import Api
import progressbar
import time
from datetime import datetime
import isodate


#NLP
import nltk
from nltk import word_tokenize, FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#CARGO EL SERVICE_NAME, EL API_VERSION Y EL DEVELOPER_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
DEVELOPER_KEY = 'AIzaSyBwcT0V1mBngVwVxl4F-Gr8it3ltwYLc6M' ###INGRESA DEVELOPER_KEY
api = Api(api_key=DEVELOPER_KEY)


def imprimir():
channel_name = 'TEDxRiodelaPlata' ###INGRESAR EL NOMBRE DEL CANAL
channel_id = api.get_channel_info(channel_name=channel_name).to_dict().get('items')[0].get('id')###EXTRAIGO EL CHANNEL_ID

###CON EL PLAYLIST_ID HAGO EL GET_PLAYLIST_ITEMS Y EXTRAIGO TODOS LOS VIDEOS_ID (Y MAS INFO)
list_playlist_item = []
for pl in progressbar.progressbar(range(len(df_list_playlist_id))):
    play_list_id = df_list_playlist_id.loc[pl,'playlist_id']
    edicion = df_list_playlist_id.loc[pl,'playlist_title']
    page_token = None
    
    while 1:
        playlist_item = api.get_playlist_items(playlist_id=play_list_id,limit=50, page_token=page_token).to_dict()
        for y in range(len(playlist_item.get('items'))):
            if playlist_item.get('items')[y].get('status').get('privacyStatus') != 'private':

                title = playlist_item.get('items')[y].get('snippet').get('title')
                description = playlist_item.get('items')[y].get('snippet').get('description')
                videoId = playlist_item.get('items')[y].get('snippet').get('resourceId').get('videoId') 
                fecha_publicación = datetime.strptime(playlist_item.get('items')[y].get('contentDetails').get('videoPublishedAt'),'%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')

                if 'TEDx' or ' TEDX' in title:
                    list_playlist_item.append({'Titulo':title,
                                               'Fecha_publicacion':fecha_publicación,
                                               'Descripcion':description,
                                               'videoId':videoId,
                                              'Edición':edicion})

        page_token = playlist_item.get('nextPageToken')
        if playlist_item.get('nextPageToken')== None:
            break
df_list_playlist_item = pd.DataFrame(list_playlist_item)
df_list_playlist_item = df_list_playlist_item[['Titulo','Fecha_publicacion','Descripcion','videoId','Edición']]
df_list_playlist_item = df_list_playlist_item[df_list_playlist_item['Titulo']!='Private video'].reset_index(drop=True)

###CON EL VIDEO_ID HAGO EL GET_VIDEO_BY_ID Y EXTRAIGO TODA LA INFO QUE NECESITO DEL VIDEO
### Eliminar los registros que no contengan la palabra TEDxRíodelaPlata ya que no son relevantes

list_info = []
for v in progressbar.progressbar(range(len(df_list_playlist_item))):
    videoID = df_list_playlist_item.loc[v,'videoId']
    edicion = df_list_playlist_item.loc[v,'Edición']
    
    titulo = df_list_playlist_item.loc[v,'Titulo']
    descripcion = df_list_playlist_item.loc[v,'Descripcion']
    
    video_info = api.get_video_by_id(video_id=videoID).to_dict()
    
    fecha = df_list_playlist_item.loc[v,'Fecha_publicacion']
    duracion = video_info.get('items')[0].get('contentDetails').get('duration')
    tags = video_info.get('items')[0].get('snippet').get('tags')
    viewCount = video_info.get('items')[0].get('statistics').get('viewCount')
    likeCount = video_info.get('items')[0].get('statistics').get('likeCount')
    dislikeCount = video_info.get('items')[0].get('statistics').get('dislikeCount')
    commentCount = video_info.get('items')[0].get('statistics').get('commentCount')
     
    list_info.append({'Fecha_Publicación':fecha, 
                    'Titulo':titulo,
                    'Descripcion':descripcion,
                    'Duración_segs':int(isodate.parse_duration(duracion).total_seconds()),
                     'Tags':tags,
                     'viewCount':int(viewCount) if viewCount != None else int(0),
                     'likeCount':int(likeCount) if likeCount != None else int(0),
                     'dislikeCount':int(dislikeCount) if dislikeCount != None else int(0),
                     'commentCount':int(commentCount) if commentCount != None else int(0),
                      'videoID':videoID,
                      'Edicion':edicion
                    })
    time.sleep(0.5)
df_info = pd.DataFrame(list_info)
df_info = df_info[['Fecha_Publicación','Titulo','viewCount','likeCount', 'dislikeCount',
                   'commentCount','Duración_segs','Tags','Descripcion','videoID', 'Edicion']]
df_info = df_info.drop_duplicates(subset=['Titulo'],keep='first').reset_index(drop=True)
df_info.to_csv(str(channel_name)+'.csv')