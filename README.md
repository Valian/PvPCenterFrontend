# PvPCenterFrontend
Usage (after cloning, assuming pip installed)
```bash
$ sudo pip install virtualenv virtualenvwrapper
$ mkvirtualenv PvPCenterFrontend
$ pip install nodeenv
$ nodeenv -p --prebuilt
$ npm install
$ npm install -g grunt-cli bower less coffee-script
$ pip install -r requirements/dev.txt
$ bower install
$ workon PvPCenterFrontend
$ grunt dev
$ python run_app.py
```

To activate virtualenv:
```bash
$ workon PvPCenterFrontend
```

To refresh static files (copy from dependencies and static files to /dist, you must kill server if running)
```bash
$ grunt static
$ python run_app.py
```

Autorefresh after file change (you can add it to your virtualenv postactivate script)
```bash
$ grunt watch
```

If virtualenvwrapper is not working, try setting WORKON_HOME variable in your ~/.bashrc file:
```bash
export WORKON_HOME=~/.virtualenvs
```
reload console and make sure, that WORKON_HOME folder exists:
```bash
$ mkdir $WORKON_HOME
```