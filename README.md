# PvPCenterFrontend
Usage (after cloning repo)
```bash
$ mkvirtualenv PvPCenterFrontend
$ pip install nodeenv
$ nodeenv -p
$ npm install
$ npm install -g grunt-cli, bower, less, coffee-script
$ bower install
$ grunt dev
$ python run_app.py
```

To refresh static files (copy from dependencies and static files to /dist, kill server if running)
```bash
$ grunt static
$ python run_app.py
```

Autorefresh after file change
```bash
$ grunt watch
```
