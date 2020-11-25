import logging
from urllib.parse import urlparse
import json
import pandas as pd
from pyyoutube import Api
import progressbar
import time
from datetime import datetime
import isodate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(channel_id):

  logger.info('Extraigo la info del canal')
  def playlist_ids(channel_id):
  list_playlist_id = []
  page_token = None
  while 1:
      playlists_id = api.get_playlists(channel_id = channel_id , limit=50, page_token=page_token).to_dict()
      
      for i in range(len(playlists_id.get('items').head(3))):
          playlist_id = playlists_id.get('items')[i].get('id')
          playlist_title = playlists_id.get('items')[i].get('snippet').get('title')

          list_playlist_id.append({'playlist_id':playlist_id,
                                  'playlist_title':playlist_title})
      
      page_token = playlists_id.get('nextPageToken')
      if playlists_id.get('nextPageToken')== None:
          break
    
  df_list_playlist_id = pd.DataFrame(list_playlist_id)
  df_list_playlist_id = df_list_playlist_id[['playlist_title' , 'playlist_id']]

  return df_list_playlist_id
    
  logger.info('extraigo la info de las playlist')
  def playlist_item(df_list_playlist_id):
  list_playlist_item = []
  ###CON EL PLAYLIST_ID HAGO EL GET_PLAYLIST_ITEMS Y EXTRAIGO TODOS LOS VIDEOS_ID (Y MAS INFO)
  for pl in progressbar.progressbar(range(len(df_list_playlist_id))):
      play_list_id = df_list_playlist_id.loc[pl,'playlist_id']
      edicion = df_list_playlist_id.loc[pl,'playlist_title']
      page_token = None
      
      while 1:
          playlist_item = api.get_playlist_items(playlist_id=play_list_id,limit=50, page_token=page_token).to_dict()
          for y in range(len(playlist_item.get('items').head(3))):
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

    return df_list_playlist_item


  
  logger.info('extraigo la info de las playlist')
  def video_info(df_list_playlist_item):
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

    return df_info
    
if __name__ == '__main__':


    df = main(channel_id)
