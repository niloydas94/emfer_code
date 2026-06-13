import os
import uuid

import streamlit as st
from posthog import Posthog


VISITOR_COOKIE_NAME = "emfer_visitor_id"


def initialize_analytics(cookies=None):
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "visitor_id" in st.session_state:
        return

    visitor_id = None
    visitor_id_source = "session_fallback"

    if cookies is not None and cookies.ready():
        visitor_id = cookies.get(VISITOR_COOKIE_NAME)

        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            cookies[VISITOR_COOKIE_NAME] = visitor_id
            cookies.save()

        visitor_id_source = "cookie"

    if not visitor_id:
        visitor_id = str(uuid.uuid4())

    st.session_state.visitor_id = visitor_id
    st.session_state.visitor_id_source = visitor_id_source


def get_visitor_id():
    if "visitor_id" not in st.session_state:
        initialize_analytics()

    return st.session_state.visitor_id


def get_session_id():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    return st.session_state.session_id


def get_visitor_id_source():
    if "visitor_id_source" not in st.session_state:
        initialize_analytics()

    return st.session_state.visitor_id_source


def format_funds_for_analytics(funds):
    return " || ".join(funds)


@st.cache_resource
def get_posthog_client():
    api_key = os.getenv("POSTHOG_API_KEY") or st.secrets.get("POSTHOG_API_KEY", None)
    host = os.getenv("POSTHOG_HOST") or st.secrets.get("POSTHOG_HOST", None)

    if not api_key or not host:
        return None

    return Posthog(
        project_api_key=api_key,
        host=host
    )


def track_event(event_name, properties=None):
    client = get_posthog_client()

    if client is None:
        return

    try:
        event_properties = properties or {}
        event_properties["visitor_id"] = get_visitor_id()
        event_properties["visitor_id_source"] = get_visitor_id_source()
        event_properties["session_id"] = get_session_id()

        client.capture(
            distinct_id=get_visitor_id(),
            event=event_name,
            properties=event_properties
        )
    except Exception:
        return
