from coreapi.auth import TokenAuthentication, domain_matches


class AuthenticationWithCustomHeader(TokenAuthentication):
    header_name = 'Authorization'

    def __init__(self, token, scheme=None, domain=None, header_name=None):
        self.header_name = header_name
        super().__init__(token, scheme, domain)

    def __call__(self, request):
        if not domain_matches(request, self.domain):
            return request

        if self.scheme:
            request.headers[self.header_name] = '%s %s' % (self.scheme, self.token)
        else:
            request.headers[self.header_name] = self.token

        return request

