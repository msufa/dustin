# I am Dustin!

Ultimately, a web service consuming hooks for group posts
from Facebook and forwarding them to an ElasticSearch index.

[![Build Status](https://travis-ci.org/msufa/dustin.svg?branch=master)](https://travis-ci.org/msufa/dustin)

## Requirements

You need to set some environment variables:
* FB_TOKEN - the Graph API token you'll use to authorize the API calls
* FB_GROUP - the Facebook group you wish to index
* ES_HOST - the ElasticSearch target host
