import os
import pickle
import streamlit as st
import requests
import gdown

# -----------------------------------------------------
# Download file from Google Drive using gdown
# -----------------------------------------------------

def download_file_from_gdrive_gdown(file_id, destination):
    url = f"https://drive.google.com/uc?id={file_id}"
    if not os.path.exists(destination):
        st.write(f"Downloading {destination} from Google Drive...")
        gdown.download(url, destination, quiet=False)
        st.write(f"Downloaded {destination}.")
    

# -----------------------------------------------------
# Download similarity.pkl from Google Drive
# -----------------------------------------------------

similarity_file_id = "10bpWJrwLrjw83MLm8nY7vrJ2xjge3mdl"
destination_file = "similarity.pkl"

# Clean up any bad previous file
if os.path.exists(destination_file):
    # Check if it accidentally contains HTML
    with open(destination_file, "rb") as f:
        chunk = f.read(10)
        if chunk.startswith(b"<html"):
            st.write("Deleting invalid similarity.pkl (HTML file).")
            os.remove(destination_file)

# Now download the file
download_file_from_gdrive_gdown(similarity_file_id, destination_file)

# -----------------------------------------------------
# Load Pickle Files
# -----------------------------------------------------

# Load movie list
movies = pickle.load(open('movie_list.pkl', 'rb'))

# Load similarity matrix safely
try:
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
except pickle.UnpicklingError:
    st.error("Downloaded similarity.pkl is not a valid pickle file. Check your Google Drive sharing settings.")
    st.stop()

# -----------------------------------------------------
# Fetch Poster Function
# -----------------------------------------------------

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=d6007022c362050c0ee9cb85556847d3&language=en-US"
    response = requests.get(url)
    data = response.json()

    if 'poster_path' in data and data['poster_path']:
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

# -----------------------------------------------------
# Recommendation Logic
# -----------------------------------------------------

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# -----------------------------------------------------
# Streamlit Frontend
# -----------------------------------------------------

st.header('🎬 Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])
    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])
