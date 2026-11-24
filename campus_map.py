"""Interactive UTAS Salalah campus map: click a numbered marker (or use the list) to choose a place."""
import os
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import config
from i18n import t, lang

IMG = Image.open(os.path.join(config.BASE, "assets", "campus_map.png")).convert("RGB")
W, H = IMG.size


def _label(n):
    en, ar, _ = config.PLACES[n]
    return f"{n} - {ar if lang() == 'ar' else en}"


def is_mobile():
    try:
        ua = st.context.headers.get("User-Agent", "")
    except Exception:
        return False
    return any(k in ua for k in ("Mobi", "Android", "iPhone", "iPad"))


def _fig(selected=None, height=340, width=None, zoom=False):
    xs, ys, cd, txt = [], [], [], []
    for n, (en, ar, pts) in config.PLACES.items():
        for x, y in pts:
            xs.append(x); ys.append(y); cd.append(n); txt.append(_label(n))
    fig = go.Figure()
    # invisible but clickable hit targets over every numbered circle of the map
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", customdata=cd, text=txt, hovertemplate="%{text}<extra></extra>",
                             marker=dict(size=22, color="rgba(19,49,127,0.08)", line=dict(width=0)),
                             selected=dict(marker=dict(color="rgba(244,123,32,0.0)")),
                             unselected=dict(marker=dict(opacity=1)), showlegend=False))
    if selected in config.PLACES:
        pts = config.PLACES[selected][2]
        fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="markers", hoverinfo="skip",
                                 marker=dict(size=26, color="rgba(244,123,32,0.25)", line=dict(width=3, color="#f47b20")),
                                 showlegend=False))
    fig.update_layout(images=[dict(source=IMG, xref="x", yref="y", x=0, y=0, sizex=W, sizey=H, sizing="stretch",
                                   xanchor="left", yanchor="top", layer="below")],
                      xaxis=dict(range=[0, W], visible=False, fixedrange=not zoom),
                      yaxis=dict(range=[H, 0], visible=False, fixedrange=not zoom, scaleanchor="x"),
                      margin=dict(l=0, r=0, t=0, b=0), height=height, width=width, hoverlabel=dict(font_size=13),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def _sync_loc():
    """Auto-fill the 'Location / Department' text with the chosen place (unless the user typed something else)."""
    n = st.session_state.get("place_sel")
    new = (config.PLACES[n][1] if lang() == "ar" else config.PLACES[n][0]) if n in config.PLACES else ""
    cur = st.session_state.get("loc_dept", "")
    if not cur or cur == st.session_state.get("_loc_auto", ""):
        st.session_state["loc_dept"] = new
        st.session_state["_loc_auto"] = new


def is_auto_text(txt):
    n = st.session_state.get("place_sel")
    return n in config.PLACES and txt.strip() in (config.PLACES[n][0], config.PLACES[n][1])


def _picked():
    key = f"campusmap{st.session_state.get('map_ver', 0)}"
    sel = st.session_state.get(key)
    try:
        pts = sel["selection"]["points"]
    except Exception:
        pts = []
    if pts:
        n = pts[-1].get("customdata")
        n = n[0] if isinstance(n, (list, tuple)) else n
        if n in config.PLACES:
            st.session_state["place_sel"] = int(n)
            _sync_loc()
    st.session_state["map_ver"] = st.session_state.get("map_ver", 0) + 1   # reset chart selection state


def _list_changed():
    _sync_loc()
    st.session_state["map_ver"] = st.session_state.get("map_ver", 0) + 1


def _clear():
    st.session_state["place_sel"] = None
    _sync_loc()
    st.session_state["map_ver"] = st.session_state.get("map_ver", 0) + 1


def picker():
    """Renders the map + list; returns the chosen place number or None. State lives in st.session_state['place_sel']."""
    st.markdown(f"**{t('map_title')}**")
    st.caption(t("map_hint"))
    if st.session_state.pop("_reset_place", False):
        st.session_state["place_sel"] = None
        st.session_state["loc_dept"] = ""
        st.session_state["_loc_auto"] = ""
    st.session_state.setdefault("place_sel", None)
    sel = st.session_state["place_sel"]
    with st.container(key="mapbox"):
        mob = is_mobile()
        cfg = {"displayModeBar": mob, "displaylogo": False, "scrollZoom": False,
               "modeBarButtons": [["zoomIn2d", "zoomOut2d", "resetScale2d"]]}
        st.plotly_chart(_fig(sel, 250, None, zoom=True) if mob else _fig(sel), key=f"campusmap{st.session_state.get('map_ver', 0)}",
                        on_select=_picked, selection_mode="points", config=cfg, width="stretch")
    if mob:
        st.caption(t("map_scroll"))
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    c1.selectbox(t("map_list"), [None] + list(config.PLACES), key="place_sel", on_change=_list_changed,
                 format_func=lambda n: t("map_none") if n is None else _label(n))
    c2.button(t("map_clear"), on_click=_clear, disabled=sel is None, width="stretch")
    return st.session_state["place_sel"]


def show(name):
    """Read-only map with one building highlighted (admin / responsible detail)."""
    n = config.PLACE_BY_EN.get(name)
    if n is None:
        return
    st.plotly_chart(_fig(n, 230), key=f"map_show_{n}_{id(name)}", config={"displayModeBar": False, "staticPlot": True}, width="stretch")
    st.caption(_label(n))
