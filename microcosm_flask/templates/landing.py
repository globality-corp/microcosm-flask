template = """
    <!doctype html>
    <html class="no-js" lang="">
        <head>
            <meta charset="utf-8">
            <meta http-equiv="x-ua-compatible" content="ie=edge">
            <title>{{ service_name }}</title>
            <meta name="description" content="Landing">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700" rel="stylesheet">
        </head>
        <style>
            html {
                font-family: sans-serif;
                -ms-text-size-adjust: 100%;
                -webkit-text-size-adjust: 100%;
                font-size: 10px;
                -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
            }
            body {
                margin: 0;
                font-family: "Open Sans", sans-serif;
                font-size: 14px;
                line-height: 1.42857143;
                color: #333333;
                background-color: #fff;
            }
            a {
                background-color: transparent;
                color: #337ab7;
                text-decoration: none;
            }

            h1 {
                font-weight: 500;
                line-height: 1.1;
                color: inherit;
                text-align: center;
                padding-top: 2%;
                padding-bottom: 2%;
                text-transform: capitalize;
            }
            h3 {
                text-align: center;
            }
            pre {
                background-color: #E8E8E8;
                border-style: solid;
                border-width: 1px;
            }
            .section {
                margin: 0 100px;
            }
        </style>
        <body>
            <h1>{{ service_name }}</h1>
            <h3>{{ version }}</h3>
            {%-if description -%}
                <div class="section">
                    <h2>Description</h2>
                    <p>{{ description }}</p>
                </div>
            {%- endif -%}
            <div class="section">
                <h2><a href="api/health">Health</a></h2>
                <pre id=health></pre>
            </div>
            {%- for swagger_version in swagger_versions -%}
                <div class="section">
                    <h2><a href="api/{{ swagger_version }}/swagger">Swagger ({{ swagger_version }})</a></h2>
                </div>
            {%- endfor -%}
            {%-if homepage -%}
                <div class="section">
                    <h2><a href={{ homepage }}>Home Page</a></h2>
                </div>
            {%- endif -%}
            <div class="section">
                <h2><a href="api/config">Config</a></h2>
                <pre id=config></pre>
            </div>
            <script>
                processRequest('/api/config', configReqListener);
                processRequest('/api/health', healthReqListener);

                function processRequest(uri, reqListener) {
                    var req = new XMLHttpRequest();
                    req.onload = reqListener;
                    req.onerror = reqError;
                    req.open('get', uri, true);
                    req.send();
                }

                function configReqListener() {
                    var data = JSON.parse(this.responseText);
                    document.getElementById("config").innerHTML = objectToString(data);
                }

                function healthReqListener() {
                    var data = JSON.parse(this.responseText);
                    document.getElementById("health").innerText = objectToString(data);
                }

                function objectToString(object) {
                    return JSON.stringify(object, null, 2)
                }

                function reqError(err) {
                    console.log('Fetch Error :-S', err);
                }
        </script>
        </body>
    </html>
"""