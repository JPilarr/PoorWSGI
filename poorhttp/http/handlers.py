
from random import random
from time import localtime
from traceback import format_exception
from os import name as osname
#
# $Id$
#

from exceptions import IOError
import types, sys, os

from enums import *
import env

class SERVER_RETURN(Exception):
    def __init__(self, code = HTTP_INTERNAL_SERVER_ERROR):
        Exception.__init__(self, code)
#endclass

def redirect(req, uri, permanent = 0, text = None):
    """
    Redirect server request to url via 302 server status.
    """
    if len(req.headers_out) > 2 or \
        'Server' not in req.headers_out or 'X-Powered-By' not in req.headers_out:
        raise IOError('Headers are set before redirect')
    
    url = req.construct_url(uri)
    
    if permanent:
        req.status = HTTP_MOVED_PERMANENTLY
    else:
        req.status = HTTP_MOVED_TEMPORARILY
    
    req.headers_out.add('Location', url)
    if text:
        req.write(text)
    raise SERVER_RETURN, DONE
#enddef

def forbidden(req):
    content = \
        "<html>\n"\
        "  <head>\n"\
        "    <title>403 - Forbidden Acces</title>\n"\
        "    <style>\n"\
        "      body {width: 80%%; margin: auto; padding-top: 30px;}\n"\
        "      h1 {text-align: center; color: #ff0000;}\n"\
        "      p {text-indent: 30px; margin-top: 30px; margin-bottom: 30px;}\n"\
        "    </style>\n"\
        "  <head>\n" \
        "  <body>\n"\
        "    <h1>403 - Forbidden Acces</h1>\n"\
        "    <p>You don't have permission to access <code>%s</code> on this server.</p>\n"\
        "    <hr>\n"\
        "    <small><i>webmaster: %s </i></small>\n"\
        "  </body>\n"\
        "</html>" % (req.uri, env.webmaster)
        
    req.content_type = "text/html"
    req.status = HTTP_FORBIDDEN
    req.headers_out = req.err_headers_out
    req.headers_out.add('Content-Length', str(len(content)))
    req.write(content)
    return DONE
#enddef

def not_found(req):
    content = \
        "<html>\n"\
        "  <head>\n"\
        "    <title>404 - Page Not Found</title>\n"\
        "    <style>\n"\
        "      body {width: 80%%; margin: auto; padding-top: 30px;}\n"\
        "      h1 {text-align: center; color: #707070;}\n"\
        "      p {text-indent: 30px; margin-top: 30px; margin-bottom: 30px;}\n"\
        "    </style>\n"\
        "  <head>\n" \
        "  <body>\n"\
        "    <h1>404 - Page Not Found</h1>\n"\
        "    <p>Your reqeuest <code>%s</code> was not found.</p>\n"\
        "    <hr>\n"\
        "    <small><i>webmaster: %s </i></small>\n"\
        "  </body>\n"\
        "</html>" % (req.uri, env.webmaster)
        
    req.content_type = "text/html"
    req.status = HTTP_NOT_FOUND
    req.headers_out = req.err_headers_out
    req.headers_out.add('Content-Length', str(len(content)))
    req.write(content)
    return DONE
#enddef

def method_not_allowed(req):
    content = \
        "<html>\n"\
        "  <head>\n"\
        "    <title>405 - Method Not Allowed</title>\n"\
        "    <style>\n"\
        "      body {width: 80%%; margin: auto; padding-top: 30px;}\n"\
        "      h1 {text-align: center; color: #707070;}\n"\
        "      p {text-indent: 30px; margin-top: 30px; margin-bottom: 30px;}\n"\
        "    </style>\n"\
        "  <head>\n"\
        "  <body>\n"\
        "    <h1>405 - Method Not Allowed</h1>\n"\
        "    <p>This method %s is not allowed to access <code>%s</code> on this server.</p>\n"\
        "    <hr>\n"\
        "    <small><i>webmaster: %s </i></small>\n"\
        "  </body>\n"\
        "</html>" % (req.method, req.uri, env.webmaster)
        
    req.content_type = "text/html"
    req.status = HTTP_METHOD_NOT_ALLOWED
    req.headers_out = req.err_headers_out
    req.headers_out.add('Content-Length', str(len(content)))
    req.write(content)
    return DONE
#enddef

def internal_server_error(req):
    """
    This function call error log in init. When is not used, errors will
    not be loged. See code.
    """
    traceback = format_exception(sys.exc_type,
                                 sys.exc_value,
                                 sys.exc_traceback)
    traceback = ''.join(traceback)
    req.log_error(traceback, LOG_ERR)
    traceback = traceback.split('\n')

    req.content_type = "text/html"
    req.status = HTTP_INTERNAL_SERVER_ERROR
    req.headers_out = req.err_headers_out

    content = [
            "<html>\n",
            "  <head>\n",
            "    <title>500 - Internal Server Error</title>\n",
            "    <style>\n",
            "      body {width: 80%%; margin: auto; padding-top: 30px;}\n",
            "      pre .line1 {background: #e0e0e0}\n",
            "    </style>\n",
            "  <head>\n",
            "  <body>\n",
            "    <h1>500 - Internal Server Error</h1>\n",
    ]
    for l in content: req.write(l)

    if env.debug:
        content = [
            "    <h2> Exception Traceback</h2>\n",
            "    <pre>",
        ]
        for l in content: req.write(l)

        # Traceback
        for i in xrange(len(traceback)):
            req.write('<div class="line%s">%s</div>' % ( i % 2, traceback[i]))

        content = [
            "    </pre>\n",
            "    <hr>\n",
            "    <small><i>Poor Http / %s, Python / %s, webmaster: %s </i></small>\n" % \
                    (env.server_version,
                    sys.version.split(' ')[0],
                    env.webmaster),
        ]
        for l in content: req.write(l)
    
    else:
        content = [
            "    <hr>\n",
            "    <small><i>webmaster: %s </i></small>\n" % env.webmaster ,
        ]
        for l in content: req.write(l)
    #endif
        
    content = [
        "  </body>\n",
        "</html>"
    ]

    for l in content: req.write(l)
    return DONE
#enddef

def not_implemented(req, code = None):
    content = \
            "<html>\n"\
            "  <head>\n"\
            "    <title>501 - Not Implemented</title>\n"\
            "    <style>\n"\
            "      body {width: 80%%; margin: auto; padding-top: 30px;}\n"\
            "      h1 {text-align: center; color: #707070;}\n"\
            "      p {text-indent: 30px; margin-top: 30px; margin-bottom: 30px;}\n"\
            "    </style>\n"\
            "  <head>\n"\
            "  <body>\n"\
            "    <h1>501 - Not Implemented</h1>\n"

    if code:
        content += \
            "    <p>Your reqeuest <code>%s</code> returned not implemented\n"\
            "      status <code>%s</code>.</p>\n" % (req.uri, code)
    else:
        content += \
            "    <p>Response for Your reqeuest <code>%s</code> is not implemented</p>" \
            % req.uri
    #endif

    content += \
            "    <hr>\n"\
            "    <small><i>webmaster: %s </i></small>\n"\
            "  </body>\n"\
            "</html>" % env.webmaster
        
    req.content_type = "text/html"
    req.status = HTTP_NOT_IMPLEMENTED
    req.headers_out = req.err_headers_out
    req.headers_out.add('Content-Length', str(len(content)))
    req.write(content)
    return DONE
#enddef

def sendfile(req, path):
    """
    Returns file with content_type detect from server configuration or
    application/octet-stream.
    """
    if not os.path.isfile(path):
        raise SERVER_RETURN, HTTP_FORBIDDEN

    bf = os.open(path, os.O_RDONLY)
    
    ext = os.path.splitext(path)
    if env.cfg.has_option('mime-type', ext[1][1:]):
        req.content_type = env.cfg.get('mime-type', ext[1][1:])
    else:
        req.content_type = 'application/octet-stream'
    #endif

    req.headers_out.add('Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(path))
    req.headers_out.add('Content-Length', str(os.fstat(bf).st_size))

    data = os.read(bf, 4096)
    while data != '':
        req.write(data)
        data = os.read(bf, 4096)
    #endwhile
    os.close(bf)

    return DONE
#enddef

errors = {
    HTTP_INTERNAL_SERVER_ERROR  : internal_server_error,
    HTTP_NOT_FOUND              : not_found,
    HTTP_METHOD_NOT_ALLOWED     : method_not_allowed,
    HTTP_FORBIDDEN              : forbidden,
    HTTP_NOT_IMPLEMENTED        : not_implemented,
}