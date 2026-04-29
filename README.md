# GloVePlaylistMaker
Uses Global Vector embeddings to obtain vector representations of  songs which can then be used to make playlists of similar sounding songs


```
git clone <repo>
cd my-project
uv sync           # installs dependencies from uv.lock
uv pip install -e .   # registers the src package in the environment
uv run python src/main.py   # works from any directory
```