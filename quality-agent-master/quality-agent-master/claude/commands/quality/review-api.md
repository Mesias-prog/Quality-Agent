---
description: Revisa el contrato de API (OpenAPI) del proyecto: reglas de diseño, seguridad de endpoints y cambios que rompen compatibilidad.
argument-hint: <ruta-del-proyecto>
---

# /quality:review-api

Revisa la API del proyecto en **$ARGUMENTS** como complemento a `verify`.

Pasos:
1. Localiza la especificación OpenAPI (`*.yaml`/`*.yml`/`*.json`) bajo `$ARGUMENTS` o, si no
   existe, deriva los endpoints de los `@RestController` con Grep sobre `$ARGUMENTS/src/main`.
2. **Diseño**: nombres de recursos, verbos HTTP, códigos de estado, versionado,
   paginación y consistencia. Señala desviaciones contra las reglas del SKILL.
3. **Seguridad**: todo endpoint sensible debe exigir autenticación. Marca los que no.
4. **Compatibilidad**: si hay una versión previa del contrato, detecta cambios que
   rompen (campos eliminados, tipos cambiados, endpoints retirados).
5. Entrega un resumen con hallazgos citados (archivo:línea o ruta del endpoint) y, si
   corresponde, alimenta el bloque de seguridad de `quality-output/verification.json`.

> Esto complementa el gate; no lo reemplaza. El veredicto duro sigue saliendo de `verify`.
