curl -XDELETE http://$ES_HOST:9200/hbc
curl -XPUT http://$ES_HOST:9200/hbc -d @${BASH_SOURCE%/*}/data/post_mapping.json
