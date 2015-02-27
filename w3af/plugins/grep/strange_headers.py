"""
strange_headers.py

Copyright 2006 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import w3af.core.data.kb.knowledge_base as kb

from w3af.core.controllers.plugins.grep_plugin import GrepPlugin
from w3af.core.data.kb.info import Info
from w3af.core.data.kb.info_set import InfoSet


class strange_headers(GrepPlugin):
    """
    Grep headers for uncommon headers sent in HTTP responses.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """
    # Remember that this headers are only the ones SENT BY THE SERVER TO THE
    # CLIENT. Headers must be uppercase in order to compare them
    COMMON_HEADERS = {'ACCEPT-RANGES', 'AGE', 'ALLOW', 'CONNECTION',
                      'CONTENT-DISPOSITION', 'CONTENT-ENCODING',
                      'CONTENT-LENGTH', 'CONTENT-TYPE', 'CONTENT-SCRIPT-TYPE',
                      'CONTENT-STYLE-TYPE', 'CONTENT-SECURITY-POLICY',
                      'CONTENT-SECURITY-POLICY-REPORT-ONLY', 'CONTENT-LANGUAGE',
                      'CONTENT-LOCATION', 'CACHE-CONTROL', 'DATE', 'EXPIRES',
                      'ETAG', 'FRAME-OPTIONS', 'KEEP-ALIVE', 'LAST-MODIFIED',
                      'LOCATION', 'P3P', 'PUBLIC', 'PUBLIC-KEY-PINS',
                      'PUBLIC-KEY-PINS-REPORT-ONLY', 'PRAGMA',
                      'PROXY-CONNECTION', 'SET-COOKIE', 'SERVER',
                      'STRICT-TRANSPORT-SECURITY', 'TRANSFER-ENCODING', 'VIA',
                      'VARY', 'WWW-AUTHENTICATE', 'X-FRAME-OPTIONS',
                      'X-CONTENT-TYPE-OPTIONS', 'X-POWERED-BY',
                      'X-ASPNET-VERSION', 'X-CACHE', 'X-UA-COMPATIBLE', 'X-PAD',
                      'X-XSS-PROTECTION'}

    def grep(self, request, response):
        """
        Check if the header names are common or not

        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None, all results are saved in the kb.
        """
        # Check for protocol anomalies
        self._content_location_not_300(request, response)

        # Check header names
        for header_name in response.get_headers().keys():
            if header_name.upper() in self.COMMON_HEADERS:
                continue

            # Create a new info object and save it to the KB
            hvalue = response.get_headers()[header_name]

            itag = 'header_name'
            desc = 'The remote web server sent the HTTP header: "%s"'\
                   ' with value: "%s", which is quite uncommon and'\
                   ' requires manual analysis.'
            desc = desc % (header_name, hvalue)

            i = Info('Strange header', desc, response.id, self.get_name())
            i.add_to_highlight(hvalue, header_name)
            i.set_url(response.get_url())
            i[itag] = header_name
            i['header_value'] = hvalue

            ff = lambda iset, info: iset.get_attribute(itag) == info[itag]
            self.kb_append_uniq_group(self, 'strange_headers', i, ff,
                                      group_klass=StrangeHeaderInfoSet)

    def _content_location_not_300(self, request, response):
        """
        Check if the response has a content-location header and the response
        code is not in the 300 range.

        :return: None, all results are saved in the kb.
        """
        headers = response.get_headers()
        header_value, header_name = headers.iget('content-location')

        if header_value is not None and 300 < response.get_code() < 310:
            desc = 'The URL: "%s" sent the HTTP header: "content-location"'\
                   ' with value: "%s" in an HTTP response with code %s which'\
                   ' is a violation to the RFC.'
            desc = desc % (response.get_url(),
                           header_value,
                           response.get_code())
            i = Info('Content-Location HTTP header anomaly', desc,
                     response.id, self.get_name())
            i.set_url(response.get_url())
            i.add_to_highlight('content-location')
            
            kb.kb.append(self, 'anomaly', i)

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin greps all headers for non-common headers. This could be
        useful to identify special modules and features added to the server.
        """


class StrangeHeaderInfoSet(InfoSet):
    TEMPLATE = (
        'The remote web server sent {{ uris|length }} HTTP responses with'
        ' the uncommon response header "{{ header_name }}", one of the received'
        ' header values is "{{ header_value }}". The first ten URLs which sent'
        ' the uncommon header are:\n'
        ''
        '{% for url in uris[:10] %}'
        ' - {{ url }}\n'
        '{% endfor %}'
    )