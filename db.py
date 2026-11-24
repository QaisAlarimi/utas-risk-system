import hashlib, hmac, os, random, datetime as dt
from sqlalchemy import create_engine, String, Integer, Text, DateTime, Boolean, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
import config


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))          # admin | responsible
    department: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    reporter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    expected_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.now)
    reporter_type: Mapped[str] = mapped_column(String(20), default="Visitor")   # Visitor | Staff | Student
    reporter_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reporter_contact: Mapped[str | None] = mapped_column(String(100), nullable=True)
    building: Mapped[str] = mapped_column(String(60))
    floor: Mapped[str] = mapped_column(String(20))
    location_type: Mapped[str] = mapped_column(String(30))
    room: Mapped[str | None] = mapped_column(String(40), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    people_exposed: Mapped[str] = mapped_column(String(20), default="Unknown")
    frequency: Mapped[str] = mapped_column(String(20), default="Unknown")
    injury_occurred: Mapped[str] = mapped_column(String(10), default="Unknown")
    immediate_hazard: Mapped[str] = mapped_column(String(10), default="Unknown")   # = hazard_active
    existing_controls: Mapped[str] = mapped_column(String(10), default="Unknown")
    visible_damage: Mapped[str] = mapped_column(String(10), default="Unknown")
    assessor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    likelihood_reported: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity_reported: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lvl_model_pred: Mapped[str | None] = mapped_column(String(10), nullable=True)
    lvl_model_conf: Mapped[float | None] = mapped_column(nullable=True)
    urgency: Mapped[str] = mapped_column(String(15), default="Normal")
    photo_path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # AI suggestion (never final)
    ai_category: Mapped[str | None] = mapped_column(String(5), nullable=True)
    ai_subtype: Mapped[str | None] = mapped_column(String(6), nullable=True)
    ai_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ai_likelihood: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(nullable=True)
    ai_source: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ai_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Verified by a human (becomes the ML label)
    category: Mapped[str | None] = mapped_column(String(5), nullable=True)
    subtype: Mapped[str | None] = mapped_column(String(6), nullable=True)
    likelihood: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(10), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(3), nullable=True)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="New")
    department: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    updates: Mapped[list["Update"]] = relationship(back_populates="report", order_by="Update.created_at")


class Update(Base):
    __tablename__ = "updates"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    user_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.now)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    evidence_path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    report: Mapped[Report] = relationship(back_populates="updates")


engine = create_engine(config.DATABASE_URL, future=True, pool_pre_ping=True)
Session = sessionmaker(engine, expire_on_commit=False)


def hash_pw(pw: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 120_000)
    return salt.hex() + "$" + h.hex()


def check_pw(pw: str, stored: str) -> bool:
    salt, h = stored.split("$")
    return hmac.compare_digest(hash_pw(pw, bytes.fromhex(salt)).split("$")[1], h)


def authenticate(username: str, password: str):
    with Session() as s:
        u = s.scalar(select(User).where(User.username == username.strip()))
        if u and check_pw(password, u.password_hash):
            return u
    return None


def next_code(s) -> str:
    n = s.query(Report).count() + 1
    return f"RPT-{dt.date.today().year}-{n:04d}"


def init_db(seed: bool = True):
    Base.metadata.create_all(engine)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    with Session() as s:
        if s.query(User).count() == 0:
            # DEFAULT DEMO ACCOUNTS - change before any real use
            s.add_all([
                User(username="user1", password_hash=hash_pw("user123"), full_name="Ahmed Al Balushi", role="user", is_demo=True),
                User(username="admin", password_hash=hash_pw("admin123"), full_name="Demo Admin", role="admin", is_demo=True),
                User(username="elec", password_hash=hash_pw("resp123"), full_name="Demo Electrical Officer", role="responsible", department="FM_ELEC", is_demo=True),
                User(username="hse", password_hash=hash_pw("resp123"), full_name="Demo HSE Officer", role="responsible", department="HSE", is_demo=True),
                User(username="maint", password_hash=hash_pw("resp123"), full_name="Demo Maintenance Officer", role="responsible", department="FM_GEN", is_demo=True),
                User(username="equip", password_hash=hash_pw("resp123"), full_name="Demo Equipment Officer", role="responsible", department="EQP", is_demo=True),
            ])
            s.commit()
    if seed:
        seed_demo()


DEMO_TEXTS = [
    ("Exposed wires hanging from the ceiling near the projector, students sit below.", "Classroom"),
    ("Wet floor in the corridor after the AC leak, people are slipping.", "Corridor"),
    ("Chemical spill on the bench in the lab, strong smell, no label on the bottle.", "Lab"),
    ("Fire extinguisher is missing next to the workshop door.", "Workshop"),
    ("Cables on the floor behind the instructor desk, trip hazard.", "Classroom"),
    ("Waste bin is overflowing and not emptied for days.", "Corridor"),
    ("Lathe machine broke down, mechanical failure, needs maintenance.", "Workshop"),
    ("Emergency exit blocked by stacked boxes.", "Corridor"),
    ("Poor lighting in the stairs, very dark in the evening.", "Corridor"),
    ("Overloaded socket with many extension plugs in the office.", "Office"),
    ("Gas smell near the lab storage room.", "Lab"),
    ("Rust and corrosion on the old equipment frame.", "Workshop"),
    ("Broken tile on the walkway, uneven floor.", "Corridor"),
    ("Smoke detector not working in the library hall.", "Other"),
    ("Strong fumes in the lab, ventilation not working.", "Lab"),
    ("Storage room is messy and materials stacked unsafe.", "Workshop"),
    ("انسكاب مادة كيميائية في المختبر وبدون ملصق على القارورة.", "Lab"),
    ("أسلاك مكشوفة خلف السبورة في القاعة.", "Classroom"),
    ("الأرضية مبللة في الممر والناس ينزلقون.", "Corridor"),
    ("المكيف لا يعمل والحرارة عالية جدا في المعمل.", "Lab"),
]


def seed_demo():
    import ai
    rnd = random.Random(7)
    with Session() as s:
        if s.query(Report).count() > 0:
            return
        admin = s.scalar(select(User).where(User.role == "admin"))
        resp = {u.department: u for u in s.scalars(select(User).where(User.role == "responsible"))}
        now = dt.datetime.now()
        for i, (txt, loc) in enumerate(DEMO_TEXTS):
            sug = ai.suggest(txt, urgency=rnd.choice(config.URGENCY[:2]))
            r = Report(code=f"RPT-DEMO-{i+1:03d}", title=txt.split(",")[0].split(".")[0][:60], created_at=now - dt.timedelta(days=rnd.randint(0, 40), hours=rnd.randint(0, 20)),
                       reporter_type=rnd.choice(["Visitor", "Staff", "Student"]), building=rnd.choice(config.BUILDINGS[:-1]),
                       floor=rnd.choice(config.FLOORS), location_type=loc, description=txt,
                       people_exposed=rnd.choice(config.PEOPLE_BANDS), frequency=rnd.choice(config.FREQUENCIES),
                       injury_occurred="No", immediate_hazard="No", existing_controls=rnd.choice(config.YES_NO_UNKNOWN),
                       visible_damage=rnd.choice(config.YES_NO_UNKNOWN), urgency="Normal", is_demo=True,
                       ai_category=sug["category"], ai_subtype=sug["subtype"], ai_level=sug["level"],
                       ai_likelihood=sug["likelihood"], ai_severity=sug["severity"], ai_confidence=sug["confidence"],
                       ai_source=sug["source"], ai_reason=sug["reason"])
            if i % 3 != 0 and sug["subtype"]:   # two thirds are already verified by the demo admin
                r.category, r.subtype = sug["category"], sug["subtype"]
                r.likelihood, r.severity = sug["likelihood"], sug["severity"]
                r.risk_score = r.likelihood * r.severity
                r.risk_level = config.level_from_score(r.risk_score)
                r.priority = config.PRIORITY[r.risk_level]
                r.verified_by, r.verified_at = admin.id, r.created_at + dt.timedelta(hours=3)
                r.department = config.CATEGORY_TO_DEPT.get(r.category)
                r.assigned_to = resp[r.department].id if r.department in resp else None
                r.status = rnd.choice(["Sent to Responsible", "In Progress", "Done", "Closed"])
            s.add(r)
        s.commit()
