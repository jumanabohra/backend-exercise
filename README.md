# This is a solution to the following LNRS problem

https://github.com/RiskNarrative/spring-exercise

# Backend (Python and FastAPI)

This is the backend API to fetch the list of companies and their officers

## Prerequisites

- Python 3.10+

## Setup Instructions

MAC environment

- Install `pipx` on your system: `brew install pipx`
- Clone this repo
- Run `pipx install poetry`
- Run `poetry install`
- Run `pipx ensurepath` to ensure that apps can be accessed globally (Note you will have to restart terminal if you need this step)
- Run `fastapi dev main.py` to start the server

The app runs by default on [http://localhost:8000](http://localhost:8000). To open Swagger docs, go to [http://localhost:8000/docs](http://localhost:8000/docs).

## Production

To run in production mode, run `fastapi run main.py`.
