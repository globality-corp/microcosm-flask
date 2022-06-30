html = """
<!-- HTML for static distribution bundle build -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <!-- <link rel="stylesheet" type="text/css" href="./swagger-ui.css" /> -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.12.0/swagger-ui.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.12.0/index.min.css">
    <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.12.0/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.12.0/favicon-16x16.png" sizes="16x16" />
  </head>

  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.12.0/swagger-ui-bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.12.0/swagger-ui-standalone-preset.min.js"></script>
    <script type="text/javascript">
      window.onload = function() {
        // Swagger should be located under this URL, without the `/docs`
        var swaggerLocation = window.location.href.replace("/docs", "");
        console.log("Swagger location: " + swaggerLocation);

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
