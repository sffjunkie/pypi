from requests.auth import AuthBase, HTTPBasicAuth


class MultiDomainBasicAuth(AuthBase):
    def __init__(self, prompting=True):
        self.prompting = prompting
        self.passwords = {}

    def __call__(self, req):
        parsed = urllib_parse.urlparse(req.url)

        # Get the netloc without any embedded credentials
        netloc = parsed.netloc.rsplit("@", 1)[-1]

        # Set the url of the request to the url without any credentials
        req.url = urllib_parse.urlunparse(parsed[:1] + (netloc,) + parsed[2:])

        # Use any stored credentials that we have for this netloc
        username, password = self.passwords.get(netloc, (None, None))

        # Extract credentials embedded in the url if we have none stored
        if username is None:
            username, password = self.parse_credentials(parsed.netloc)

        if username or password:
            # Store the username and password
            self.passwords[netloc] = (username, password)

            # Send the basic auth with this request
            req = HTTPBasicAuth(username or "", password or "")(req)

        # Attach a hook to handle 401 responses
        req.register_hook("response", self.handle_401)

        return req

    def handle_401(self, resp, **kwargs):
        # We only care about 401 responses, anything else we want to just
        #   pass through the actual response
        if resp.status_code != 401:
            return resp

        # We are not able to prompt the user so simple return the response
        if not self.prompting:
            return resp

        parsed = urllib_parse.urlparse(resp.url)

        # Prompt the user for a new username and password
        username = six.moves.input("User for %s: " % parsed.netloc)
        password = getpass.getpass("Password: ")

        # Store the new username and password to use for future requests
        if username or password:
            self.passwords[parsed.netloc] = (username, password)

        # Consume content and release the original connection to allow our new
        #   request to reuse the same one.
        resp.content
        resp.raw.release_conn()

        # Add our new username and password to the request
        req = HTTPBasicAuth(username or "", password or "")(resp.request)

        # Send our new request
        new_resp = resp.connection.send(req, **kwargs)
        new_resp.history.append(resp)

        return new_resp

    def parse_credentials(self, netloc):
        if "@" in netloc:
            userinfo = netloc.rsplit("@", 1)[0]
            if ":" in userinfo:
                return userinfo.split(":", 1)
            return userinfo, None
        return None, None
