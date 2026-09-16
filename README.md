# devboard-web
Django front door for the DevBoard microservices - the only service the browser talks to. Renders HTML by calling the other six services server-side (auth, core, work, analytics, attachments, integrations). No API or database of its own; Redis-backed sessions, async views + httpx for backend calls.
