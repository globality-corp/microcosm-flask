# flake8: noqa
html = """
<!-- HTML for static distribution bundle build -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <!-- <link rel="stylesheet" type="text/css" href="./swagger-ui.css" /> -->
    <link rel="stylesheet" href="https://static.globality.com/swagger-ui/swagger-ui.min.css">
    <link rel="stylesheet" href="https://static.globality.com/swagger-ui/index.min.css">
    <link rel="icon" type="image/png" href="https://static.globality.com/swagger-ui/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="https://static.globality.com/swagger-ui/favicon-16x16.png" sizes="16x16" />
  </head>

  <body>
    <div id="swagger-ui"></div>
    <script
      src="https://static.globality.com/swagger-ui/swagger-ui-bundle.min.js"
      integrity="sha384-LcgLZWos2uaRMwKJ/GTaZG1YnVGGDfFZEi76GEE36zMizIyUqYnsraObUwMNmuc+"
      crossorigin="anonymous"
    ></script>
    <script
      src="https://static.globality.com/swagger-ui/swagger-ui-standalone-preset.min.js"
      integrity="sha384-ELu05sHa6F1QPgm+8BhV45gWSiSqaL2yiZqfzvdctJkUyihk0nKxkyZCFepBZhuP"
      crossorigin="anonymous"
    ></script>
    <script type="text/javascript">
      window.onload = function() {
        // Assumes swagger is located under this URL, without the `/docs`
        var swaggerLocation = window.location.href.replace("/docs", "");

        window.ui = SwaggerUIBundle({
          url: swaggerLocation,
          dom_id: '#swagger-ui',
          deepLinking: true,
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
          ],
          layout: "StandaloneLayout"
        });
      };
    </script>
  </body>
</html>
"""
