# Política de Privacidad — SniX Cloud

**Última actualización:** 19 de julio de 2026

> Resumen en una frase: **tus notas personales están cifradas de
> extremo a extremo y nadie más que tú puede leerlas — ni siquiera
> nosotros.**

## 1. Qué datos guardamos

| Dato | Dónde | Quién puede leerlo |
|---|---|---|
| Correo electrónico | Servidor (Supabase) | El desarrollador (para soporte) |
| Notas y snippets personales | Servidor, **cifrados de extremo a extremo** | **Solo tú.** El servidor solo ve texto cifrado |
| Notas, chats y archivos de grupo | Servidor, protegidos por permisos de acceso | Solo los miembros del grupo (y técnicamente el administrador del sistema) |
| Foto de perfil | Servidor (pública para tus compañeros de grupo) | Tus grupos |
| Tickets de soporte | Servidor | El desarrollador |
| Preferencias de la app | Solo en tu equipo | Solo tú |

## 2. Cómo funciona el cifrado

- Tus notas personales se cifran **en tu dispositivo** antes de subir,
  con una clave derivada de tu contraseña que nunca sale de tu equipo.
- En tu equipo, la base local también se guarda cifrada.
- Consecuencia honesta: si olvidas tu contraseña y no tienes un equipo
  con copia local, tus notas de la nube no pueden recuperarse.
- Las notas **de grupo** aún no usan cifrado de extremo a extremo (se
  protegen con permisos por usuario en el servidor); está previsto en
  una versión futura y esta política se actualizará.

## 3. Qué NO hacemos

- No vendemos ni compartimos tus datos con terceros.
- No mostramos publicidad.
- No usamos rastreadores ni analítica de comportamiento en la app.
- No leemos tu contenido (y el personal, además, no podríamos).

## 4. Proveedores

Usamos **Supabase** (base de datos y autenticación, servidores en la
nube) como infraestructura. GitHub aloja las descargas de la app.

## 5. Tus derechos

Puedes exportar tus datos desde la app (Ajustes → Respaldo) y puedes
pedir la eliminación completa de tu cuenta escribiendo al soporte.

## 6. Contacto

**mongeb@hotmail.es** (temporal, hasta activar el correo del dominio
propio) o la sección 🎧 Soporte dentro de la app.
