# Oberon
This repo contains the backend for the Villanova Courses platform

## Primary Features
 Fetches course data from Banner on a schedule
 Parses Course data and writes the data into a database

# To Run Oberon

## You will need . . .
1. python 2.7
2. Python Install Package (pip)
3. PostgreSQL (psql)
4. virtualenv (through pip)

### on OSX

```brew doctor```

```brew update```

```brew install postgresql```

### on Linux (Ubuntu for now)

```sudo apt-get install postgresql```

### setup

```pip install virtualenv```

```createdb VillanovaCourseDB```

```virtualenv oberon-env``` (will create your environment)

```source oberon-env/bin/activate``` (will start reload your shell to use the environment)

```git clone the repo```

```cd Oberon```

```pip install -r requirements.txt``` (fetch the dependencies for the project)

```cd oberon``` (get into the src)

download the output2.html, config.py, and private.py and place them in this src folder

```python populate_db.py``` (fetches the info from the output file)

```python oberon.py``` (spins up the api on port 5000)

Visit the api in your browser



