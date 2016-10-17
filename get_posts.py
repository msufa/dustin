import os
import json
import facebook
import elasticsearch

def fb_to_es(fb):
	es = {}
	es['created_time'] = fb['created_time']
	es['message'] = fb['message']
	es['from'] = fb['from']['name']
	return fb['id'], es

graph = facebook.GraphAPI(access_token=os.environ['FB_TOKEN'], version='2.7')
feed = graph.request(os.environ['FB_GROUP'] + '/feed', {'fields': 'id,created_time,from,message'})
es = elasticsearch.Elasticsearch(os.environ['ES_HOST'])

for post in feed['data']:
	id, doc = fb_to_es(post)
	es.create('hbc', 'post', json.dumps(doc), id)
