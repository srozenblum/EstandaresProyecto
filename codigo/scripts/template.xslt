<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="html" indent="yes" encoding="utf-8"/>

    <!-- Plantilla principal -->
    <xsl:template match="/">
        <html>
        <head>
            <title>MongoDB Query Output</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                h1 { margin-bottom: 20px; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ccc; padding: 6px; vertical-align: top; }
                th { background-color: #f0f0f0; }
                .nested-table { margin: 5px; }
            </style>
            <script type="text/javascript">
            function toggleVisibility(id) {
              var el = document.getElementById(id);
              if (!el) return;
              if (el.style.display === 'none' || el.style.display === '') {
                el.style.display = 'block';
              } else {
                el.style.display = 'none';
              }
            }
            </script>
        </head>

        <body>
            <h1>Resultados de la consulta</h1>

            <table>
                <!-- cabecera: lee las claves del primer registro -->
                <tr>
                    <xsl:for-each select="root/element[1]/*">
                        <th><xsl:value-of select="name()"/></th>
                    </xsl:for-each>
                </tr>

                <!-- filas -->
                <xsl:for-each select="root/element">
                    <tr>
                        <xsl:for-each select="*">
                            <td>
                                <xsl:choose>

                                    <!-- Si es otro objeto -->
                                    <xsl:when test="@type='object'">
                                        <table class="nested-table">
                                            <xsl:for-each select="*">
                                                <tr>
                                                    <th><xsl:value-of select="name()"/></th>
                                                    <td>
                                                        <xsl:choose>
                                                            <!-- objeto dentro de objeto -->
                                                            <xsl:when test="@type='object'">
                                                                <xsl:call-template name="renderObject">
                                                                    <xsl:with-param name="node" select="."/>
                                                                </xsl:call-template>
                                                            </xsl:when>

                                                            <!-- lista dentro de objeto -->
                                                            <xsl:when test="@type='list'">
                                                                <xsl:call-template name="renderList">
                                                                    <xsl:with-param name="node" select="."/>
                                                                </xsl:call-template>
                                                            </xsl:when>

                                                            <!-- valor simple -->
                                                            <xsl:otherwise>
                                                                <xsl:value-of select="." />
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                </tr>
                                            </xsl:for-each>
                                        </table>
                                    </xsl:when>

                                    <!-- Si es una lista en el nivel superior -->
                                    <xsl:when test="@type='list'">
                                        <xsl:call-template name="renderList">
                                            <xsl:with-param name="node" select="."/>
                                        </xsl:call-template>
                                    </xsl:when>

                                    <!-- Si es un valor simple -->
                                    <xsl:otherwise>
                                        <xsl:value-of select="." />
                                    </xsl:otherwise>

                                </xsl:choose>
                            </td>
                        </xsl:for-each>
                    </tr>
                </xsl:for-each>

            </table>

        </body>
        </html>
    </xsl:template>


    <!-- PLANTILLA PARA OBJETOS -->
    <xsl:template name="renderObject">
        <xsl:param name="node"/>
        <table class="nested-table">
            <xsl:for-each select="$node/*">
                <tr>
                    <th><xsl:value-of select="name()"/></th>
                    <td>
                        <xsl:choose>
                            <!-- objeto anidado -->
                            <xsl:when test="@type='object'">
                                <xsl:call-template name="renderObject">
                                    <xsl:with-param name="node" select="."/>
                                </xsl:call-template>
                            </xsl:when>

                            <!-- lista anidada -->
                            <xsl:when test="@type='list'">
                                <xsl:call-template name="renderList">
                                    <xsl:with-param name="node" select="."/>
                                </xsl:call-template>
                            </xsl:when>

                            <!-- valor simple -->
                            <xsl:otherwise>
                                <xsl:value-of select="."/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>


    <!-- PLANTILLA PARA LISTAS -->
    <xsl:template name="renderList">
        <xsl:param name="node"/>

        <xsl:choose>

            <!-- CASO ESPECIAL: lista de variantes -->
            <xsl:when test="name($node) = 'variants'">
                <!-- ID único a partir del nodo -->
                <xsl:variable name="vid" select="concat('variants-', generate-id($node))"/>

                <!-- Resumen arriba -->
                <div>
                    <strong>
                        Variantes:
                        <xsl:value-of select="../variants_count"/>
                    </strong>
                    <button type="button"
                            onclick="toggleVisibility('{$vid}')"
                            style="margin-left:10px;">
                        Mostrar / Ocultar
                    </button>
                </div>

                <!-- Contenedor colapsable, oculto por defecto -->
                <div id="{$vid}" style="display:none; margin-top:8px;">
                    <table class="nested-table">
                        <xsl:for-each select="$node/element">
                            <tr>
                                <td>
                                    <xsl:call-template name="renderObject">
                                        <xsl:with-param name="node" select="."/>
                                    </xsl:call-template>
                                </td>
                            </tr>
                        </xsl:for-each>
                    </table>
                </div>
            </xsl:when>

            <!-- CASO GENÉRICO: lista de objetos -->
            <xsl:when test="$node/element/*">
                <table class="nested-table">
                    <xsl:for-each select="$node/element">
                        <tr>
                            <td>
                                <xsl:call-template name="renderObject">
                                    <xsl:with-param name="node" select="."/>
                                </xsl:call-template>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>
            </xsl:when>

            <!-- Lista de valores simples -->
            <xsl:otherwise>
                <ul>
                    <xsl:for-each select="$node/element">
                        <li><xsl:value-of select="."/></li>
                    </xsl:for-each>
                </ul>
            </xsl:otherwise>

        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
