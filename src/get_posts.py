import os
import json
import itertools
import requests
import facebook
import elasticsearch

POST_FIELDS = 'id,created_time,from,message,permalink_url,full_picture,place,' \
              'reactions{id},comments{id},shares'

def fb_post_to_es_doc(post):
    doc = {
        'created_time': post['created_time'],
        'message': post.get('message'),
        'from': post['from']['name'],
        'permalink_url': post['permalink_url'],
        'full_picture': post.get('full_picture'),
        'shares': get_shares_count(post),
        'comments': get_object_count(post, 'comments'),
        'reactions': get_object_count(post, 'reactions')
    }
    doc['total_interactions'] = doc['shares'] + doc['comments'] + doc['reactions']
    doc.update(get_place(post))
    return post['id'], doc

def get_shares_count(post):
    return post['shares']['count'] if 'shares' in post else 0

def get_object_count(post, object_name):
    count = 0
    if object_name in post:
        for obj in itertools.chain([post[object_name]], pages(post[object_name])):
            count += len(obj['data'])
    return count

def get_place(post):
    place_info = {}
    place = post.get('place')
    if place:
        place_info['place_name'] = place.get('name')
        location = place.get('location')
        if location:
            place_info['city'] = location.get('city')
            place_info['country'] = location.get('country')
            place_info['coordinates'] = {
                'lat': location.get('latitude'),
                'lon': location.get('longitude')
            }
    return place_info

def process_data(data, es_api):
    print 'processing batch of {0} posts'.format(len(data))
    for post in data:
        post_id, doc = fb_post_to_es_doc(post)
        es_api.index('hbc', 'post', json.dumps(doc), post_id)

def get_next_page(obj):
    next_page_url = obj['paging']['next']
    print 'next object URL: {0}'.format(next_page_url)
    return requests.get(next_page_url).json()

def has_more_data(obj):
    return ('paging' in obj) and ('next' in obj['paging'])

def pages(obj):
    while has_more_data(obj):
        obj = get_next_page(obj)
        yield obj


GRAPH_API = facebook.GraphAPI(access_token=os.environ['FB_TOKEN'], version='2.7')
ES_API = elasticsearch.Elasticsearch(os.environ['ES_HOST'])
INITIAL_FEED_PAGE = GRAPH_API.request(os.environ['FB_GROUP'] + '/feed', {'fields': POST_FIELDS})

# chain the initial feed and the following pages so that we can treat them as
# a single sequence and don't need to duplicate the logging and processing calls
for page_index, page in enumerate(
        itertools.chain([INITIAL_FEED_PAGE], pages(INITIAL_FEED_PAGE)), start=1):
    print 'processing page: {0}'.format(page_index)
    process_data(page['data'], ES_API)
