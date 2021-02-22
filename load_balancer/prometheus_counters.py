import prometheus_client


class PrometheusCounters(object):
    c_success = prometheus_client.Counter('target_domain_success_counter',
                                          'Successful requests target domain counter', ['domain'])

    c_failed = prometheus_client.Counter('target_domain_failed_counter',
                                         'Failed requests target domain counter', ['domain'])

    c_total_success = prometheus_client.Counter('Total_domains_success_counter',
                                                'Total success requests for target domains counter')

    c_total_failed = prometheus_client.Counter('Total_domains_failed_counter',
                                               'Total Failed requests for target domains counter')

    def prometheus_inc_failed_counter(self, dst_domain):
        self.c_failed.labels(dst_domain).inc()
        self.c_total_failed.inc()

    def prometheus_inc_success_counter(self, dst_domain):
        self.c_success.labels(dst_domain).inc()
        self.c_total_success.inc()
