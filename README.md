Spotify Album Art Plotter
===========================

## Requirements

This project was ran and tested with Python version 3.7.2.
It depends on two packages (spotipy, matplotlib) that can be installed with
Python's `pip` package manager through the `requirements.txt` file as follows:

    pip install -r requirements.txt

## Usage

Currently, the project requires a bit of manual intervention to properly use.
Firstly, the `saved_tracks.py` file that generates the JSON file of all saved songs
only polls the users saved tracks in their library for songs. It does not interact
with playlists or other methods of saving songs, so if most of your songs are stored
in playlists this will not work well.

