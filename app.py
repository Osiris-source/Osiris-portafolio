import streamlit as st
import json
import os
from datetime import datetime

# ----- Configuración -----
st.set_page_config(page_title="Portafolio - Flavio", page_icon=":computer:", layout="centered")
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
INBOX_FILE = os.path.join(DATA_DIR, "inbox.json")
AVATAR_PATH = os.path.join(BASE_DIR, "static", "avatar.jpg")

# ----- Helpers para lectura/escritura -----
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(INBOX_FILE):
        with open(INBOX_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_projects():
    ensure_data_dir()
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_projects(projects):
    ensure_data_dir()
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def load_inbox():
    ensure_data_dir()
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_inbox(messages):
    ensure_data_dir()
    with open(INBOX_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def new_project_id(projects):
    if not projects:
        return 1
    return max(p.get("id", 0) for p in projects) + 1

# ----- Estado de sesión para edición -----
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ----- Barra lateral navegación -----
st.sidebar.title("Navegación")
page = st.sidebar.radio("", ["Inicio", "Proyectos", "Agregar proyecto", "Contacto", "Admin"])

# ----- Contenido de la app -----
def show_header():
    cols = st.columns([1, 3])
    if os.path.exists(AVATAR_PATH):
        with cols[0]:
            st.image(AVATAR_PATH, width=110)
    else:
        with cols[0]:
            st.write("")  # espacio si no hay avatar
    with cols[1]:
        st.markdown("## Flavio Osiris Becerra Hernandez")
        st.markdown("**Systems engineer • Backend developer • Mentor**")
        st.markdown("Tarapoto, Perú")
        st.markdown("---")

def page_inicio():
    show_header()
    st.header("Sobre mí")
    st.markdown(
        """
Soy bachiller en Ingeniería de Sistemas con experiencia en backend, integración de datos y mentoría.
Me apasiona construir soluciones simples y robustas para negocios locales y aprender nuevas tecnologías.
        """
    )
    st.header("Habilidades")
    skills = ["Python", "Flask", "Streamlit", "MySQL", "PostgreSQL", "JavaScript", "Docker", "Git", "SQL"]
    st.write(", ".join(skills))

def page_proyectos():
    show_header()
    st.header("Proyectos")
    projects = load_projects()
    if not projects:
        st.info("Aún no hay proyectos. Ve a Agregar proyecto para crear el primero.")
        return
    # mostrar tarjetas simples
    for p in sorted(projects, key=lambda x: x.get("id", 0), reverse=True):
        with st.container():
            st.subheader(p.get("title", "Sin título"))
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(p.get("description", ""))
                tech = p.get("tech", [])
                if tech:
                    st.markdown("**Tecnologías:** " + ", ".join(tech))
                link = p.get("link", "")
                if link:
                    st.markdown(f"[Ver proyecto]({link})")
            with cols[1]:
                if st.button("Ver detalle", key=f"view_{p['id']}"):
                    st.session_state.edit_id = p["id"]
                    st.experimental_rerun()
    # mostrar detalle si edit_id es un proyecto existente
    if st.session_state.edit_id:
        proj = next((x for x in projects if x.get("id") == st.session_state.edit_id), None)
        if proj:
            st.markdown("---")
            st.subheader("Detalle de proyecto")
            st.write("**Título:**", proj.get("title"))
            st.write("**Descripción:**", proj.get("description"))
            st.write("**Tecnologías:**", ", ".join(proj.get("tech", [])))
            if proj.get("link"):
                st.markdown(f"**Enlace:** [{proj.get('link')}]({proj.get('link')})")
            if st.button("Cerrar detalle"):
                st.session_state.edit_id = None
                st.experimental_rerun()

def page_add_project():
    show_header()
    st.header("Agregar o editar proyecto")
    projects = load_projects()
    edit_id = st.session_state.edit_id
    # valores por defecto para edición
    default = {"title": "", "description": "", "tech": "", "link": ""}
    if edit_id:
        p = next((x for x in projects if x.get("id") == edit_id), None)
        if p:
            default["title"] = p.get("title", "")
            default["description"] = p.get("description", "")
            default["tech"] = ", ".join(p.get("tech", []))
            default["link"] = p.get("link", "")
    with st.form("project_form"):
        title = st.text_input("Título", value=default["title"])
        description = st.text_area("Descripción", value=default["description"], height=150)
        tech = st.text_input("Tecnologías separadas por coma", value=default["tech"])
        link = st.text_input("Enlace opcional (URL)", value=default["link"])
        submitted = st.form_submit_button("Guardar proyecto")
    if submitted:
        tech_list = [t.strip() for t in tech.split(",") if t.strip()]
        if not title or not description:
            st.error("Título y descripción son obligatorios")
        else:
            if edit_id and any(x.get("id") == edit_id for x in projects):
                # editar
                for x in projects:
                    if x.get("id") == edit_id:
                        x["title"] = title
                        x["description"] = description
                        x["tech"] = tech_list
                        x["link"] = link or ""
                        x["updated_at"] = datetime.utcnow().isoformat()
                        break
                save_projects(projects)
                st.success("Proyecto actualizado")
                st.session_state.edit_id = None
            else:
                # nuevo
                new_id = new_project_id(projects)
                new_proj = {
                    "id": new_id,
                    "title": title,
                    "description": description,
                    "tech": tech_list,
                    "link": link or "",
                    "created_at": datetime.utcnow().isoformat()
                }
                projects.append(new_proj)
                save_projects(projects)
                st.success("Proyecto agregado")

def page_contact():
    show_header()
    st.header("Contacto")
    st.write("Déjame un mensaje y lo guardaré para que puedas revisarlo luego.")
    with st.form("contact_form"):
        name = st.text_input("Nombre")
        email = st.text_input("Email")
        message = st.text_area("Mensaje", height=150)
        sent = st.form_submit_button("Enviar mensaje")
    if sent:
        if not name or not email or not message:
            st.error("Completa todos los campos")
        else:
            inbox = load_inbox()
            inbox.append({
                "name": name,
                "email": email,
                "message": message,
                "received_at": datetime.utcnow().isoformat()
            })
            save_inbox(inbox)
            st.success("Mensaje guardado. Gracias por escribir.")

def page_admin():
    show_header()
    st.header("Admin panel")
    projects = load_projects()
    inbox = load_inbox()
    st.subheader("Proyectos existentes")
    if projects:
        for p in sorted(projects, key=lambda x: x.get("id", 0), reverse=True):
            cols = st.columns([4,1,1])
            with cols[0]:
                st.write(f"**{p.get('title')}**  \nTecnologías: {', '.join(p.get('tech', []))}")
            with cols[1]:
                if st.button("Editar", key=f"edit_{p['id']}"):
                    st.session_state.edit_id = p["id"]
                    st.experimental_rerun()
            with cols[2]:
                if st.button("Eliminar", key=f"del_{p['id']}"):
                    projects = [x for x in projects if x.get("id") != p["id"]]
                    save_projects(projects)
                    st.success("Proyecto eliminado")
                    st.experimental_rerun()
    else:
        st.info("No hay proyectos")

    st.markdown("---")
    st.subheader("Bandeja de mensajes")
    if inbox:
        for msg in sorted(inbox, key=lambda x: x.get("received_at", ""), reverse=True):
            st.write(f"**{msg.get('name')}**  •  {msg.get('email')}  •  {msg.get('received_at')}")
            st.write(msg.get("message"))
            st.markdown("---")
        if st.button("Vaciar bandeja"):
            save_inbox([])
            st.success("Bandeja vaciada")
            st.experimental_rerun()
    else:
        st.info("No hay mensajes")

# ----- Rutas según la selección -----
if page == "Inicio":
    page_inicio()
elif page == "Proyectos":
    page_proyectos()
elif page == "Agregar proyecto":
    page_add_project()
elif page == "Contacto":
    page_contact()
elif page == "Admin":
    page_admin()