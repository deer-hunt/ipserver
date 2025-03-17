from http.client import HTTPConnection, HTTPSConnection


class Requester:
    def request(self, method, parsed_url, headers, post_data):
        https = True if parsed_url.scheme == 'https' else False
        connection = self.get_connection(parsed_url.netloc, https)

        path = parsed_url.path

        if parsed_url.query:
            path += '?' + parsed_url.query

        connection.request(method, path, body=post_data, headers=headers)

        response = connection.getresponse()

        binary = response.read()

        return response, binary

    def get_connection(self, hostname, https=False):
        if https:
            connection = HTTPSConnection(hostname)
        else:
            connection = HTTPConnection(hostname)

        return connection
