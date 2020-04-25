from pymongo import MongoClient


## Database configuration

DB = {
    'auth': {
        'username': 'service-portfolio',
        'password': 'gRWn33ZIhV9u'
    },
    'connection': {
        'schema': 'mongodb+srv',
        'host': 'cluster0-ind5n.mongodb.net',
        'path': 'test?retryWrites=true&w=majority'
    }
}

CONNECTION_STRING = '{schema}://{username}:{password}@{host}/{path}'.format(**DB['auth'], **DB['connection'])

database = MongoClient(CONNECTION_STRING).portfolio
