"""Reference data for the UTAS Risk Management System.

Taxonomy (categories / subtypes) is read from the supervisor's Excel template so the
web app and the ML dataset always use the same codes.
Anything marked PLACEHOLDER must be replaced with real UTAS data.
"""
import os
import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_XLSX = os.path.join(BASE, "data", "Campus_Risk_ML_Dataset_Template.xlsx")
UPLOAD_DIR = os.path.join(BASE, "uploads")
MODEL_DIR = os.path.join(BASE, "models")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE, "data", "risk.db"))


def _load_taxonomy():
    wb = openpyxl.load_workbook(TEMPLATE_XLSX, read_only=True)
    cats, subs = {}, {}
    for r in wb["Risk_Taxonomy"].iter_rows(min_row=2, values_only=True):
        if r[0]:
            cats[r[0]] = r[1]
            subs[r[2]] = (r[0], r[3])
    return cats, subs


CATEGORIES, SUBTYPES = _load_taxonomy()          # {code: name}, {code: (cat_code, name)}

CATEGORY_AR = {
    "EH": "مخاطر كهربائية", "FH": "مخاطر الحريق", "ED": "تلف المعدات",
    "CH": "مخاطر كيميائية", "PH": "مخاطر مادية", "HK": "سوء النظافة والترتيب",
}
SUBTYPE_AR = {
    "EH01": "أسلاك كهربائية مكشوفة", "EH02": "كابلات كهربائية تالفة", "EH03": "ماس كهربائي",
    "EH04": "أحمال زائدة على المقابس", "EH05": "معدات كهربائية معطلة", "EH06": "خطر الصعق الكهربائي",
    "EH07": "تأريض غير سليم", "EH08": "رطوبة بالقرب من الكهرباء", "EH09": "أعمال كهربائية غير مصرح بها",
    "EH10": "جهد عالٍ",
    "FH01": "تخزين مواد قابلة للاشتعال", "FH02": "تسرب غاز", "FH03": "مخرج طوارئ مسدود",
    "FH04": "عطل في نظام إنذار الحريق", "FH05": "خطر حريق كهربائي", "FH06": "التدخين في مناطق ممنوعة",
    "FH07": "ارتفاع حرارة المعدات", "FH08": "نقص طفايات الحريق", "FH09": "تخزين مواد كيميائية غير سليم",
    "FH10": "أعمال اللحام والقطع الساخنة",
    "ED01": "ضعف الصيانة", "ED02": "تآكل المعدات", "ED03": "عطل ميكانيكي / سوء استخدام",
    "ED04": "تلف بسبب تذبذب الكهرباء", "ED05": "خلل في المعايرة", "ED06": "تحميل زائد على المعدات",
    "ED07": "أضرار المياه", "ED08": "عطل البرمجيات / النظام", "ED09": "معدات قديمة",
    "CH01": "انسكاب مواد كيميائية", "CH02": "التعرض لغاز سام", "CH03": "ملامسة مواد أكالة",
    "CH04": "استنشاق أبخرة خطرة", "CH05": "حروق كيميائية", "CH06": "ملصقات كيميائية غير سليمة",
    "CH07": "خطر تفاعل كيميائي", "CH08": "فشل تخزين المواد الكيميائية", "CH09": "التعرض للنفايات الخطرة",
    "CH10": "مواد كيميائية قابلة للاشتعال",
    "PH01": "سقوط أجسام", "PH02": "حواف حادة", "PH03": "أسطح زلقة", "PH04": "إضاءة ضعيفة",
    "PH05": "اهتزاز مفرط", "PH06": "درجات حرارة قصوى", "PH07": "أماكن مغلقة / ضيقة",
    "PH08": "جسيمات متطايرة", "PH09": "إصابات الرفع اليدوي", "PH10": "ممر غير آمن",
    "HK01": "أماكن عمل مزدحمة", "HK02": "تراكم النفايات", "HK03": "ممرات مسدودة", "HK04": "انسكاب زيوت",
    "HK05": "تخزين غير منظم", "HK06": "ضعف ممارسات النظافة", "HK07": "مخارج طوارئ معاقة",
    "HK08": "تخزين مواد غير سليم", "HK09": "كابلات سائبة على الأرض", "HK10": "حاويات نفايات ممتلئة",
}

# ---- Field value lists (taken from the template's Data_Dictionary) ----
FLOORS = ["Ground", "1", "2", "3", "Other"]
LOCATION_TYPES = ["Lab", "Classroom", "Corridor", "Office", "Workshop", "Other"]
PEOPLE_BANDS = ["1", "2-5", "6-20", "21-50", "50+", "Unknown"]
FREQUENCIES = ["Rarely", "Occasionally", "Daily", "Continuously", "Unknown"]
YES_NO_UNKNOWN = ["Yes", "No", "Unknown"]
URGENCY = ["Normal", "Urgent", "Immediate"]
LEVELS = ["Low", "Medium", "High", "Critical"]
STATUSES = ["New", "Sent to Responsible", "In Progress", "Done", "Closed", "Returned"]
LIKELIHOOD_LABELS = {1: "Rare", 2: "Unlikely", 3: "Possible", 4: "Likely", 5: "Almost certain"}
SEVERITY_LABELS = {1: "Negligible", 2: "Minor", 3: "Moderate", 4: "Major", 5: "Catastrophic"}

# Real UTAS Salalah campus places (numbers and names from the official campus map, assets/campus_map.png).
# n: (English, Arabic, [(x, y) marker positions in map-image pixels])
PLACES = {
    1: ("Gate 1 (Main Entry & Exit)", "بوابة ١ (الدخول والخروج الرئيسي)", [(540, 399)]),
    2: ("Gate 2 (Emergency Entry / Exit)", "بوابة ٢ (دخول وخروج الطوارئ)", [(968, 394)]),
    3: ("Male Students Parking Entry / Exit Gate", "دخول وخروج مواقف الطلاب الذكور", [(201, 375)]),
    4: ("Female Entry / Exit Gate", "دخول وخروج مواقف الطالبات", [(894, 381)]),
    5: ("Student's Outside Parking", "مواقف الطلاب الخارجية", [(128, 389), (355, 395), (795, 396)]),
    6: ("Information Technology Building (I.T.)", "مبنى تقنية المعلومات", [(635, 258)]),
    7: ("Library (inside I.T. Building)", "المكتبة (داخل مبنى تقنية المعلومات)", [(600, 309)]),
    8: ("Career Guidance Building", "مبنى التوجيه الوظيفي", [(678, 262)]),
    9: ("Business Studies Building (BUSS.)", "مبنى الدراسات التجارية", [(788, 299)]),
    10: ("Dean's Office", "مكتب العميد", [(833, 343)]),
    11: ("Canteen (Female Students)", "مطعم (الطالبات)", [(839, 278)]),
    12: ("Quality Assurance Office (Q.A.)", "مكتب ضمان الجودة", [(964, 356)]),
    13: ("Electrical & Electronic Engineering (ELEC.)", "شعبة الهندسة الكهربائية والإلكترونية", [(706, 240)]),
    14: ("Civil & Architecture Engineering (CIVL)", "شعبة الهندسة المدنية والمعمارية", [(675, 174)]),
    15: ("Mechanical & Industrial Engineering (MECH.)", "شعبة الهندسة الميكانيكية والصناعية", [(773, 207)]),
    16: ("Mechanical Workshop", "ورشة ميكانيكية", [(761, 157)]),
    17: ("Canteen (Male Students)", "مطعم (الطلاب)", [(794, 180)]),
    18: ("Chemical & Petrochemical Eng. / Physics & Chemistry", "الهندسة الكيميائية والبتروكيماوية / الفيزياء والكيمياء", [(695, 133)]),
    19: ("BSIT Building", "مبنى الدراسات التجارية وتقنية المعلومات", [(572, 156)]),
    20: ("Multi-Purpose Building", "قاعة متعددة الأغراض", [(646, 124)]),
    21: ("Staff Club Building", "مبنى نادي الموظفين", [(709, 113)]),
    22: ("Student's Hub (Male & Female)", "استراحة (الطلاب والطالبات)", [(630, 97)]),
    23: ("Mosque", "المسجد", [(698, 94)]),
    24: ("Administration & Finance (Bldg. #1)", "الإدارة والتمويل (المبنى ١)", [(734, 62)]),
    25: ("Educational Technology Center - ETC (Bldg. #2)", "مركز تقنيات التعليم (المبنى ٢)", [(697, 46)]),
    26: ("Students Registration", "قبول وتسجيل الطلبة", [(672, 50)]),
    27: ("Student Affairs (Bldg. #3)", "شؤون الطلاب (المبنى ٣)", [(664, 30)]),
    28: ("Staff Office (Bldg. #4)", "مكتب الموظفين (المبنى ٤)", [(636, 14)]),
    29: ("University Store", "مخزن الجامعة", [(703, 26)]),
    30: ("University Warehouse", "مستودع الجامعة", [(663, 14)]),
    31: ("Clinic - Small Villa (Male & Female)", "العيادة (طلاب وطالبات)", [(649, 64)]),
    32: ("Guest (Small Villas)", "ضيوف (فلل صغيرة)", [(623, 50)]),
    33: ("Dean's (Big Villa)", "العميد (فيلا كبيرة)", [(595, 23)]),
    34: ("Prayer Room (Female)", "مصلى (طالبات)", [(552, 15)]),
    35: ("English Language Center (ELC)", "مركز اللغة الإنجليزية", [(495, 25)]),
    36: ("New Classrooms (ELC)", "فصول دراسية جديدة", [(353, 53)]),
    37: ("Back Entrance", "المدخل الخلفي", [(424, 24)]),
    38: ("Football Field", "ملعب كرة القدم", [(406, 309)]),
    39: ("Maintenance Quarters-1", "أماكن الصيانة ١", [(735, 46)]),
    40: ("Maintenance Quarters-2", "أماكن الصيانة ٢", [(124, 315), (577, 357)]),
}
PLACE_BY_EN = {en: n for n, (en, ar, _) in PLACES.items()}
PLACE_AR = {en: ar for en, ar, _ in PLACES.values()}
NOT_SPECIFIED = "Not specified"
# academic / admin buildings used for demo data
BUILDINGS = [PLACES[n][0] for n in (6, 7, 9, 13, 14, 15, 16, 18, 19, 20, 24, 8)] + [NOT_SPECIFIED]

# PLACEHOLDER: responsible departments and the category -> department routing.
DEPARTMENTS = {
    "FM_ELEC": ("Facilities - Electrical", "المرافق - الكهرباء"),
    "FM_GEN": ("Facilities & Maintenance", "المرافق والصيانة"),
    "HSE": ("Health & Safety Office", "مكتب الصحة والسلامة"),
    "EQP": ("Equipment Maintenance", "صيانة المعدات"),
}
CATEGORY_TO_DEPT = {"EH": "FM_ELEC", "FH": "HSE", "ED": "EQP", "CH": "HSE", "PH": "FM_GEN", "HK": "FM_GEN"}

# Risk score (likelihood x severity) -> level / priority. PROPOSED thresholds: the risk
# specialist must confirm the official rubric (see README_ML sheet).
def level_from_score(score: int) -> str:
    if score <= 4:
        return "Low"
    if score <= 9:
        return "Medium"
    if score <= 16:
        return "High"
    return "Critical"


PRIORITY = {"Low": "P4", "Medium": "P3", "High": "P2", "Critical": "P1"}
