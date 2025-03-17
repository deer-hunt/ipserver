from urllib.parse import urlparse, urlunparse


class URLParser:
    '''
    test-sample.com:443
    test-sample.com
    //test-sample.com/
    http://test-sample.com/
    http://test-sample.com/sample
    HTTP://test-sample.com/abc
    https://test-sample.com
    test-sample.com/sample
    '''

    def parse(self, url, aux_port=True):
        if '//' not in url:
            url = '//' + url

        parsed = urlparse(url)

        if aux_port:
            if (parsed.scheme == 'https' or parsed.scheme == 'ssl') and not parsed.port:
                new_url = urlunparse((parsed.scheme, '{}:{}'.format(parsed.hostname, 443), parsed.path, parsed.params, parsed.query, parsed.fragment))
                parsed = urlparse(new_url)

        return parsed

    def parse_url(self, url):
        parsed = self.parse(url)

        if not parsed.path:
            parsed = parsed._replace(path='/')

        if not parsed.scheme:
            if parsed.port == 443:
                parsed = parsed._replace(scheme='https')
            else:
                parsed = parsed._replace(scheme='http')

        return parsed

    def normalize_url(self, url):
        parsed = self.parse_url(url)

        return urlunparse(parsed)
