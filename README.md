**YouTube Data Harvesting and Warehousing using MYSQL and Streamlit**

This is a Streamlit app designed for accessing and analyzing data from diverse YouTube channels. 
Key functionalities include data retrieval (Channel id, video count, etc.) via the Google YouTube Data API, storing in MySQL tables, 
and enabling search and retrieval through SQL queries and provide seamless reporting for end user 

**Problem Statement:**

The problem statement is to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels. 
The application should have the following features:

1)Ability to input a YouTube channel ID and retrieve all the relevant data (Channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using Google API.

2)Option to store the data in a MySQL database .

3)Option to select a channel id and display the details

4)Ability to search and retrieve data from the SQL database using different search options, including joining tables to get channel details

5)Provide the required data as a display to the End User 

**Approach :**

1)Set up a Streamlit app: Streamlit is a great choice for building data visualization and analysis tools quickly and easily. 
You can use Streamlit to create a simple UI where users can enter a YouTube channel ID, view the channel details

2)Connect to the YouTube API: You'll need to use the YouTube API to retrieve channel and video data. 
You can use the Google API client library for Python to make requests to the API. 

3)Store data in a MySQL tables: Once you retrieve the data from the YouTube API, you can store it in a MySQL Database tables. 

4)Query the SQL data warehouse: You can use SQL queries to join the tables in the SQL data warehouse and retrieve data for specific channels based on user input. 
You can use a Python SQL library such as SQLAlchemy to interact with the SQL database.

5)Display data in the Streamlit app: Finally, you can display the retrieved data in the Streamlit app.

**Tools Used:**

1)STREAMLIT

2)PYTHON

3)GOOGLE API CLIENT

4)MY SQL Database

5)PANDAS

6)SQLALCHEMY

**PREREQUISITES:**

1)Get the required Google Client API

2)Create the youtube database,required tables in the MY SQL

You can view a video of this work in below link:  
https://www.linkedin.com/posts/rajalakshmi-venkatachalam-01b00990_youtube-data-harvesting-project-activity-7192418432712151040--owk?utm_source=share&utm_medium=member_desktop
