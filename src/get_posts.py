import os
import json
import facebook
import elasticsearch
import requests
import itertools

POST_FIELDS = 'id,created_time,from,message,permalink_url,full_picture,reactions{type},comments{id},shares'

def fb_to_es(fb):
	es = {}
	es['created_time'] = fb['created_time']
	es['message'] = fb.get('message')
	es['from'] = fb['from']['name']
	es['permalink_url'] = fb['permalink_url']
	es['full_picture'] = fb.get('full_picture')
	es['shares'] = get_shares_count(fb)
	es['comments'] = get_comments_count(fb)
	return fb['id'], es

def get_shares_count(post):
	return post['shares']['count'] if 'shares' in post else 0

def get_comments_count(post):
	count = 0
	if 'comments' in post:
		for comments in itertools.chain([post['comments']], pages(post['comments'])):
			count += len(comments['data'])
	return count

def process_data(data):
	print 'processing batch of {0} posts'.format(len(data))
	for post in data:
		id, doc = fb_to_es(post)
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


graph = facebook.GraphAPI(access_token=os.environ['FB_TOKEN'], version='2.7')
es = elasticsearch.Elasticsearch(os.environ['ES_HOST'])
feed = graph.request(os.environ['FB_GROUP'] + '/feed', {'fields': POST_FIELDS})

# chain the initial feed and the following pages so that we can treat them as
# a single sequence and don't need to duplicate the logging and processing calls
for page_index, page in enumerate(itertools.chain([feed], pages(feed)), start=1):
	print 'processing page: {0}'.format(page_index)
	process_data(page['data'])
