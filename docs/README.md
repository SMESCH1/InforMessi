# Documentación - InforMessi

Índice de la documentación del proyecto.

---

## Guías de Uso

- **[Guía: Agregar Contenido](guia-agregar-contenido.md)** — cómo agregar eventos, media y noticias manuales
- **[Guía: Pre-Aprobación](guia-pre-aprobacion.md)** — flujo de edición y pre-aprobación de informes
- **[Guía: Pruebas de Flujos](guia-pruebas-flujos.md)** — cómo probar cada flujo del sistema
- **[Editar Informes](editar-informes.md)** — edición y validación de reportes

---

## Configuración

- **[Checklist de Configuración](checklist-configuracion.md)** — lista completa de pasos para dejar el sistema funcional
- **[Configuración de APIs](api-setup-guide.md)** — Groq, NewsAPI, Reddit, Telegram
- **[Instalar Ollama](install-ollama.md)** — configuración del LLM local
- **[Configuración de GitHub Actions](github-actions-setup.md)** — secrets, workflow y cron diario
- **[Configuración de Render (Webhook)](guia-render-setup.md)** — deploy del servidor webhook
- **[Configuración de Telegram](configuracion-telegram-dos-chats.md)** — dos chats (privado y público)
- **[Telegram Bot Setup](telegram-setup.md)** — crear y configurar el bot

---

## Referencia Técnica

- **[Arquitectura](architecture.md)** — diseño del sistema, stack y componentes
- **[Sistema de Memoria RAG](sistema-memoria-rag.md)** — memoria anti-repetición
- **[Formato de Eventos](formato-eventos.md)** — schema de `events.json`
- **[Secciones Semanales](secciones-semanales.md)** — temas por día de semana
- **[Guía Editorial](editorial-guide.md)** — identidad, tono y reglas de contenido
- **[Validación de Noticias](validacion-noticias.md)** — deduplicación y filtrado

---

## Integraciones

- **[Integración Reddit](reddit-integracion.md)** — configuración y subreddits
- **[Contenido Audiovisual](contenido-audiovisual.md)** — detección de media y formatos soportados
- **[Scraper de Eventos](scraper-eventos.md)** — generación de eventos históricos
- **[Prompt para Generar Eventos](prompt-generar-eventos.md)** — prompt para completar `events.json`

---

## Flujos y Aprobación

- **[Flujo Automático con Aprobación](flujo-automatico-aprobacion.md)** — cómo funciona el flujo asíncrono
- **[Guía de Pre-Aprobación](guia-pre-aprobacion.md)** — pre-aprobar informes antes del cron
- **[Guía Configurar Canal Telegram](guia-configurar-canal-telegram.md)** — setup del canal público

---

## Troubleshooting

- **[Troubleshooting Workflow](troubleshooting-workflow.md)** — problemas con GitHub Actions
- **[Solución de Problemas con APIs](solucion-problemas-apis.md)** — errores de APIs y fallbacks

---

Para empezar, lee el **[README principal](../README.md)** del proyecto.
