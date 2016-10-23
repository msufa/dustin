curl -XDELETE http://$ES_USER:$ES_SECRET@$ES_HOST:9200/hbc
curl -XPUT http://$ES_USER:$ES_SECRET@$ES_HOST:9200/hbc -d @data/post_mapping.json
