import os
import json
import facebook
import elasticsearch
import requests

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

def get_next_feed(feed):
	next = feed['paging'].get('next') if 'paging' in feed else None
	print 'next feed URL: {0}'.format(next)
	return requests.get(next).json() if next else None

def crawl_remaining_feeds(initial_feed):
	next_feed = get_next_feed(initial_feed)
	page = 2
	while next_feed:
		print 'processing page: {0}'.format(page)
		process_data(next_feed['data'])
		next_feed = get_next_feed(next_feed)
		page += 1


graph = facebook.GraphAPI(access_token=os.environ['FB_TOKEN'], version='2.7')
es = elasticsearch.Elasticsearch(os.environ['ES_HOST'])
initial_feed = graph.request(os.environ['FB_GROUP'] + '/feed', {'fields': 'id,created_time,from,message'})

process_data(initial_feed['data'])
crawl_remaining_feeds(initial_feed)
