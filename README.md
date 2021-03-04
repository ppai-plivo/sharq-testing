## sharq-testing

Requires python3:

```sh
$ python3 --version
Python 3.9.2
```

Setup environment, install sharq and other dependencies:

```sh
$ python3 -m venv env
$ source env/bin/activate
$ pip3 install -U pip
$ pip3 install -r requirements.txt
```

Run redis locally as single server:

```sh
$ redis-server --version
Redis server v=6.0.9 sha=00000000:0 malloc=libc bits=64 build=85c36b8d70a68649
$ redis-server
```
