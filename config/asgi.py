"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import tempfile

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_application = get_asgi_application()

# Bodies are buffered only when a proxy sends them without a length; anything
# past this many bytes spills from memory to a temporary file.
SPOOL_LIMIT = 1024 * 1024
READ_BLOCK = 64 * 1024


class ChunkedMultipartBody:
    """Publish the length of a chunked multipart body to Django.

    A proxy may forward a form body with ``Transfer-Encoding: chunked`` instead
    of ``Content-Length``. Django takes the size of a multipart body from
    CONTENT_LENGTH and returns an empty POST when the header is absent
    (django/http/multipartparser.py), so every multipart/form-data post — file
    uploads, the profile form with its photo field — failed CSRF with
    "CSRF token missing", even though the form carried a valid token and the
    origin was trusted. urlencoded posts never had the problem because they
    parse the streamed body directly, which is why login kept working while
    uploads did not.

    Only those requests are touched: the body is read once and replayed to
    Django with the real length added to the scope. Requests that already
    carry a Content-Length, chunked non-multipart bodies and every other
    request pass through untouched. CSRF enforcement itself is unchanged — a
    request without a valid token is still rejected.
    """

    def __init__(self, application):
        self.application = application

    @staticmethod
    def _needs_length(scope):
        # Only methods whose body Django may parse as a form are affected.
        if scope.get('method') not in ('POST', 'PUT', 'PATCH'):
            return False
        headers = dict(scope.get('headers') or [])
        if b'content-length' in headers:
            return False
        if headers.get(b'transfer-encoding', b'').lower() != b'chunked':
            return False
        return headers.get(b'content-type', b'').startswith(b'multipart/form-data')

    async def __call__(self, scope, receive, send):
        if scope.get('type') != 'http' or not self._needs_length(scope):
            return await self.application(scope, receive, send)
        spool = tempfile.SpooledTemporaryFile(max_size=SPOOL_LIMIT)
        total = 0
        complete = False
        try:
            while True:
                message = await receive()
                if message.get('type') != 'http.request':
                    break
                chunk = message.get('body', b'')
                if chunk:
                    spool.write(chunk)
                    total += len(chunk)
                if not message.get('more_body', False):
                    complete = True
                    break

            empty_body_frame_sent = False

            async def replay():
                nonlocal empty_body_frame_sent
                if complete:
                    block = spool.read(READ_BLOCK)
                    if block:
                        return {
                            'type': 'http.request',
                            'body': block,
                            'more_body': spool.tell() < total,
                        }
                    if not total and not empty_body_frame_sent:
                        # An empty body still needs its one empty frame, or Django
                        # reads the request as a client disconnect.
                        empty_body_frame_sent = True
                        return {'type': 'http.request', 'body': b'', 'more_body': False}
                # The buffered body is finished. Hand over what the server sends
                # next, dropping stray body frames: Django rejects anything but a
                # disconnect once it has read the request body.
                while True:
                    message = await receive()
                    if message.get('type') != 'http.request':
                        return message

            if complete:
                headers = list(scope.get('headers') or [])
                headers.append((b'content-length', str(total).encode()))
                scope = dict(scope, headers=headers)
                spool.seek(0)
            return await self.application(scope, replay, send)
        finally:
            spool.close()


application = ChunkedMultipartBody(django_application)
