# Dustin

Currently these are the roots of (hopefully some day) a web service consuming hooks for group posts from Facebook and forwarding them to an ElasticSearch index.

So far this is just a simple Python script that fetches post data for a specified Facebook Group, parses and ingests it to a specified ES index.

[![Build Status](https://travis-ci.org/msufa/dustin.svg?branch=master)](https://travis-ci.org/msufa/dustin)

## Requirements

You need to set some environment variables which the script expects to be able to authenticate in all the relevant services:
* FB_TOKEN - the Graph API token you'll use to authorize the API calls
* FB_GROUP - the Facebook Group you wish to index
* ES_HOST - the ElasticSearch target host

Dummy edit to trigger PR build.
