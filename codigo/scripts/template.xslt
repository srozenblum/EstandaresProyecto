<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="/">
    <html>
      <head>
        <title>Resultado Consulta</title>
        <style>
          body { font-family: Arial; background:#f5f5f5; padding:30px; }
          .card {
            background:white;
            margin-bottom:20px;
            padding:20px;
            border-radius:10px;
            border:1px solid #d9d9d9;
            box-shadow:0 2px 4px rgba(0,0,0,0.1);
            width:60%;
          }
          .field { margin-bottom:6px; }
          .key { font-weight:bold; color:#01579b; }
          .value { color:#222; }
          h1 { margin-bottom:20px; }
        </style>
      </head>
      <body>
        <h1>Resultado de la consulta</h1>
        <xsl:apply-templates select="root/item"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="item">
    <div class="card">
      <xsl:for-each select="*">
        <div class="field">
          <span class="key">
            <xsl:value-of select="name()"/>:
          </span>
          <span class="value">
            <xsl:value-of select="."/>
          </span>
        </div>
      </xsl:for-each>
    </div>
  </xsl:template>

</xsl:stylesheet>
