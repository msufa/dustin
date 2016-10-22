import os
import json
import facebook
import elasticsearch
import requests
import itertools

def fb_to_es(fb):
	es = {}
	es['created_time'] = fb['created_time']
	es['message'] = fb.get('message')
	es['from'] = fb['from']['name']
	return fb['id'], es

def process_data(data):
	print 'processing batch of {0} posts'.format(len(data))
	for post in data:
		id, doc = fb_to_es(post)
		es.index('hbc', 'post', json.dumps(doc), id)

def get_next_page(feed):
	next = feed['paging']['next']
	print 'next feed URL: {0}'.format(next)
	return requests.get(next).json()

def has_more_data(feed):
	return ('paging' in feed) and ('next' in feed['paging'])

def pages(feed):
	while has_more_data(feed):
		feed = get_next_page(feed)
		yield feed


graph = facebook.GraphAPI(access_token=os.environ['FB_TOKEN'], version='2.7')
es = elasticsearch.Elasticsearch(os.environ['ES_HOST'])
feed = graph.request(os.environ['FB_GROUP'] + '/feed', {'fields': 'id,created_time,from,message'})

# chain the initial feed and the following pages so that we can treat them as
# a single sequence and don't need to duplicate the logging and processing calls
for page_index, page in enumerate(itertools.chain([feed], pages(feed)), start=1):
	print 'processing page: {0}'.format(page_index)
	process_data(page['data'])
