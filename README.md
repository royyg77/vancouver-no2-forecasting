# Urban Mobility and Air Quality Forecasting (Group 7)

Shared code and notebooks for the COMP 9170 group project.

## Setup

1. Clone the repo and open a terminal in it.
2. Make a virtual environment with Python 3.12 and activate it:
   ```
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```
   On Windows, use `py -3.12 -m venv .venv` and then `.venv\Scripts\activate`.
3. Run `pip install -r requirements.txt`. For the graph model, use `requirements-gnn.txt` instead.
4. Get the cleaned grid. How it will be shared is still being settled.
5. Run `python build.py`. It isn't built yet.

## Commands

| Command | What it does | Needs |
|---|---|---|
| `python clean_data.py` | raw files -> cleaned hourly grid | the raw files |
| `python build.py` | cleaned grid -> all tables | the cleaned grid |

Neither is built yet.

## Column contract

These are the column names every model table will use.

**Fixed columns:** `station`, `origin_utc`, `target_utc`, `h`, `day_band`, `split`, `y`, `persistence`, `climatology`, `scored`

`h` is a key and also a model input.

**Feature columns** start with one of these prefixes:

| Prefix | Features |
|---|---|
| `own_` | the station's own NO2 |
| `wx_` | weather |
| `cal_` | calendar |
| `nb_` | neighbouring stations |
| `tr_` | traffic, if it arrives |

Select features by prefix, not by listing names.

## Working together

- `main` always works. Make a branch, then open a pull request.
- One branch edits a notebook at a time. To experiment, copy it under a new name.
- Changes to `pipeline/` need a pull request and passing tests.
- Notebook outputs are kept in git.
- No 2024 scores until the end.
