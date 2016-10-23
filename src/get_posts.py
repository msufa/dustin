import os
import json
import facebook
import elasticsearch
import requests
import itertools

POST_FIELDS = 'id,created_time,from,message,permalink_url,full_picture,reactions{id},comments{id},shares,place'

def fb_post_to_es_doc(post):
	doc = {}
	doc['created_time'] = post['created_time']
	doc['message'] = post.get('message')
	doc['from'] = post['from']['name']
	doc['permalink_url'] = post['permalink_url']
	doc['full_picture'] = post.get('full_picture')
	doc['interactions'] = {
		'shares': get_shares_count(post),
		'comments': get_object_count(post, 'comments'),
		'reactions': get_object_count(post, 'reactions')
	}
	doc['interactions']['total'] = sum(doc['interactions'].values())
	doc['location'] = get_location(post)
	return post['id'], doc

def get_shares_count(post):
	return post['shares']['count'] if 'shares' in post else 0

def get_object_count(post, object_name):
	count = 0
	if object_name in post:
		for obj in itertools.chain([post[object_name]], pages(post[object_name])):
			count += len(obj['data'])
	return count

def get_location(post):
	if 'place' in post and 'location' in post['place']:
		return {
			'lat': post['place']['location']['latitude'],
			'lon': post['place']['location']['longitude']
		}
	return None

def process_data(data, es):
	print 'processing batch of {0} posts'.format(len(data))
	for post in data:
		id, doc = fb_post_to_es_doc(post)
		es.index('hbc', 'post', json.dumps(doc), id)

def get_next_page(obj):
	next = obj['paging']['next']
	print 'next object URL: {0}'.format(next)
	return requests.get(next).json()

def has_more_data(obj):
	return ('paging' in obj) and ('next' in obj['paging'])

def pages(obj):
	while has_more_data(obj):
		obj = get_next_page(obj)
		yield obj


graph_api = facebook.GraphAPI(access_token=os.environ['FB_TOKEN'], version='2.7')
es_api = elasticsearch.Elasticsearch(os.environ['ES_HOST'])
feed = graph_api.request(os.environ['FB_GROUP'] + '/feed', {'fields': POST_FIELDS})

# chain the initial feed and the following pages so that we can treat them as
# a single sequence and don't need to duplicate the logging and processing calls
for page_index, page in enumerate(itertools.chain([feed], pages(feed)), start=1):
	print 'processing page: {0}'.format(page_index)
	process_data(page['data'], es_api)
