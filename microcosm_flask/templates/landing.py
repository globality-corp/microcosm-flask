template = """
    <!doctype html>
    <html class="no-js" lang="">
        <head>
            <meta charset="utf-8">
            <meta http-equiv="x-ua-compatible" content="ie=edge">
            <title>{{ service_name | capitalize }}</title>
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
            }
            pre {
                background-color: #E8E8E8;
                border-style: solid;
                border-width: 1px;
            }
            .float-left {
                float: left;
            }
            .float-right {
                float: right;
            }
            .section {
                margin: 25px;
            }
            .section-health {
                padding-top: 25px;
                display: grid;
                grid-template-columns: 50% 50%;
            }
            .section-health > pre {
                height: 500px;
                overflow: scroll;
            }
            .text-center {
                text-align: center;
            }
            .no-margin {
                margin: 0px;
            }
            #env-button {
                margin: 5px 10px;
            }
        </style>
        <body>
            <h1 class="text-center">{{ service_name | capitalize }} - {{ version }}</h1>
            {%- if description -%}
            <h3 class="text-center">{{ description }}</h2>
            {%- endif -%}
            <div class="section section-health">
                <h2 class="no-margin"><a href="api/health">Health</a></h2>
                <div>
                    <h2 class="no-margin float-left"><a href="api/config">Config</a></h2>
                </div>
                <pre id="health">{{ health }}</pre>
                <pre id="config"><a id="env-button" class="float-right" href="data:text/plain;charset=utf-8,
                    {%- for item in env | sort -%}
                        {{ item | urlencode }}%0A
                    {%- endfor %}" download="{{ service_name }}_env"><button>Download Env</button></a>{{ config }}</pre>
            </div>
            {%- if homepage -%}
                <div class="section">
                    <h2><a href={{ homepage }}>Home Page</a></h2>
                </div>
            {%- endif -%}
            {%- if links -%}
            <div class="section">
                <h2>Links</h2>
                {%- for link in links | sort -%}
                <ul>
                    <li>
                        <a href="{{ links[link] }}">{{ link | replace("_", " ") | capitalize }}</a>
                    </li>
                </ul>
                {%- endfor -%}
            </div>
            {%- endif -%}
        </body>
    </html>
"""
