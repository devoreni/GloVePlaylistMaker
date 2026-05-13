import sqlite3
from src import config
from pathlib import Path
from pprint import pprint
import pickle

def generate_playlist(conn: sqlite3.Connection, song_id: int, similarity_score: int) -> list[tuple[tuple, float]]:
    cur = conn.cursor()
    starting_song = cur.execute("""
        select * from tracks where id = ?
    """, (song_id,)).fetchone()

    if not starting_song:
        raise ValueError('invalid song id')

    starting_mixture = pickle.loads(starting_song[4])
    baseline_score = max(starting_mixture.score_samples(starting_mixture.means_))

    all_songs = cur.execute(
        """select * from tracks where id != ?""", (song_id,)
    ).fetchall()
    playlist = []
    not_in_playlist = []
    for song in all_songs:
        current_mixture = pickle.loads(song[4])
        sm_to_cm = sum(sorted(starting_mixture.score_samples(current_mixture.means_), reverse=True)[:3]) / 3
        cm_to_sm = sum(sorted(current_mixture.score_samples(starting_mixture.means_), reverse=True)[:3]) / 3
        current_score = (sm_to_cm + cm_to_sm) / 2 - baseline_score

        if current_score > similarity_score:
            playlist.append(((song[0], song[1], song[2], song[3], song[5]), float(current_score)))
        else:
            not_in_playlist.append(((song[0], song[1], song[2], song[3], song[5]), float(current_score)))


    return playlist, not_in_playlist






if __name__ == '__main__':
    conn = sqlite3.connect(Path(__file__).parent.parent / 'sen.db')
    playlist, not_in_playlist = generate_playlist(conn, 1, -150)
    pprint(playlist)
    print()
    pprint(not_in_playlist)