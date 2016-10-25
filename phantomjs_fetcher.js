// Author: Batman

var port, server, service,
    wait_before_end = 1000,
    rediect_codes = [301, 302, 303, 307],
    system = require('system'),
    webpage = require('webpage');

if (system.args.length !== 2) {
    console.log('Usage: simpleserver.js <portnumber>');
    phantom.exit(1);
} else {
    port = system.args[1];
    server = require('webserver').create();
    console.debug = function (msg) {
        //console.log(new Date().toJSON() + " " + msg);
    };

    log = function (msg) {
        console.log(new Date().toJSON() + " " + msg);
    };

    service = server.listen(port, {
        'keepAlive': false
    }, function (request, response) {
        phantom.clearCookies();

        console.debug(JSON.stringify(request, null, 4));
        if (request.method === 'GET') {
            body = "method not allowed!";
            response.statusCode = 403;
            response.headers = {
                'Cache': 'no-cache',
                'Content-Length': body.length
            };
            response.write(body);
            response.closeGracefully();
            return;
        }

        var first_response = null,
            finished = false,
            page_loaded = false,
            start_time = Date.now(),
            end_time = null,
            redirect_urls = [],
            follow_redirect = false,
            abort_ids = [];
        //script_executed = false,
        //script_result = null;

        var headers = request.headers;
        var fetch = request.post;

        // create and set page
        var page = webpage.create();
        page.onConsoleMessage = function (msg) {
            log('console: ' + msg);
        };

        page.viewportSize = {
            width: fetch['js_viewport_width'] || 1024,
            height: fetch['js_viewport_height'] || 768
        };

        // this may cause memory leak: https://github.com/ariya/phantomjs/issues/12903
        page.settings.loadImages = fetch['load_images'] === undefined ? false : fetch['load_images'];

        page.settings.resourceTimeout = fetch['timeout'] ? fetch['timeout'] * 1000 : 120 * 1000;

        page.settings.userAgent = headers['User-Agent'] ? headers['User-Agent'] : 'CloudScan/1.1';

        headers['Accept-Encoding'] = undefined;
        headers['Connection'] = undefined;
        headers['Content-Length'] = undefined;
        headers['Content-Type'] = undefined;
        headers['Host'] = undefined;
        page.customHeaders = headers;

        if (fetch['follow_redirect'] === 'true') {
            follow_redirect = true;
        }

        console.debug('page headers: ' + JSON.stringify(page.customHeaders, null, 4));
        console.debug('page settings: ' + JSON.stringify(page.settings, null, 4));

        // add callbacks
        page.onInitialized = function () {
            //if (!script_executed && fetch.js_script && fetch.js_run_at === "document-start") {
            //    script_executed = true;
            //    log('running document-start script.');
            //    script_result = page.evaluateJavaScript(fetch.js_script);
            //}
        };
        page.onLoadFinished = function (status) {
            page_loaded = true;
            //if (!script_executed && fetch.js_script && fetch.js_run_at !== "document-start") {
            //    script_executed = true;
            //    log('running document-end script.');
            //    script_result = page.evaluateJavaScript(fetch.js_script);
            //}
            console.debug("LoadFinished waiting " + wait_before_end + "ms before finished.");
            end_time = Date.now() + wait_before_end;
            setTimeout(make_result, wait_before_end + 10, page);
        };
        page.onResourceRequested = function (requestData, networkRequest) {
            if (!follow_redirect && redirect_urls.indexOf(requestData.url) !== -1) {
                console.debug("Abort redirect request: #" + requestData.id + " [" + requestData.method + "]" + requestData.url);
                abort_ids.push(requestData.id);
                networkRequest.abort();
            }

            // FIXME not support www.douban.com <= movie.douban.com
            if (get_domain(requestData.url) != get_domain(fetch.url)) {
                console.debug("Abort 3rd request: #" + requestData.id + " [" + requestData.method + "]" + requestData.url);
                abort_ids.push(requestData.id);
                networkRequest.abort();
            }

            console.debug("Starting request: #" + requestData.id + " [" + requestData.method + "]" + requestData.url);
            end_time = null;
        };
        page.onResourceReceived = function (response) {
            console.debug("Request finished: #" + response.id + " [" + response.status + "]" + response.url);
            if (follow_redirect) {
                if (first_response === null && rediect_codes.indexOf(response.status) === -1) {
                    first_response = response;
                }
            }
            else {
                if (first_response === null) {
                    first_response = response;
                }
                if (rediect_codes.indexOf(response.status) !== -1) {
                    console.debug("Request finished push redirect url: " + response.redirectURL);
                    redirect_urls.push(response.redirectURL);
                }
            }

            if (page_loaded) {
                console.debug("onResourceReceived waiting " + wait_before_end + "ms before finished.");
                end_time = Date.now() + wait_before_end;
                setTimeout(make_result, wait_before_end + 10, page);
            }
        };
        page.onResourceError = page.onResourceTimeout = function (resourceError) {
            if (abort_ids.indexOf(resourceError.id) === -1) {
                console.info("Request error: #" + resourceError.id + " [" + resourceError.errorCode + "="
                    + resourceError.errorString + "]" + resourceError.url);
                if (first_response === null) {
                    first_response = resourceError;
                }
                if (page_loaded) {
                    console.debug("onResourceError onResourceTimeout waiting " + wait_before_end + "ms before finished.");
                    end_time = Date.now() + wait_before_end;
                    setTimeout(make_result, wait_before_end + 10, page);
                }
            }
        };

        // make sure request will finished
        setTimeout(function (page) {
            make_result(page);
        }, page.settings.resourceTimeout + 100, page);

        // send request
        page.open(fetch.url, {
            operation: fetch.method,
            data: fetch.data
        });

        function get_domain(url) {
            var link = document.createElement('a');
            link.setAttribute('href', url);
            return link.hostname;
        }

        // make response
        function make_result(page) {
            if (finished) {
                return;
            }
            if (Date.now() - start_time < page.settings.resourceTimeout) {
                if (!end_time) {
                    return;
                }
                if (end_time > Date.now()) {
                    setTimeout(make_result, Date.now() - end_time, page);
                    return;
                }
            }

            var result = _make_result(page);
            page.close();
            finished = true;

            log("[" + result.status_code + "] " + result.orig_url + "[" + page.url + "] " + result.time);

            var body = JSON.stringify(result, null, 4);
            //log(body);

            response.writeHead(200, {
                'Cache': 'no-cache',
                'Content-Type': 'application/json'
            });

            //FIXME should consider the charset, default is utf-8
            response.write(body);
            response.closeGracefully();
        }

        function _make_result(page) {
            if (first_response === null) {
                console.debug('response is null, page=' + JSON.stringify(page, null, 4));
                return {
                    orig_url: fetch.url,
                    status_code: 599,
                    msg: 'No response received!',
                    error: 'No response received!',
                    content: '',
                    headers: {},
                    url: page.url,
                    cookies: {},
                    time: (Date.now() - start_time) / 1000
                }
            }

            var cookies = {};
            if (page.cookies) {
                page.cookies.forEach(function (e) {
                    cookies[e.name] = e.value;
                });
            }

            var headers = {};
            if (first_response.headers) {
                first_response.headers.forEach(function (e) {
                    headers[e.name] = e.value;
                });
            }

            console.debug('first_response: ' + JSON.stringify(first_response, null, 4));

            var url = page.url;
            if (!url) {
                url = fetch.url;
            }

            return {
                orig_url: fetch.url,
                status_code: first_response.status,
                msg: first_response.statusText,
                error: first_response.errorString,
                content: page.content,
                headers: headers,
                url: url,
                cookies: cookies,
                time: (Date.now() - start_time) / 1000
            }
        }
    });

    if (service) {
        log('Web server running on port ' + port);
    } else {
        log('Error: Could not create web server listening on port ' + port);
        phantom.exit();
    }
}
