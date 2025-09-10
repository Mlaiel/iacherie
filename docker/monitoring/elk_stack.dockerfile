# ELK Stack - Multi-stage build for Elasticsearch, Logstash, and Kibana

# Elasticsearch
FROM docker.elastic.co/elasticsearch/elasticsearch:8.8.0 AS elasticsearch
ENV cluster.name=ainflue-monitoring
ENV discovery.type=single-node
ENV "ES_JAVA_OPTS=-Xms2g -Xmx2g"
ENV xpack.security.enabled=false
EXPOSE 9200
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:9200/_cluster/health || exit 1

# Logstash
FROM docker.elastic.co/logstash/logstash:8.8.0 AS logstash
ENV "LS_JAVA_OPTS=-Xmx1g -Xms1g"
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
EXPOSE 5044 9600
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:9600/ || exit 1

# Kibana  
FROM docker.elastic.co/kibana/kibana:8.8.0 AS kibana
ENV ELASTICSEARCH_HOSTS=http://elasticsearch:9200
ENV SERVER_HOST=0.0.0.0
EXPOSE 5601
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:5601/api/status || exit 1