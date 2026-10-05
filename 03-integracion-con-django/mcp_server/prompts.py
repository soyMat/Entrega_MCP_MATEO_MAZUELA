"""Prompts: flujos guiados reutilizables que el host puede invocar.

TRABAJO DEL ALUMNO: implementar el prompt de este módulo.
A diferencia de un resource (contexto legible) o una tool (acción que el
modelo decide ejecutar), un prompt empaqueta un flujo completo en mensajes
listos para el modelo: qué resources/tools usar y en qué orden.
No copia reglas de negocio: sólo orquesta las capacidades ya expuestas.
"""

from mcp.server import MCPServer


def register_prompts(mcp: MCPServer) -> None:
    @mcp.prompt(
        description="Guía al estudiante paso a paso: explorar, elegir e inscribirse en una actividad."
    )
    def guia_inscripcion(query: str = "", student_email: str = "") -> list[dict[str, object]]:
        """Flujo guiado de inscripción a actividades.

        Args:
            query: tema o palabra clave de interés (ej. "robótica").
                Vacío = mostrar todo el catálogo.
            student_email: correo del estudiante, si ya se conoce.
                Vacío = el modelo debe pedirlo antes de inscribir.
        """
        normalized_query = str(query or "").strip()
        normalized_email = str(student_email or "").strip()
        search_instruction = (
            f'Busca actividades relacionadas con "{normalized_query}".'
            if normalized_query
            else "Mostrame todas las actividades disponibles."
        )
        email_context = (
            f"El correo informado es `{normalized_email}`."
            if normalized_email
            else "Todavia no informe mi correo; pedimelo antes de inscribirme."
        )

        return [
            {
                "role": "user",
                "content": (
                    "Quiero encontrar una actividad y, si me convence, inscribirme. "
                    f"{search_instruction} {email_context}"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Guiame de manera clara y en este orden:\n"
                    "1. Lee el resource `activities://available` para mostrarme el catalogo.\n"
                    "2. Usa la tool `search_activities` con la busqueda indicada y "
                    "`only_available=True`.\n"
                    "3. Cuando elija una opcion, lee el resource "
                    "`activities://{activity_id}` y explicame su detalle.\n"
                    "4. Antes de cambiar datos, pedime una confirmacion explicita y, "
                    "si todavia falta, el correo. No interpretes la eleccion de una "
                    "actividad como permiso para inscribir.\n"
                    "5. Solo despues de mi confirmacion, usa la tool "
                    "`register_for_activity` con `activity_id` y `student_email`, y "
                    "comunica el resultado. Si falla, explica si no existe la actividad, "
                    "el correo es invalido, no hay cupo o ya estoy inscripto."
                ),
            },
        ]
