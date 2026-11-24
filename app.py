import os, io, uuid, datetime as dt
import streamlit as st
import pandas as pd
from sqlalchemy import select
import config, db, ai, level_model, campus_map
from db import Session, Report, Update, User
from i18n import t, v, cat_name, sub_name, dept_name, lang

st.set_page_config(page_title="UTAS Risk Management", page_icon="🛡️", layout="wide")
db.init_db()

NAVY, ORANGE = "#13317f", "#f47b20"
LEVEL_COLOR = {"Low": "#2e8b57", "Medium": "#e0a800", "High": "#e8710a", "Critical": "#c62828"}
CHIP = {"New": ("#e3f0ff", "#1a5fb4"), "Sent to Responsible": ("#dbe9ff", "#13317f"), "In Progress": ("#ffe9d6", "#c25e00"),
        "Done": ("#dff5e3", "#1e7a34"), "Closed": ("#e6e8ec", "#444"), "Returned": ("#fde2e1", "#b3261e")}
STEP = {"New": 1, "Returned": 1, "Sent to Responsible": 2, "In Progress": 3, "Done": 3, "Closed": 4}
LOGO = os.path.join(config.BASE, "assets", "utas_logo.png")


def css():
    rtl = lang() == "ar"
    st.markdown(f"""<style>
    header[data-testid="stHeader"] {{display:none}}
    .block-container {{padding:6.4rem 2rem 2rem 2rem; max-width:100%}}
    [data-testid="stAppViewContainer"] {{background:#f3f6fb}}
    .st-key-topbar {{position:fixed; top:0; left:0; right:0; z-index:1000; background:{NAVY}; margin:0; padding:.6rem 2rem; color:#fff; align-items:center; box-shadow:0 2px 6px rgba(0,0,0,.2)}}
    [data-testid="stSidebar"] {{top:4.4rem; height:calc(100vh - 4.4rem)}}
    .st-key-topbar * {{color:#fff}}
    .st-key-topbar .stButton button {{background:{ORANGE}; border:none; color:#fff; font-weight:600}}
    .st-key-topbar [data-testid="stRadio"] label p {{color:#fff; font-size:.9rem}}
    .brand-logo {{font-size:2rem; font-weight:800; letter-spacing:1px; display:inline-block; margin-{'left' if rtl else 'right'}:14px; vertical-align:middle}}
    .brand-txt {{display:inline-block; vertical-align:middle; line-height:1.25}}
    .brand-txt b {{font-size:1.05rem}} .brand-txt span {{font-size:.8rem; opacity:.95}}
    {'html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .block-container {direction: rtl; text-align: right;}' if rtl else ''}
    [data-testid="stSidebar"] {{background:#f3f6fb; border-right:none}}
    [data-testid="stSidebarNavLink"] {{border-radius:8px; padding:.7rem 1rem; font-weight:600; margin-bottom:6px}}
    [data-testid="stSidebarNavLink"][aria-current="page"] {{background:{NAVY}; border-left:5px solid {ORANGE}}}
    [data-testid="stSidebarNavLink"][aria-current="page"] span {{color:#fff !important}}
    .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {{background:{ORANGE}; border-color:{ORANGE}; color:#fff; font-weight:600}}
    h1,h2,h3 {{color:#111}}
    .pill {{display:inline-block;padding:2px 12px;border-radius:12px;color:#fff;font-weight:600;font-size:.85rem}}
    .chip {{display:inline-block;padding:3px 14px;border-radius:14px;font-weight:600;font-size:.82rem}}
    .alert {{border-left:5px solid #c62828;background:#fdecea;padding:10px 14px;border-radius:6px;margin:8px 0;color:#611a15}}
    .demo {{background:#fff4e5;border:1px solid #ffb74d;padding:6px 12px;border-radius:8px;font-size:.85rem;color:#5d4037;margin-bottom:.6rem}}
    .lbl {{font-weight:700; font-size:.85rem; margin-top:.5rem}} .val {{font-size:.9rem; color:#333}}
    .stepper {{display:flex; justify-content:space-between; margin:14px 0}}
    .stepper div {{text-align:center; font-size:.78rem; flex:1}}
    .stepper i {{display:flex; width:30px; height:30px; border-radius:50%; margin:0 auto 4px; align-items:center; justify-content:center; font-style:normal; font-weight:700; border:2px solid {NAVY}}}
    .stepper .on i {{background:{NAVY}; color:#fff}}
    @media (max-width: 760px) {{
      header[data-testid="stHeader"] {{display:flex !important; position:fixed; top:0; left:0; right:0; height:2.75rem; background:#f3f6fb; z-index:1001}}
      .block-container {{padding:3.2rem .8rem 1.5rem .8rem}}
      .st-key-topbar {{position:static; padding:.5rem .8rem; border-radius:10px; margin-bottom:.8rem}}
      .st-key-topbar [data-testid="stHorizontalBlock"] {{flex-wrap:wrap !important; gap:.4rem .6rem !important}}
      .st-key-topbar [data-testid="stColumn"] {{min-width:0 !important; width:auto !important; flex:0 1 auto !important}}
      .st-key-topbar [data-testid="stColumn"]:first-child {{flex:1 1 100% !important; width:100% !important}}
      .brand-logo {{font-size:1.5rem; margin-{'left' if rtl else 'right'}:10px}}
      .brand-txt b {{font-size:.95rem}} .brand-txt span {{display:none}}
      [data-testid="stSidebar"] {{top:0; height:100vh; direction:ltr !important}}
      [data-testid="stSidebar"][data-collapsed="true"] {{display:none !important}}
      [data-testid="stSidebarResizeHandle"] {{display:none}}
      [data-testid="stSidebarContent"] {{direction:{'rtl' if rtl else 'ltr'}}}
      [data-testid="stHorizontalBlock"] {{flex-wrap:wrap}}
      [data-testid="stColumn"] {{min-width:100% !important}}
      .stepper div {{font-size:.68rem}}
      h1 {{font-size:1.6rem !important}}
    }}
    </style>""", unsafe_allow_html=True)


def chip(status):
    bg, fg = CHIP.get(status, ("#eee", "#333"))
    return f'<span class="chip" style="background:{bg};color:{fg}">{v(status)}</span>'


def pill(level):
    return f'<span class="pill" style="background:{LEVEL_COLOR.get(level, "#777")}">{v(level)}</span>'


def stepper(status):
    n = STEP.get(status, 1)
    names = [t("step1"), t("step2"), t("step3"), t("step4")]
    return '<div class="stepper">' + "".join(
        f'<div class="{"on" if i + 1 <= n else ""}"><i>{i + 1}</i>{names[i]}</div>' for i in range(4)) + "</div>"


def user():
    return st.session_state.get("user")


def topbar():
    u = user()
    with st.container(key="topbar", horizontal=False):
        c1, c2, c3, c4 = st.columns([5, 1.4, 2.2, 1], vertical_alignment="center")
        c1.markdown(f'<span class="brand-logo">UTAS</span><span class="brand-txt"><b>{t("sys_name")}</b><br>'
                    f'<span>{t("org")}</span></span>', unsafe_allow_html=True)
        pick = c2.radio("lang", ["EN", "عربي"], horizontal=True, label_visibility="collapsed",
                        index=0 if lang() == "en" else 1)
        newl = "ar" if pick == "عربي" else "en"
        if newl != lang():
            st.session_state["lang"] = newl
            st.rerun()
        if u:
            c3.markdown(f"**{u['name']}**")
            if c4.button(t("logout"), key="logout"):
                st.session_state.pop("user", None)
                st.session_state.pop("guest", None)
                st.rerun()
        elif st.session_state.get("guest"):
            c3.markdown(f"**{t('role_visitor')}**")
            if c4.button(t("back_login"), key="tologin"):
                st.session_state.pop("guest", None)
                st.rerun()


def demo_banner():
    st.markdown(f'<div class="demo">{t("demo_banner")}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ helpers
def loc_text(r):
    return (r.room + " - " if r.room else "") + f"{v(r.building)}"


def by_text(r, users):
    if r.reporter_user_id and r.reporter_user_id in users:
        return users[r.reporter_user_id].full_name
    return r.reporter_name or v("Visitor")


def load_users():
    with Session() as s:
        return {x.id: x for x in s.scalars(select(User))}


def mine(u):
    """Reports a Responsible Person can see: assigned to them, or routed to their department and not yet assigned."""
    from sqlalchemy import or_, and_
    return or_(Report.assigned_to == u["id"], and_(Report.assigned_to.is_(None), Report.department == u["dept"]))


def img_path(r):
    p = r.photo_path and os.path.join(config.UPLOAD_DIR, r.photo_path)
    return p if p and os.path.exists(p) else None


def table(rows, users, key):
    df = pd.DataFrame([{t("tbl_id"): r.code, t("tbl_title"): r.title or r.description[:40],
                        t("tbl_type"): cat_name(r.category or r.ai_category).split(" - ")[-1],
                        t("tbl_loc"): loc_text(r), t("tbl_by"): by_text(r, users),
                        t("tbl_date"): r.created_at.strftime("%d %b %Y"), t("tbl_status"): v(r.status)} for r in rows])
    ev = st.dataframe(df, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row", key=key)
    st.caption(t("showing", n=len(rows)))
    idx = ev.selection.rows
    return rows[idx[0]] if idx else None


# ------------------------------------------------------------------ pages
def page_login():
    topbar()
    c1, c2 = st.columns([1.1, 1], vertical_alignment="center")
    with c1:
        if os.path.exists(LOGO):
            st.image(LOGO, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.subheader(t("login"))
            with st.form("login", border=False):
                un = st.text_input(t("user_email"))
                pw = st.text_input(t("password"), type="password")
                role = st.selectbox(t("role"), ["user", "admin", "responsible"],
                                    format_func=lambda x: {"user": t("role_user"), "admin": t("role_adminx"), "responsible": t("role_resp")}[x])
                go = st.form_submit_button(t("login"), type="primary", use_container_width=True)
            if go:
                u = db.authenticate(un, pw)
                if not u:
                    st.error(t("bad_login"))
                elif u.role != role:
                    st.error(t("role_mismatch"))
                else:
                    st.session_state["user"] = {"id": u.id, "name": u.full_name, "role": u.role, "dept": u.department}
                    st.rerun()
            if st.button(t("forgot"), type="tertiary"):
                st.info(t("forgot_msg"))
            if st.button(t("visitor_btn"), use_container_width=True):
                st.session_state["guest"] = True
                st.rerun()
    st.caption(f"Demo: user1/user123 · admin/admin123 · elec/resp123")
    demo_banner()


def page_report():
    topbar()
    u = user()
    users = load_users()
    st.title(t("p_report"))
    left, right = st.columns([3, 1])
    with left, st.container(border=True):
        st.markdown(f'<div class="alert">{t("emergency")}</div>', unsafe_allow_html=True)
        place_no = campus_map.picker()
        building = config.PLACES[place_no][0] if place_no else config.NOT_SPECIFIED
        with st.form("report_form", clear_on_submit=False):
            title = st.text_input(t("risk_title"))
            rtype = st.selectbox(t("risk_type"), [None] + list(config.CATEGORIES),
                                 format_func=lambda x: t("select_type") if x is None else cat_name(x))
            room = st.text_input(t("loc_dept"), key="loc_dept")
            d1, d2 = st.columns(2)
            day = d1.date_input(t("date_time"), value=dt.date.today())
            tm = d2.time_input(" ", value=dt.datetime.now().time(), label_visibility="hidden")
            desc = st.text_area(t("risk_desc"), height=120, help=t("desc_help"))
            st.caption(t("privacy_note"))
            photo = st.file_uploader(t("attach_img"), type=["png", "jpg", "jpeg"])
            with st.expander(t("more_details")):
                c2, c3 = st.columns(2)
                floor = c2.selectbox(t("floor"), config.FLOORS, format_func=v)
                loc = c3.selectbox(t("location_type"), config.LOCATION_TYPES, format_func=v)
                c1, c2 = st.columns(2)
                people = c1.selectbox(t("people"), config.PEOPLE_BANDS, index=5, format_func=v)
                freq = c2.selectbox(t("frequency"), config.FREQUENCIES, index=4, format_func=v)
                c1, c2, c3 = st.columns(3)
                injury = c1.selectbox(t("injury"), config.YES_NO_UNKNOWN, index=1, format_func=v)
                imm = c2.selectbox(t("immediate"), config.YES_NO_UNKNOWN, index=1, format_func=v)
                urg = c3.selectbox(t("urgency"), config.URGENCY, format_func=v)
                c1, c2 = st.columns(2)
                controls = c1.selectbox(t("controls"), config.YES_NO_UNKNOWN, index=2, format_func=v)
                damage = c2.selectbox(t("damage"), config.YES_NO_UNKNOWN, index=2, format_func=v)
                c1, c2 = st.columns(2)
                rl = c1.selectbox(t("rep_L"), [None, 1, 2, 3, 4, 5], format_func=lambda x: t("not_sure") if x is None else f"{x} - {config.LIKELIHOOD_LABELS[x]}")
                rs = c2.selectbox(t("rep_S"), [None, 1, 2, 3, 4, 5], format_func=lambda x: t("not_sure") if x is None else f"{x} - {config.SEVERITY_LABELS[x]}")
                if not u:
                    c1, c2 = st.columns(2)
                    rname = c1.text_input(t("reporter_name"))
                    contact = c2.text_input(t("reporter_contact"))
                else:
                    rname = contact = ""
            b1, b2, _ = st.columns([1.2, 1, 3])
            ok = b1.form_submit_button(t("submit_report"), type="primary")
            b2.form_submit_button(t("cancel"))
        if ok:
            if not title.strip():
                st.error(t("need_title")); return
            if len(desc.strip()) < 15:
                st.error(t("need_desc")); return
            path = None
            if photo is not None:
                path = f"{uuid.uuid4().hex}{os.path.splitext(photo.name)[1].lower()}"
                with open(os.path.join(config.UPLOAD_DIR, path), "wb") as f:
                    f.write(photo.getbuffer())
            sug = ai.suggest(f"{title}. {desc}", urgency=urg, injury=injury, immediate=imm, people=people, frequency=freq)
            if rtype:   # reporter's own choice is kept as the starting category
                sug["category"] = rtype
            lm = level_model.predict({"building": building, "floor": floor, "location_type": loc, "category": sug["category"],
                                      "subtype": sug["subtype"], "people": people, "frequency": freq, "controls": controls,
                                      "damage": damage, "hazard": imm, "urgency": urg, "likelihood": rl, "severity": rs,
                                      "text": f"{title}. {desc}"})
            with Session() as s:
                r = Report(code=db.next_code(s), title=title.strip(), likelihood_reported=rl, severity_reported=rs,
                           lvl_model_pred=lm[0] if lm else None, lvl_model_conf=lm[1] if lm else None, reporter_user_id=u["id"] if u else None,
                           created_at=dt.datetime.combine(day, tm), reporter_type="Staff" if u else "Visitor",
                           reporter_name=rname or None, reporter_contact=contact or None, building=building, floor=floor,
                           location_type=loc, room=(None if (not room.strip() or campus_map.is_auto_text(room)) else room.strip()), description=desc.strip(), people_exposed=people, frequency=freq,
                           injury_occurred=injury, immediate_hazard=imm, existing_controls=controls, visible_damage=damage,
                           urgency=urg, photo_path=path, ai_category=sug["category"], ai_subtype=sug["subtype"],
                           ai_level=sug["level"], ai_likelihood=sug["likelihood"], ai_severity=sug["severity"],
                           ai_confidence=sug["confidence"], ai_source=sug["source"], ai_reason=sug["reason"])
                s.add(r)
                s.commit()
                code = r.code
            st.session_state["_reset_place"] = True
            st.success(f"{t('submitted')} **{code}**")
            st.info(t("keep_code"))
    with right, st.container(border=True):
        st.subheader(t("recent"))
        if u:
            with Session() as s:
                rows = list(s.scalars(select(Report).where(Report.reporter_user_id == u["id"]).order_by(Report.created_at.desc()).limit(5)))
            for r in rows:
                st.markdown(f"**{r.title or r.description[:40]}**<br>{chip(r.status)}", unsafe_allow_html=True)
                st.write("")
            if not rows:
                st.caption(t("no_reports"))
        else:
            st.caption(t("recent_guest"))
    demo_banner()


def page_track():
    topbar()
    st.title(t("track_title"))
    code = st.text_input(t("code"), placeholder="RPT-2026-0001").strip().upper()
    if code:
        with Session() as s:
            r = s.scalar(select(Report).where(Report.code == code))
            if not r:
                st.warning(t("not_found")); return
            st.markdown(f"{chip(r.status)} &nbsp; **{t('created')}:** {r.created_at:%Y-%m-%d %H:%M}", unsafe_allow_html=True)
            st.markdown(stepper(r.status), unsafe_allow_html=True)
            st.write(f"**{r.title or ''}**")
            st.write(r.description)
            if r.status == "Returned" and r.admin_note:
                st.warning(f"{t('returned_msg')} {r.admin_note}")
            for up in r.updates:
                st.markdown(f"- {up.created_at:%Y-%m-%d %H:%M} · {v(up.status)} {up.note if up.user_name and up.status == 'Returned' else ''}")


def page_myreports():
    topbar()
    u = user()
    users = load_users()
    st.title(t("p_myreports"))
    with Session() as s:
        rows = list(s.scalars(select(Report).where(Report.reporter_user_id == u["id"]).order_by(Report.created_at.desc())))
    if not rows:
        st.info(t("no_reports")); return
    sel = table(rows, users, "myrep")
    if sel:
        with st.container(border=True):
            st.subheader(sel.title or sel.code)
            st.markdown(chip(sel.status) + stepper(sel.status), unsafe_allow_html=True)
            st.write(sel.description)
            if sel.status == "Returned" and sel.admin_note:
                st.warning(f"{t('returned_msg')} {sel.admin_note}")
            if img_path(sel):
                st.image(img_path(sel), width=300)
    else:
        st.caption(t("pick_row"))


def page_reports():
    topbar()
    u = user()
    users = load_users()
    st.title(t("p_reports"))
    with Session() as s:
        rows = list(s.scalars(select(Report).order_by(Report.created_at.desc())))
    c1, c2 = st.columns([1.25, 1.3])
    with c1, st.container(border=True):
        f1, f2 = st.columns(2)
        fs = f1.selectbox(t("filter_status"), [None] + config.STATUSES, format_func=lambda x: t("all") if x is None else v(x))
        fc = f2.selectbox(t("filter_cat"), [None] + list(config.CATEGORIES), format_func=lambda x: t("all") if x is None else cat_name(x))
        rows = [r for r in rows if (not fs or r.status == fs) and (not fc or (r.category or r.ai_category) == fc)]
        sel = table(rows, users, "adm_tbl") if rows else None
        if not rows:
            st.info(t("no_reports"))
    with c2, st.container(border=True):
        if sel is None:
            st.subheader(t("rep_details")); st.caption(t("pick_row"))
        else:
            detail_admin(sel, u, users)
    demo_banner()


def kv(label, val):
    st.markdown(f'<div class="lbl">{label}</div><div class="val">{val}</div>', unsafe_allow_html=True)


def detail_admin(r, u, users):
    k = r.id
    a, b = st.columns(2)
    with a:
        st.subheader(t("rep_details"))
        kv(t("tbl_title"), r.title or "-"); kv(t("rep_desc"), r.description)
        kv(t("tbl_type"), cat_name(r.category or r.ai_category)); kv(t("tbl_loc"), loc_text(r))
        kv(t("tbl_by"), by_text(r, users)); kv(t("tbl_date"), r.created_at.strftime("%d %b %Y"))
        kv(t("tbl_status"), chip(r.status))
    with b:
        st.subheader(t("img_prev"))
        if img_path(r):
            st.image(img_path(r), use_container_width=True)
        else:
            st.caption(t("no_image"))
        if r.building in config.PLACE_BY_EN:
            campus_map.show(r.building)
    imm = r.immediate_hazard == "Yes" or r.urgency == "Immediate" or any(w in r.description.lower() for w in ai.IMMEDIATE_WORDS)
    with st.container(border=True):
        st.markdown(f"**🤖 {t('ai_suggest')}**")
        if imm:
            st.markdown(f'<div class="alert">{t("ai_immediate")}</div>', unsafe_allow_html=True)
        cats = list(config.CATEGORIES)
        cur_cat = r.category or r.ai_category or cats[0]
        x1, x2 = st.columns(2)
        cat = x1.selectbox(t("category"), cats, index=cats.index(cur_cat), format_func=cat_name, key=f"cat{k}")
        subs = [c for c, (cc, _) in config.SUBTYPES.items() if cc == cat]
        cur_sub = r.subtype or r.ai_subtype
        sub = x2.selectbox(t("subtype"), subs, index=subs.index(cur_sub) if cur_sub in subs else 0, format_func=sub_name, key=f"sub{k}")
        x1, x2 = st.columns(2)
        L = x1.slider(t("likelihood"), 1, 5, int(r.likelihood or r.likelihood_reported or r.ai_likelihood or 3), key=f"L{k}")
        S = x2.slider(t("severity"), 1, 5, int(r.severity or r.severity_reported or r.ai_severity or 2), key=f"S{k}")
        lvl = config.level_from_score(L * S)
        st.markdown(f"{t('priority')}: {pill(lvl)} **{config.PRIORITY[lvl]}** · {t('score')} {L * S}", unsafe_allow_html=True)
        st.caption(f"{t('ai_conf')} {int((r.ai_confidence or 0) * 100)}% · {r.ai_source} · {r.ai_reason}")
        if r.lvl_model_pred:
            st.markdown(f"**{t('lvl_model')}:** {pill(r.lvl_model_pred)} {int((r.lvl_model_conf or 0) * 100)}% "
                        f"· {t('rep_L')} {r.likelihood_reported} × {t('rep_S')} {r.severity_reported}", unsafe_allow_html=True)
            st.caption("⚠️ " + t("lvl_model_warn"))
        else:
            st.caption(t("lvl_model_none"))
        meta = ai.model_meta()
        if r.ai_source in ("ml", "ml+rules") and meta and meta["data"] == "synthetic":
            st.caption("⚠️ " + t("synthetic_warn"))
        st.caption(t("thresholds"))
    depts = list(config.DEPARTMENTS)
    d0 = r.department or config.CATEGORY_TO_DEPT.get(cat)
    dep = st.selectbox(t("resp_dept"), depts, index=depts.index(d0) if d0 in depts else 0, format_func=dept_name, key=f"dep{k}")
    people = [x for x in users.values() if x.role == "responsible" and x.department == dep]
    ids = [None] + [x.id for x in people]
    asg = st.selectbox(t("assignee"), ids, index=ids.index(r.assigned_to) if r.assigned_to in ids else 0,
                       format_func=lambda i: t("none") if i is None else users[i].full_name, key=f"asg{k}")
    reason = st.text_input(t("return_note"), key=f"rn{k}")
    b1, b2 = st.columns(2)
    if b1.button(t("approve_send"), type="primary", key=f"ap{k}", disabled=r.status in ("Closed",)):
        with Session() as s:
            x = s.get(Report, k)
            x.category, x.subtype, x.likelihood, x.severity = cat, sub, L, S
            x.risk_score, x.risk_level, x.priority = L * S, lvl, config.PRIORITY[lvl]
            x.department, x.assigned_to, x.status = dep, asg, "Sent to Responsible"
            x.verified_by, x.verified_at = u["id"], dt.datetime.now()
            s.add(Update(report_id=k, user_name=u["name"], status="Sent to Responsible", note=""))
            s.commit()
        st.rerun()
    if b2.button(t("return_user"), key=f"rt{k}", disabled=r.status in ("Closed",)):
        if not reason.strip():
            st.warning(t("need_reason"))
        else:
            with Session() as s:
                x = s.get(Report, k)
                x.status, x.admin_note = "Returned", reason.strip()
                s.add(Update(report_id=k, user_name=u["name"], status="Returned", note=reason.strip()))
                s.commit()
            st.rerun()
    st.markdown(stepper(r.status), unsafe_allow_html=True)
    st.subheader(t("final_dec"))
    with Session() as s:
        ups = [x for x in s.get(Report, k).updates if x.status in ("In Progress", "Done") and x.user_name != u["name"]]
    if ups:
        last = ups[-1]
        c1, c2 = st.columns(2)
        with c1:
            kv(t("resp_reply"), f"{last.user_name} {chip(last.status)}")
        with c2:
            kv(t("sol_note"), last.note or "-")
        if last.evidence_path and os.path.exists(os.path.join(config.UPLOAD_DIR, last.evidence_path)):
            st.image(os.path.join(config.UPLOAD_DIR, last.evidence_path), width=220)
    else:
        st.caption(t("no_reply"))
    more = st.text_input(t("more_note"), key=f"mo{k}")
    c1, c2 = st.columns(2)
    if c1.button(t("close_report"), key=f"cl{k}", disabled=r.status != "Done", type="primary"):
        with Session() as s:
            s.get(Report, k).status = "Closed"
            s.add(Update(report_id=k, user_name=u["name"], status="Closed", note=""))
            s.commit()
        st.rerun()
    if c2.button(t("more_action"), key=f"ma{k}", disabled=r.status not in ("Done", "In Progress")):
        if not more.strip():
            st.warning(t("need_reason"))
        else:
            with Session() as s:
                x = s.get(Report, k)
                x.status, x.admin_note = "Sent to Responsible", more.strip()
                s.add(Update(report_id=k, user_name=u["name"], status="Sent to Responsible", note=more.strip()))
                s.commit()
            st.rerun()


def page_users():
    topbar()
    u = user()
    st.title(t("p_users"))
    with Session() as s:
        rows = list(s.scalars(select(User).order_by(User.id)))
    df = pd.DataFrame([{t("tbl_name"): x.full_name, t("tbl_username"): x.username,
                        t("tbl_role"): {"user": t("role_user"), "admin": t("role_adminx"), "responsible": t("role_resp")}[x.role],
                        t("resp_dept"): dept_name(x.department)} for x in rows])
    ev = st.dataframe(df, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row", key="utbl")
    if ev.selection.rows and st.button(t("del_user")):
        target = rows[ev.selection.rows[0]]
        if target.id == u["id"]:
            st.error(t("cant_del_self"))
        else:
            with Session() as s:
                s.delete(s.get(User, target.id)); s.commit()
            st.rerun()
    with st.container(border=True):
        st.subheader(t("add_user"))
        with st.form("adduser", clear_on_submit=True):
            c1, c2 = st.columns(2)
            fn = c1.text_input(t("full_name")); un = c2.text_input(t("tbl_username"))
            c1, c2, c3 = st.columns(3)
            pw = c1.text_input(t("password"), type="password")
            role = c2.selectbox(t("role"), ["user", "responsible", "admin"],
                                format_func=lambda x: {"user": t("role_user"), "admin": t("role_adminx"), "responsible": t("role_resp")}[x])
            dep = c3.selectbox(t("resp_dept"), [None] + list(config.DEPARTMENTS), format_func=lambda x: t("none") if x is None else dept_name(x))
            go = st.form_submit_button(t("create"), type="primary")
        if go:
            if not (fn and un and pw):
                st.error(t("need_all"))
            else:
                with Session() as s:
                    if s.scalar(select(User).where(User.username == un.strip())):
                        st.error(t("user_exists"))
                    else:
                        s.add(User(username=un.strip(), password_hash=db.hash_pw(pw), full_name=fn.strip(), role=role,
                                   department=dep if role == "responsible" else None))
                        s.commit(); st.success(t("user_created")); st.rerun()


def export_df(include_demo):
    """Columns follow the supervisor's Risk_Reports_Dataset sheet (README_ML naming)."""
    with Session() as s:
        rows = [r for r in s.scalars(select(Report).where(Report.verified_at.is_not(None))) if include_demo or not r.is_demo]
    return pd.DataFrame([{
        "report_id": r.code, "reported_at": r.created_at.strftime("%Y-%m-%d %H:%M"), "building_id": r.building, "floor": r.floor,
        "location_type": r.location_type, "room_id": r.room, "risk_category_code": r.category, "risk_subtype_code": r.subtype,
        "risk_description": r.description, "people_exposed_band": r.people_exposed, "exposure_frequency": r.frequency,
        "existing_controls": r.existing_controls, "visible_damage": r.visible_damage, "hazard_active": r.immediate_hazard,
        "reporter_urgency": r.urgency, "likelihood_reported": r.likelihood_reported, "severity_reported": r.severity_reported,
        "assessed_at": r.verified_at.strftime("%Y-%m-%d %H:%M") if r.verified_at else None,
        "likelihood_verified": r.likelihood, "severity_verified": r.severity, "risk_level_verified": r.risk_level,
        "assessor_notes": r.assessor_notes, "status": r.status, "is_demo": r.is_demo} for r in rows])


def page_settings():
    topbar()
    st.title(t("p_settings"))
    with st.container(border=True):
        st.subheader(t("settings_ai"))
        st.info(t("data_info"))
        meta = ai.model_meta()
        if meta:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Data", meta["data"]); c2.metric("Rows", meta["rows"])
            c3.metric("Macro-F1 (hold-out)", f"{meta['macro_f1_holdout']:.2f}"); c4.metric("Classes", meta["classes"])
            st.caption(f"{meta['model']} · {meta['split']} · {meta['trained_at']}")
            if meta["data"] == "synthetic":
                st.warning(t("synthetic_warn"))
        else:
            st.caption(t("ai_rules_note"))
        inc = st.checkbox(t("include_demo"))
        df = export_df(inc)
        st.metric(t("verified_rows"), len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)
        buf = io.BytesIO(); df.to_excel(buf, index=False)
        st.download_button(t("download"), buf.getvalue(), "risk_reports_verified.xlsx")
        import train_model
        c1, c2 = st.columns(2)
        if c1.button(t("train")):
            m2, why = train_model.train_verified(df)
            if m2:
                st.success(f"OK: {m2['rows']} rows, macro-F1 {m2['macro_f1_holdout']:.2f}"); ai.reload()
            else:
                st.warning(t("train_min", n=train_model.MIN_ROWS) + f" ({why})")
        if c2.button(t("train_syn")):
            m3 = train_model.train_synthetic(); ai.reload()
            st.success(f"OK: {m3['rows']} rows, macro-F1 {m3['macro_f1_holdout']:.2f}")
    demo_banner()


def page_assigned():
    topbar()
    u = user()
    users = load_users()
    st.title(t("p_assigned"))
    with Session() as s:
        rows = list(s.scalars(select(Report).where(mine(u)).order_by(Report.created_at.desc())))
    tabs = st.tabs([t("tab_new"), t("tab_prog"), t("tab_done")])
    groups = [["Sent to Responsible"], ["In Progress"], ["Done"]]
    for tab, g, i in zip(tabs, groups, range(3)):
        with tab:
            rs = [r for r in rows if r.status in g]
            if not rs:
                st.info(t("no_reports")); continue
            sel = table(rs, users, f"as{i}")
            if sel:
                respond(sel, u, users, editable=(g != ["Done"]))
    demo_banner()


def respond(r, u, users, editable=True):
    k = r.id
    with st.container(border=True):
        st.subheader(t("assigned_report"))
        a, b = st.columns([1.2, 1])
        with a:
            kv(t("tbl_id"), r.code); kv(t("risk_title"), r.title or "-"); kv(t("tbl_type"), cat_name(r.category))
            kv(t("tbl_loc"), loc_text(r)); kv(t("tbl_date"), r.created_at.strftime("%d %b %Y"))
            kv(t("rep_desc"), r.description)
            if r.admin_note:
                kv(t("admin_note_l"), r.admin_note)
        with b:
            if img_path(r):
                st.image(img_path(r), use_container_width=True)
    if not editable:
        return
    with st.container(border=True):
        st.subheader(t("your_response"))
        sol = st.text_area(t("solution"), key=f"sol{k}")
        c1, c2, c3 = st.columns(3)
        stt = c1.radio(t("status"), ["In Progress", "Done"], format_func=v, key=f"stt{k}")
        exp = c2.date_input(t("exp_date"), value=None, key=f"exp{k}")
        ev = c3.file_uploader(t("evidence"), type=["png", "jpg", "jpeg"], key=f"ev{k}")
        if st.button(t("send_admin"), type="primary", key=f"send{k}"):
            if not sol.strip():
                st.warning(t("need_solution")); return
            path = None
            if ev is not None:
                path = f"{uuid.uuid4().hex}{os.path.splitext(ev.name)[1].lower()}"
                with open(os.path.join(config.UPLOAD_DIR, path), "wb") as f:
                    f.write(ev.getbuffer())
            with Session() as s:
                x = s.get(Report, k)
                x.status, x.expected_date = stt, str(exp) if exp else None
                s.add(Update(report_id=k, user_name=u["name"], status=stt, note=sol.strip(), evidence_path=path))
                s.commit()
            st.rerun()


def page_history():
    topbar()
    u = user()
    users = load_users()
    st.title(t("p_history"))
    with Session() as s:
        rows = list(s.scalars(select(Report).where(mine(u), Report.status.in_(["Done", "Closed"])).order_by(Report.created_at.desc())))
    if not rows:
        st.info(t("history_empty")); return
    sel = table(rows, users, "hist")
    if sel:
        respond(sel, u, users, editable=False)


# ------------------------------------------------------------------ navigation
css()
u = user()
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
P = st.Page
if u and u["role"] == "admin":
    pages = [P(page_reports, title=t("p_reports"), url_path="reports", default=True),
             P(page_users, title=t("p_users"), url_path="users"), P(page_settings, title=t("p_settings"), url_path="settings")]
elif u and u["role"] == "responsible":
    pages = [P(page_assigned, title=t("p_assigned"), url_path="assigned", default=True),
             P(page_history, title=t("p_history"), url_path="history")]
elif u:
    pages = [P(page_report, title=t("p_report"), url_path="report", default=True),
             P(page_myreports, title=t("p_myreports"), url_path="myreports")]
elif st.session_state.get("guest"):
    pages = [P(page_report, title=t("p_report"), url_path="report", default=True),
             P(page_track, title=t("nav_track"), url_path="track")]
else:
    pages = [P(page_login, title=t("login"), url_path="login", default=True)]
st.navigation(pages).run()
