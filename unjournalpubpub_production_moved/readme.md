To run scripts like 'create_eval_01' in the command line you need to have sourced and installed some things.



Set up this virtual environment

```
source .venv/bin/activate
```

And then

```
python -m venv .venv
```

And then source the env:

```
source .venv/bin/activate
```

Install stuff

```

pip install --verbose git+https://github.com/unjournal/pypubpub@main

pip install pytest bibtexparser

pip install nltk
pip install pycryptodome pyparsing
pip install pluggy
pip install python-slugify
pip install typing

```
and more?


For the conf.py file:

```
community_url="https://unjournal.pubpub.org"
community_id="d28e8e57-7f59-486b-9395-b548158a27d6"

```

To lookup author pubpub ids (or any pubpub id) use https://pubpub.tefkah.com/

passwords are saved  in G collab (ask David)


And to run a script in python via command line, just type:

```
python create_eval_01.py
```
