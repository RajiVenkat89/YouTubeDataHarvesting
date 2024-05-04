import mysql.connector
import googleapiclient.discovery
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

##Provides connection to the Mysql Database
conn=create_engine('mysql+mysqlconnector://root:root@localhost:3306/youtube')

##Initialisation of variables that is required for the data fetch from the API . Providing the API Key is the 
##pre-requisite for this program
api_key="AIzaSyAvJUQiRyig8aC9YCjtH0yEpjiFACJFFM4"
api_service_name = "youtube"
api_version = "v3"
youtube = googleapiclient.discovery.build(api_service_name,api_version,developerKey=api_key) 

st.set_page_config(layout="wide")
st.header(':blue[YOUTUBE DATA HARVESTING]')
Menu = st.selectbox(
   "Please select the Menu from below",
   ("Data Insertion","Data Deletion", "Report Generation")
   )
if(Menu == 'Data Insertion'): 
    c_id=st.text_input("Enter Channel_id:")
    submit_button= st.button("Insert Data")
    ##Function to get the Channel data from the API. This uses the C_ID(Channel ID) as parameter which is passed on as an user 
    ##input from the streamlit screen . It has two parameters , One is the Channel id and other one is to return
    ##either all the columns from the channel id or return only the playlist id which will be used for 
    ##merging with the video data
    def get_channel_data(c_id,resp):	  
        request = youtube.channels().list(
        part="snippet,contentDetails,statistics,status",
        id=c_id
        )
        response = request.execute()
        if resp=='all':
            c_data=[]											#defining a empty list to store channel data
            data=dict(channel_id=c_id,	
            channel_name=response['items'][0]['snippet']['title'],
            channel_desc=response['items'][0]['snippet']['description'],
            channel_pdate=response['items'][0]['snippet']['publishedAt'],
            channel_plists=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
            channel_viewcount=response['items'][0]['statistics']['viewCount'],
            channel_videocount=response['items'][0]['statistics']['videoCount'],
            channel_subcount=response['items'][0]['statistics']['subscriberCount'],
            channel_status=response['items'][0]['status']['privacyStatus'])				#fetching the channel data as dictionary and storing in the list
            c_data.append(data)
            return c_data
        else:
            channel_plists=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            return channel_plists

    ##Function to get the get the playlist data from the API by passing the channel id as the parameter
    def get_playlist_data(c_id):						
        playlist_data=[]
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=c_id,
            maxResults=50)
        response = request.execute()
        for item in range(len(response['items'])):						##For loop to iterate number of playlist
            p_data=dict(channel_id=c_id,playlist_id=response['items'][item]['id'],
                        playlist_name=response['items'][item]['snippet']['title'])		##fetching the playlist data as dictionary and storing in the list
            playlist_data.append(p_data)
        return playlist_data

    ##Function to get video ids with playlist id
    def get_video_ids(p_id):						
        video_ids=[]							##defining a empty list to video ids
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=p_id,
            maxResults=50)
        response = request.execute()
        for item in range(len(response['items'])):					##For loop to iterate number of video ids in first page
            v_id=response['items'][item]['contentDetails']['videoId']	##Fetching the video id as dictionary and storing in the list
            video_ids.append(v_id)
        next_page_count=response.get('nextPageToken')				##Get next page token from YouTube API
        next_page=True
        while next_page:								##Traverse through multiple pages using while loop and get the video id till next page count becomes null
            if next_page_count is None:
                next_page=False
            else:
                request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=p_id,
                pageToken=next_page_count,
                maxResults=50)
                response = request.execute()
                for item in range(len(response['items'])):
                    v_id=response['items'][item]['contentDetails']['videoId']
                    video_ids.append(v_id)
                next_page_count=response.get('nextPageToken')
        return video_ids

    ##Function to convert the durtion of the video in seconds. This takes the Duration string as a parameter and 
    ##converts it to seconds and retuns the seconds data which will be used for further processes of inserting to the database
    def duration_to_seconds(duration_string):
        # Remove the "PT" prefix
        duration_string = duration_string[2:]

        # Initialize variables for hours, minutes, and seconds
        hours = 0
        minutes = 0
        seconds = 0

        # Check if "H" (hours) is present
        if "H" in duration_string:
            hours_str = duration_string.split("H")[0]
            hours = int(hours_str)
            duration_string = duration_string.split("H")[1]

        # Check if "M" (minutes) is present
        if "M" in duration_string:
            minutes_str = duration_string.split("M")[0]
            minutes = int(minutes_str)
            duration_string = duration_string.split("M")[1]

        # Check if "S" (seconds) is present
        if "S" in duration_string:
            seconds_str = duration_string.split("S")[0]
            seconds = int(seconds_str)

        # If duration is "Not available", set total seconds to 0
        if duration_string.lower() == "not available":
            return 0

        # Calculate total seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds

    ## This functions is used to get all the details of a video by using the playlist id and Video id . The playlist id
    ## is passed to link the playlist to the video and also the duration of video is converted to seconds and this
    ##returns the total video data for a particular playlist id to insert into the database.
    def get_video_data(p_id,v_ids):						
        video_data=[]							##defining a empty list to store video data
        for video_id in v_ids:
            request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id)
            response = request.execute()
            video_dur=response['items'][0].get('contentDetails',{}).get('duration','Not Available')
            data=dict(video_id=response['items'][0]['id'],
            channel_plists=p_id,
            channel_id=response['items'][0]['snippet']['channelId'],
            video_name=response['items'][0]['snippet']['title'],
            video_desc=response['items'][0]['snippet']['description'],
            video_pdate=response['items'][0]['snippet']['publishedAt'],
            video_thumbnail=response['items'][0]['snippet']['thumbnails']['default']['url'],
            video_duration=response['items'][0].get('contentDetails',{}).get('duration','Not Available'),
            video_dur_inseconds=duration_to_seconds(video_dur),
            video_captionsts=response['items'][0]['contentDetails']['caption'],
            video_viewcount=response['items'][0]['statistics'].get('viewCount',0),
            video_likecount=response['items'][0]['statistics'].get('likeCount',0),
            video_commentcount=response['items'][0]['statistics'].get('commentCount',0),
            video_dislikecount=response['items'][0]['statistics'].get('dislikeCount',0))
            video_data.append(data)
        return video_data

    ##Function to get video comments with video_ids list and restricting to max of 2
    def get_video_comments(v_ids):							
        comment_data=[]								##defining a empty list to store video comments
        for video_id in v_ids:
            try:									## validation to check if comments available or not
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=2)
                response = request.execute()
            except:
                response='None'
            if response is not 'None':
                resp=response['items']
                if not resp:				## Empty list will be passed in case of no comments    
                    return comment_data
                else:
                    for i in range(len(response['items'])):
                        data=dict(video_id=video_id,
                        comment_id=response['items'][i]['id'],
                        comment_text=response['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'],
                        comment_author=response['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        comment_pdate=response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt']
                        )
                        comment_data.append(data)
        return comment_data

    ##The below piece of code is the main program which establises the connection with the MySQL database . 
    ##It has the validation to check if the Channelid provided by the user is already present in the database or not
    ## If the channel_id is present it will only display the details of the channel . If not it will insert the 
    ##the data of channel,playlist,video and comments into the database . 
    ## these details will be used by the streamlit application for the final report to be created for the user 
    #if st.session_state.Get_state==True:
    if submit_button==True:
        client=mysql.connector.connect(host='127.0.0.1',user='root',password='root',database='youtube')
        cursor=client.cursor()
        query="select count(*) from channel_details where channel_id=%s"
        cursor.execute(query,(c_id,))
        count_channel=cursor.fetchall()
        cursor.close()
        client.close()
        if len(c_id)>0:
            if  count_channel[0][0]==0:
                try:
                    channel_data=get_channel_data(c_id,"all")                 ##call get_channel_data with channel id and store in a variable
                    channel_details=(pd.DataFrame(channel_data)) 		##convert channel data to dataframe using pandas and store in a variable	
                    playlist_data = get_playlist_data(c_id)
                    playlist_details=(pd.DataFrame(playlist_data))
                    channel_plst=get_channel_data(c_id,"plst")
                    video_id=get_video_ids(channel_plst)		##Call get_video_ids function with playlist id and store in a variable
                    video_Data= get_video_data(channel_plst,video_id)				##Call get_video_data function with Channle Playlist_id and video ids list
                    video_details=pd.DataFrame(video_Data)						##convert video_Data to dataframe and store in a variable
                    video_Comment=get_video_comments(video_id)				##call get_video_comments with video_ids list
                    video_comments=pd.DataFrame(video_Comment)					##convert video_Comment to dataframe and store in a variable
                    channel_details.to_sql("channel_details",conn,if_exists='append',index=False)  ##Insert data into Channel_details Table
                    playlist_details.to_sql("playlist_details",conn,if_exists='append',index=False) ##Insert data into Playlist_details Table
                    video_details.to_sql("video_details",conn,if_exists='append',index=False) ##Insert data into Video_details Table
                    video_comments.to_sql("comment_details",conn,if_exists='append',index=False) ##Insert data into Comment_details Table
                    st.write(f"Data insertion into the MySQL database successful for the Channel ID {c_id}")
                except Exception as e:
                    st.write(e)
                    #st.write(':red[Please Enter Valid Channel ID!!!]')
            else:
                client=mysql.connector.connect(host='127.0.0.1',user='root',password='root',database='youtube')
                cursor=client.cursor()
                query="select channel_id,channel_name,channel_pdate,channel_viewcount,channel_videocount,channel_subcount from channel_details where channel_id=%s"
                cursor.execute(query,(c_id,))
                channel_data_fetch=cursor.fetchall()
                cursor.close()
                client.close()
                st.write(':green[Channel details already exists!!!]')
                channel_data_disp=pd.DataFrame(channel_data_fetch,columns=["Channel ID","Channel Name","Channel Published Date","Channel View Count","Channel Video Count","Channel Subscriber Count"])
                channel_data_disp.index.name="S.No"
                channel_data_disp.index+=1
                st.write(channel_data_disp)
        submit_button=False
elif(Menu == 'Data Deletion'):
    c_id_d=st.text_input("Enter Channel_id:")
    delete_button=st.button("Delete Data")
    if delete_button==True:
        client=mysql.connector.connect(host='127.0.0.1',user='root',password='root',database='youtube')
        cursor=client.cursor()
        query="select count(*) from channel_details where channel_id=%s"
        cursor.execute(query,(c_id_d,))
        count_channel=cursor.fetchall()
        cursor.close()
        client.close()
        if  len(c_id_d)>0:
            if  count_channel[0][0]==0:
                st.write(':red[Channel does not exists]')
            else:
                try:
                    client1=mysql.connector.connect(host='127.0.0.1',user='root',password='root',database='youtube')
                    cursor1=client1.cursor()
                    query="delete from comment_details where video_id in (select video_id from video_details where channel_id=%s)"
                    cursor1.execute(query,(c_id_d,))
                    client1.commit()
                    #channel_data_fetch=cursor.fetchall()
                    query="delete from video_details where channel_id=%s"
                    cursor1.execute(query,(c_id_d,))
                    client1.commit()
                    #channel_data_fetch=cursor.fetchall()
                    query="delete from playlist_details where channel_id=%s"
                    cursor1.execute(query,(c_id_d,))
                    client1.commit()
                    #channel_data_fetch=cursor.fetchall()
                    query="delete from channel_details where channel_id=%s"
                    cursor1.execute(query,(c_id_d,))
                    client1.commit()
                    #channel_data_fetch=cursor.fetchall()
                    cursor1.close()
                    client1.close()
                    st.write(':green[Data deleted successfully]')
                except Exception as e:
                    st.write(e)
        delete_button=False
## Incase of Report Generation, gets the Questions as input and displays the Output accordingly
else:       
    client=mysql.connector.connect(host='127.0.0.1',user='root',password='root',database='youtube')
    cursor=client.cursor()
    Report_1="Report 1: Names of all the Videos and its corresponding Channel Name"
    Report_2="Report 2: Channel with Maximum Videos"
    Report_3="Report 3: Top 10 Most Viewed Videos"
    Report_4="Report 4: Comment Count on Each Video"
    Report_5="Report 5: Video with Highest Likes and its corresponding Channel Name"
    Report_6="Report 6: Videos with its Like and Dislike Count"
    Report_7="Report 7: Channel Name with its View Count"
    Report_8="Report 8: Channels with Video Published in 2022"
    Report_9="Report 9: Channels with Average Duration of all its Videos"
    Report_10="Report 10: Video with Highest Comments and its corresponding Channel Name"

    option = st.selectbox(
       "Select Report to be Generated",
        (Report_1,Report_2, Report_3,Report_4,Report_5,Report_6,Report_7,Report_8,Report_9,Report_10),
        index=None,
        placeholder="--Select--",
        )
    if(option==Report_1):
        ##1.	What are the names of all the videos and their corresponding channels?
        cursor.execute("""select video_name,channel_name from video_details as vdo inner join 
                       channel_details chn on vdo.channel_id=chn.channel_id order by channel_name,video_name""")
        Output1=cursor.fetchall()
        Report1=pd.DataFrame(Output1,columns=["Video Name","Channel Name"]).reset_index(drop=True)
        Report1.index.name="S.No"
        Report1.index+=1
        st.write(Report1)
    elif(option==Report_2):
        ##2. 	Which channels have the most number of videos, and how many videos do they have?
        cursor.execute("""select channel_name,channel_videocount as video_count from channel_details chn 
                       order by video_count desc LIMIT 1""")
        Output2=cursor.fetchall()
        Report2=pd.DataFrame(Output2,columns=["Channel Name","Video Count"]).reset_index(drop=True)
        Report2.index.name="S.No"
        Report2.index+=1
        st.write(Report2)
    elif(option==Report_3):  
        ##	3.	What are the top 10 most viewed videos and their respective channels?
        cursor.execute("""select video_name,Channel_name from video_details as vdo inner join 
                       channel_details chn on vdo.channel_id=chn.channel_id order by video_viewcount  desc LIMIT 10""")
        Output3=cursor.fetchall()
        Report3=pd.DataFrame(Output3,columns=["Video Name","Channel Name"]).reset_index(drop=True)
        Report3.index.name="S.No"
        Report3.index+=1
        st.write(Report3)
    elif(option==Report_4): 
        ##	4.	How many comments were made on each video, and what are their Corresponding video names?
        cursor.execute("""select video_name,video_commentcount from video_details order by video_name""")
        Output4=cursor.fetchall()
        Report4=pd.DataFrame(Output4,columns=["Video Name","Comment Count"]).reset_index(drop=True)
        Report4.index.name="S.No"
        Report4.index+=1
        st.write(Report4)
    elif(option==Report_5): 
        ##	5.	Which videos have the highest number of likes, and what are their corresponding channel names?
        cursor.execute("""select channel_name,video_name,video_likecount from  video_details as vdo inner join
                       channel_details as chn on vdo.channel_id=chn.channel_id order by video_likecount desc limit 1""")
        Output5=cursor.fetchall()
        Report5=pd.DataFrame(Output5,columns=["Channel Name","Video Name","Like Count"]).reset_index(drop=True)
        Report5.index.name="S.No"
        Report5.index+=1
        st.write(Report5)
    elif(option==Report_6):
        #6.	What is the total number of likes and dislikes for each video, and what are their corresponding video names?
        cursor.execute("""select video_name,video_likecount,video_dislikecount from  video_details order by video_name""")
        Output6=cursor.fetchall()
        Report6=pd.DataFrame(Output6,columns=["Video Name","Like Count","Dislike Count"]).reset_index(drop=True)
        Report6.index.name="S.No"
        Report6.index+=1
        st.write(Report6)  
    elif(option==Report_7):
        #7.	What is the total number of views for each channel, and what are their corresponding channel names?
        cursor.execute("""select channel_name,channel_viewcount from channel_details order by channel_name""")
        Output7=cursor.fetchall()
        Report7=pd.DataFrame(Output7,columns=["Channel Name","Channel View Count"]).reset_index(drop=True)
        Report7.index.name="S.No"
        Report7.index+=1
        st.write(Report7)
    elif(option==Report_8):
        ##8.	What are the names of all the channels that have published videos in the year 2022?
        cursor.execute("""select channel_name,video_name,video_pdate from  video_details as vdo inner join 
                       channel_details as chn on vdo.channel_id=chn.channel_id where EXTRACT(YEAR from video_pdate)=2022 order by channel_name""")
        Output8=cursor.fetchall()
        Report8=pd.DataFrame(Output8,columns=["channel Name","Video Name","Video Published Date"]).reset_index(drop=True)
        Report8.index.name="S.No"
        Report8.index+=1
        st.write(Report8)
    elif(option==Report_9):
        #9.	What is the average duration of all videos in each channel, and what are their corresponding channel names?
        cursor.execute("""select channel_name,AVG(video_dur_inseconds) from video_details as vdo inner join 
                       channel_details as chn on vdo.channel_id=chn.channel_id group by channel_name order by channel_name""")
        Output9=cursor.fetchall()
        Report9=pd.DataFrame(Output9,columns=["channel Name","Average Duration"]).reset_index(drop=True)
        Report9.index.name="S.No"
        Report9.index+=1
        st.write(Report9)
    elif(option==Report_10):
        #10.	Which videos have the highest number of comments, and what are their corresponding channel names?
        cursor.execute("""select channel_name,video_name,video_commentcount from video_details as vdo 
                       inner join channel_details as chn on vdo.channel_id=chn.channel_id order by video_commentcount DESC limit 1""")
        Output10=cursor.fetchall()
        Report10=pd.DataFrame(Output10,columns=["channel Name","Video Name","Comment Count"]).reset_index(drop=True)
        Report10.index.name="S.No"
        Report10.index+=1
        st.write(Report10)
    else:
            st.write("Please select the report to be generated")
    cursor.close()
    client.close()