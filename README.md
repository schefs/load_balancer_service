# LoadBalancer Service

Python load balancer using aiohttp and async together with nginx all wrapped around containers for best performance for the given task

## /login endpoint**

traffic management on /login using GET request will be handled by NGINX server that will load balance the traffic using basic round-robin method.

client GET request on /login --> Nginx --> backend server number 1/2/3

## /changePassword or /register endpoint:

traffic management on /changePassword or /register will be handled differently since there is more complexity involved.

client POST request on /changePassword or /register --> Nginx --> Python load balancer (with the business logic inside) --> forward requests to all backend servers

## backend services:
    
Each backend service was writen as an example for a possible (not so good) of a service that may hiccup from time to time.
It will be controlled using ENV `SKIP_SOME_REQUESTS= "true"/"false"`.
This will help us to observe the LB service ability to recover from such cases of downtime using exposed metrics or stdout output.

In the supplied docker-compose file one of three backend servers `SKIP_SOME_REQUESTS` ENV is set to `true`.

## Load Balance python service:

This is main component managing the more complex actions required by the project.
it writen mainly using `aiohttp` and `asyncio` to deal with async requests to support the required scale.

Each request will be forwarded to ALL backend server demanding them to return `201` status code, or the LB service will keep retrying until succeed.
To avoid bad practice by default maximum retry attempts is set to 100 instead of affinity but can be change when use case varies.

Retry algorithm used is a simple exponential backoff.  

In a case of a retry wait time is `min(((2^n) + random_number_milliseconds), maximum_backoff + random_number_milliseconds)`, with n incremented by 1 for each iteration (request).

`random_number_milliseconds` is a random number of milliseconds less than or equal to 100. This helps to avoid cases in which many clients are synchronized by some situation and all retry at once, sending requests in synchronized waves. The value of random_number_milliseconds is recalculated after each retry request.

maximum_backoff is set by default to 64 seconds. The appropriate value depends on the scenario .



## metrics:

Simple nginx metrics can be found under `http://localhost/nginx_status` or in Prometheus format using prometheus exporter under `http://localhost:8000/metrics`

few simple metrics are exposed at this time from the python LB service also using Prometheus style metrics for an easy scrape.
The following custom metrics are exposed by default on `http://localhost/metrics`. 

For example:


    target_domain_success_counter_total{domain="server2:8080"} 15.0
    target_domain_success_counter_total{domain="server3:8080"} 15.0
    target_domain_success_counter_total{domain="server1:8080"} 15.0
    target_domain_failed_counter_total{domain="server1:8080"} 3.0
    target_domain_failed_counter_total{domain="server2:8080"} 2.0
    target_domain_failed_counter_total{domain="server3:8080"} 2.0
    Total_domains_failed_counter_total 7.0
    Total_domains_success_counter_total 45.0

## Build guidelines:

Nginx is only using a template configuration file injected in runtime so no build is needed for it

if you want to build load balancer service:
    
    cd load_balancer
    docker build -t schef/load-balancer-server:v1 .

or demo backend service:

    cd demo_backend_server
    docker build -t schef/demo_web_server:v1 .

## Running the services:

To run the services locally:
    
    docker-compose up -d 

You can go head and try to access the load balancer service for example:
    
    curl localhost/login
    curl -X POST -d 'username=schef' -d 'password=example' localhost/register
    curl -X POST -d 'username=schef' -d 'password=example' http://localhost/changePassword


## Load test this thing using Locust:
    
    You can run a simple banchmark on the services to test the capability

    cd locust_load_test
    docker-compose up --scale worker=10

Also, you can find a report file on `locust_load_test/report.html` already ready for you.

In this report the locust workers where running on the same machine as the web server where running on, 
so I was experiencing some bottlenecks in terms of high utilization on this local machine tested, but it probably can get even better results when services are spread across multiple machines.

## Cleanup

don't forget to clean up after yourself  and run once services are no longer needed:
    
    docker-compose down