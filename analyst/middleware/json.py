import falcon


class RequireJSONMiddleware:
    """
    Require JSON Middleware

    Ensure each requests is expecting a JSON response.  Check HTTP Header `Accept`
    """

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                "This API only accepts responses encoded as JSON."
            )
