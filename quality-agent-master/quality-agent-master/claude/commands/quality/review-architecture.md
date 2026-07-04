---
description: Revisa decisiones de arquitectura y ADRs del proyecto: coherencia, capas, acoplamiento y registro de decisiones.
argument-hint: <ruta-del-proyecto>
---

# /quality:review-architecture

Revisa la arquitectura del proyecto en **$ARGUMENTS** como complemento a `verify`.

Pasos:
1. Localiza los ADRs (`$ARGUMENTS/docs/adr/`, `*.md`) y el código fuente principal.
2. **Capas y dependencias**: ¿se respeta la separación (controller → service →
   repository)? ¿Hay dependencias que apuntan en la dirección equivocada?
3. **Coherencia**: ¿las decisiones registradas en los ADRs se reflejan en el código?
   Señala las que se documentaron pero no se cumplen, y las que se hicieron sin ADR.
4. **Acoplamiento y complejidad**: marca clases/métodos con responsabilidad difusa o
   complejidad excesiva (usa Grep sobre `$ARGUMENTS/src` para localizar candidatos).
5. Entrega un resumen con hallazgos citados (archivo:línea, ADR).

> Esto pide criterio (modelo), no umbrales duros. No bloquea por sí solo; informa.
