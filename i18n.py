import streamlit as st
import config

UI = {
 "app_title": ("UTAS Risk Management System", "نظام إدارة المخاطر - UTAS"),
 "subtitle": ("AI-assisted risk reporting and classification. The AI only suggests; a human decides.",
              "الإبلاغ عن المخاطر وتصنيفها بمساعدة الذكاء الاصطناعي. الذكاء الاصطناعي يقترح فقط والقرار للإنسان."),
 "demo_banner": ("DEMO DATA: all reports and accounts shown are sample data, not real incidents.",
                 "بيانات تجريبية: كل البلاغات والحسابات المعروضة هي أمثلة وليست حوادث حقيقية."),
 "nav_report": ("Report a Risk", "الإبلاغ عن خطر"), "nav_track": ("Track my report", "تتبع بلاغي"),
 "nav_review": ("Reports Review", "مراجعة البلاغات"), "nav_dashboard": ("Dashboard", "لوحة المؤشرات"),
 "nav_assigned": ("My Assigned Reports", "البلاغات المسندة إليّ"), "nav_data": ("ML Dataset", "بيانات التدريب"),
 "nav_login": ("Login", "تسجيل الدخول"), "logout": ("Logout", "تسجيل الخروج"), "language": ("Language", "اللغة"),
 "username": ("Username", "اسم المستخدم"), "password": ("Password", "كلمة المرور"), "login_btn": ("Sign in", "دخول"),
 "bad_login": ("Wrong username or password.", "اسم المستخدم أو كلمة المرور غير صحيحة."),
 "login_hint": ("Staff only (Admin / Responsible Person). Anyone can report a risk without logging in.",
                "للموظفين فقط (مسؤول النظام / الشخص المسؤول). يمكن لأي شخص الإبلاغ عن خطر دون تسجيل الدخول."),
 "welcome": ("Signed in as", "مسجّل الدخول باسم"),
 "role_admin": ("Admin", "مسؤول النظام"), "role_responsible": ("Responsible Person", "الشخص المسؤول"), "role_visitor": ("Visitor", "زائر"),
 "form_title": ("Report a Risk", "الإبلاغ عن خطر"),
 "emergency": ("If there is an immediate danger to life (fire, gas leak, electric shock), call the emergency number / campus security FIRST. This form is not an emergency line.",
               "إذا كان هناك خطر مباشر على الحياة (حريق، تسرب غاز، صعق كهربائي) اتصل أولاً برقم الطوارئ / أمن الحرم. هذا النموذج ليس خط طوارئ."),
 "reporter_type": ("I am a", "أنا"), "reporter_name": ("Name (optional)", "الاسم (اختياري)"),
 "reporter_contact": ("Contact (optional)", "وسيلة التواصل (اختياري)"),
 "privacy_note": ("Do not write names or personal identifiers of other people in the description.",
                  "لا تكتب أسماء أو معرّفات شخصية لأشخاص آخرين في الوصف."),
 "building": ("Building", "المبنى"), "floor": ("Floor", "الطابق"), "location_type": ("Location type", "نوع المكان"),
 "room": ("Room / area (optional)", "القاعة / المنطقة (اختياري)"), "description": ("Describe the risk", "صف الخطر"),
 "desc_help": ("What is wrong, where exactly, and who could be affected?", "ما المشكلة؟ وأين بالضبط؟ ومن قد يتأثر؟"),
 "people": ("People exposed", "عدد الأشخاص المعرّضين"), "frequency": ("How often are people exposed?", "كم مرة يتعرض الناس للخطر؟"),
 "injury": ("Has anyone been injured?", "هل أُصيب أحد؟"), "immediate": ("Is the hazard still active now?", "هل الخطر قائم حالياً؟"),
 "controls": ("Are there existing protective measures?", "هل توجد إجراءات وقائية حالياً؟"),
 "damage": ("Is there visible damage?", "هل يوجد ضرر ظاهر؟"),
 "model_info": ("AI model", "نموذج الذكاء الاصطناعي"),
 "synthetic_warn": ("Trained on SYNTHETIC sample data (supervisor file), not real incidents. Scores prove the pipeline only; do not quote them as real accuracy.",
                    "مدرَّب على بيانات اصطناعية (ملف المشرفة) وليس حوادث حقيقية. النتائج تثبت عمل المسار فقط، ولا تُذكر كدقة حقيقية."),
 "train_syn": ("Re-train on the synthetic sample dataset", "إعادة التدريب على البيانات الاصطناعية"),
 "ml_arabic_note": ("The model learned from English text only; Arabic reports use keyword rules.", "النموذج تعلّم من نص إنجليزي فقط؛ البلاغات العربية تعتمد على قواعد الكلمات المفتاحية."),
 "urgency": ("Urgency", "درجة الاستعجال"), "photo": ("Photo (optional)", "صورة (اختياري)"),
 "submit": ("Submit report", "إرسال البلاغ"), "need_desc": ("Please describe the risk (at least 15 characters).", "الرجاء وصف الخطر (15 حرفاً على الأقل)."),
 "submitted": ("Report submitted. Your tracking code:", "تم إرسال البلاغ. رمز المتابعة الخاص بك:"),
 "keep_code": ("Keep this code to track your report.", "احتفظ بهذا الرمز لمتابعة بلاغك."),
 "track_title": ("Track my report", "تتبع بلاغي"), "code": ("Tracking code", "رمز المتابعة"), "find": ("Find", "بحث"),
 "not_found": ("No report with this code.", "لا يوجد بلاغ بهذا الرمز."), "status": ("Status", "الحالة"),
 "created": ("Submitted", "تاريخ الإرسال"), "history": ("History", "السجل"),
 "review_title": ("Reports Review", "مراجعة البلاغات"), "filter_status": ("Status", "الحالة"), "filter_level": ("Risk level", "مستوى الخطر"),
 "filter_cat": ("Category", "الفئة"), "all": ("All", "الكل"), "pending_only": ("Awaiting verification only", "بانتظار التحقق فقط"),
 "no_reports": ("No reports match.", "لا توجد بلاغات مطابقة."), "select_report": ("Select a report", "اختر بلاغاً"),
 "ai_box": ("AI suggestion (not final)", "اقتراح الذكاء الاصطناعي (غير نهائي)"),
 "ai_source": ("Source", "المصدر"), "ai_conf": ("Confidence", "الثقة"), "ai_why": ("Matched on", "بناءً على"),
 "ai_rules_note": ("Rules-based suggestion (no trained model yet). Verify carefully.", "اقتراح قائم على قواعد (لا يوجد نموذج مدرَّب بعد). تحقق بعناية."),
 "ai_immediate": ("Possible IMMEDIATE hazard - follow the emergency procedure now.", "قد يكون خطراً مباشراً - اتبع إجراءات الطوارئ فوراً."),
 "verify_title": ("Human decision", "القرار البشري"), "category": ("Category", "الفئة"), "subtype": ("Risk type", "نوع الخطر"),
 "likelihood": ("Likelihood (1-5)", "الاحتمالية (1-5)"), "severity": ("Severity (1-5)", "الشدة (1-5)"),
 "score": ("Risk score", "درجة الخطر"), "level": ("Risk level", "مستوى الخطر"), "priority": ("Priority", "الأولوية"),
 "thresholds": ("Proposed thresholds (to be confirmed by the risk specialist): 1-4 Low, 5-9 Medium, 10-16 High, 17-25 Critical.",
                "الحدود المقترحة (بانتظار اعتماد أخصائي المخاطر): 1-4 منخفض، 5-9 متوسط، 10-16 عالٍ، 17-25 حرج."),
 "department": ("Responsible department", "الجهة المسؤولة"), "assignee": ("Assign to", "إسناد إلى"),
 "note": ("Note", "ملاحظة"), "save_verify": ("Confirm & save decision", "اعتماد وحفظ القرار"),
 "saved": ("Saved.", "تم الحفظ."), "verified_by": ("Verified by", "تم التحقق بواسطة"), "not_verified": ("Not verified yet", "لم يتم التحقق بعد"),
 "reporter": ("Reporter", "مقدّم البلاغ"), "location": ("Location", "الموقع"), "details": ("Details", "التفاصيل"),
 "assigned_title": ("My Assigned Reports", "البلاغات المسندة إليّ"), "my_dept": ("Department", "القسم"),
 "update_status": ("Update status", "تحديث الحالة"), "add_update": ("Save update", "حفظ التحديث"),
 "dash_title": ("Dashboard", "لوحة المؤشرات"), "total": ("Total reports", "إجمالي البلاغات"), "pending": ("Awaiting verification", "بانتظار التحقق"),
 "open_high": ("Open High/Critical", "مفتوحة عالية/حرجة"), "by_cat": ("Reports by category", "البلاغات حسب الفئة"),
 "by_level": ("Reports by risk level", "البلاغات حسب مستوى الخطر"), "by_status": ("Reports by status", "البلاغات حسب الحالة"),
 "data_title": ("ML training dataset", "بيانات تدريب النموذج"),
 "data_info": ("Only human-verified, real reports should be used for training. Demo rows are excluded by default. Leakage fields (status, department, assignee, AI outputs) are not exported as features.",
               "تُستخدم البلاغات الحقيقية التي تحقق منها إنسان فقط للتدريب. تُستثنى البيانات التجريبية افتراضياً. حقول التسرب (الحالة، الجهة، المكلّف، مخرجات الذكاء الاصطناعي) لا تُصدَّر كخصائص."),
 "include_demo": ("Include demo rows (for testing the pipeline only)", "تضمين البيانات التجريبية (لاختبار المسار فقط)"),
 "verified_rows": ("Verified rows", "الصفوف المتحقق منها"), "download": ("Download Excel", "تنزيل Excel"),
 "train": ("Train model on verified data", "تدريب النموذج على البيانات المتحقق منها"),
 "train_min": ("Not enough real verified data yet: need at least {n} rows and 2+ subtypes with 5+ examples.",
               "لا توجد بيانات حقيقية متحققة كافية بعد: يلزم {n} صفاً على الأقل ونوعان فأكثر بخمسة أمثلة لكل منهما."),
 "access_denied": ("You do not have access to this page.", "ليس لديك صلاحية الوصول لهذه الصفحة."),
 "none": ("None", "لا يوجد"), "choose": ("Choose...", "اختر..."),
 "map_title": ("Location on campus (optional)", "الموقع في الجامعة (اختياري)"),
 "map_hint": ("Click a numbered building on the map, or choose it from the list. You can skip this.",
              "اضغط على رقم المبنى في الخريطة، أو اخترْه من القائمة. ويمكنك تخطّي هذه الخطوة."),
 "map_scroll": ("Use + / − (or pinch) to zoom the map, then tap a number. Or use the list below.", "كبّر الخريطة بأزرار + / − (أو بإصبعين) ثم اضغط الرقم، أو استخدم القائمة أدناه."),
 "map_list": ("Or choose from the list", "أو اختر من القائمة"), "map_none": ("Not specified", "غير محدد"),
 "map_sel": ("Selected location", "الموقع المحدد"), "map_clear": ("Clear selection", "إلغاء الاختيار"),
 "map_caption": ("UTAS Salalah campus map", "خريطة جامعة التقنية والعلوم التطبيقية - صلالة"),
}
VAL = {
 "Low": "منخفض", "Medium": "متوسط", "High": "عالٍ", "Critical": "حرج",
 "New": "جديد", "Under Review": "قيد المراجعة", "Action Required": "يتطلب إجراء", "Resolved": "تمت المعالجة", "Closed": "مغلق",
 "Normal": "عادي", "Urgent": "عاجل", "Immediate": "فوري", "Yes": "نعم", "No": "لا", "Unknown": "غير معروف",
 "Ground": "الأرضي", "Other": "أخرى", "Lab": "مختبر", "Classroom": "قاعة دراسية", "Corridor": "ممر", "Office": "مكتب", "Workshop": "ورشة",
 "Visitor": "زائر", "Staff": "موظف", "Student": "طالب",
 "Rarely": "نادراً", "Occasionally": "أحياناً", "Daily": "يومياً", "Continuously": "باستمرار",
 "Main Building": "المبنى الرئيسي", "Engineering Building": "مبنى الهندسة", "Labs Building": "مبنى المختبرات",
 "Workshops": "الورش", "Library": "المكتبة", "Administration": "الإدارة", "Not specified": "غير محدد",
}


def lang():
    return st.session_state.get("lang", "en")


def t(k, **kw):
    s = UI[k][1 if lang() == "ar" else 0]
    return s.format(**kw) if kw else s


def v(x):
    """Translate a stored value (enum / option)."""
    if x is None:
        return "-"
    if lang() != "ar":
        return x
    return VAL.get(x) or config.PLACE_AR.get(x, x)


def cat_name(code):
    if not code:
        return "-"
    return f"{code} - " + (config.CATEGORY_AR[code] if lang() == "ar" else config.CATEGORIES[code])


def sub_name(code):
    if not code:
        return "-"
    return f"{code} - " + (config.SUBTYPE_AR[code] if lang() == "ar" else config.SUBTYPES[code][1])


def dept_name(code):
    if not code:
        return "-"
    return config.DEPARTMENTS[code][1 if lang() == "ar" else 0]

# ---- keys added for the design-matched UI ----
UI.update({
 "rep_L": ("Likelihood (reporter's estimate)", "الاحتمالية (تقدير المبلّغ)"), "rep_S": ("Severity (reporter's estimate)", "الشدة (تقدير المبلّغ)"),
 "not_sure": ("Not sure", "غير متأكد"),
 "lvl_model": ("Risk-level model (provisional)", "نموذج مستوى الخطورة (مؤقت)"),
 "lvl_model_warn": ("Trained on provisional labels generated by a likelihood × severity rule (synthetic, not expert-approved). Not an expert decision.",
                    "مدرَّب على تصنيفات مؤقتة مولَّدة بقاعدة الاحتمالية × الشدة (اصطناعية وغير معتمدة من خبير). ليس قراراً خبيراً."),
 "lvl_model_none": ("No level suggestion: the reporter did not give both likelihood and severity.", "لا يوجد اقتراح للمستوى: لم يحدد المبلّغ الاحتمالية والشدة معاً."),
 "rep_desc": ("Description", "الوصف"),
 "org": ("University of Technology and Applied Sciences - Salalah", "جامعة التقنية والعلوم التطبيقية - صلالة"),
 "sys_name": ("Risk Management System", "نظام إدارة المخاطر"),
 "login": ("Login", "تسجيل الدخول"), "user_email": ("Username or Email", "اسم المستخدم أو البريد الإلكتروني"),
 "role": ("Role", "الدور"), "role_user": ("User", "مستخدم"), "role_adminx": ("Administrator", "مسؤول النظام"),
 "role_resp": ("Responsible Person", "الجهة المسؤولة"), "forgot": ("Forgot password?", "نسيت كلمة المرور؟"),
 "forgot_msg": ("Please contact the system administrator to reset your password.", "الرجاء التواصل مع مسؤول النظام لإعادة تعيين كلمة المرور."),
 "role_mismatch": ("This account does not have the selected role.", "هذا الحساب ليس له الدور المحدد."),
 "visitor_btn": ("Report a risk without logging in (visitor)", "الإبلاغ عن خطر دون تسجيل الدخول (زائر)"),
 "back_login": ("Login", "تسجيل الدخول"),
 "p_report": ("Report a Risk", "الإبلاغ عن خطر"), "p_myreports": ("My Reports", "بلاغاتي"),
 "p_reports": ("Reports", "البلاغات"), "p_users": ("Users", "المستخدمون"), "p_settings": ("Settings", "الإعدادات"),
 "p_assigned": ("Assigned Reports", "البلاغات المسندة إليّ"), "p_history": ("History", "السجل"),
 "risk_title": ("Risk Title", "عنوان الخطر"), "risk_type": ("Risk Type", "نوع الخطر"),
 "select_type": ("Not sure - let the AI suggest", "غير متأكد - اترك الذكاء الاصطناعي يقترح"),
 "loc_dept": ("Location / Department", "الموقع / القسم"), "date_time": ("Date and Time", "التاريخ والوقت"),
 "risk_desc": ("Risk Description", "وصف الخطر"), "attach_img": ("Attach Image (Optional)", "إرفاق صورة (اختياري)"),
 "submit_report": ("Submit Report", "إرسال البلاغ"), "cancel": ("Cancel", "إلغاء"),
 "more_details": ("Additional details (helps the AI)", "تفاصيل إضافية (تساعد الذكاء الاصطناعي)"),
 "recent": ("My Recent Reports", "بلاغاتي الأخيرة"), "recent_guest": ("Visitors can track a report with its code on the Track page.", "يمكن للزائر تتبع بلاغه برمز المتابعة في صفحة التتبع."),
 "need_title": ("Please enter a title.", "الرجاء إدخال عنوان."),
 "tbl_id": ("ID", "الرقم"), "tbl_title": ("Title", "العنوان"), "tbl_type": ("Risk Type", "نوع الخطر"),
 "tbl_loc": ("Location", "الموقع"), "tbl_by": ("Reported By", "مقدّم البلاغ"), "tbl_date": ("Date", "التاريخ"), "tbl_status": ("Status", "الحالة"),
 "showing": ("Showing {n} reports", "عرض {n} بلاغ"),
 "rep_details": ("Report Details", "تفاصيل البلاغ"), "img_prev": ("Image Preview", "معاينة الصورة"), "no_image": ("No image attached", "لا توجد صورة مرفقة"),
 "ai_suggest": ("AI Suggested Category and Priority (editable)", "تصنيف وأولوية مقترحة بالذكاء الاصطناعي (قابلة للتعديل)"),
 "risk_scoring": ("Risk scoring (likelihood × severity)", "تقييم الخطر (الاحتمالية × الشدة)"),
 "resp_dept": ("Responsible Department", "الجهة المسؤولة"),
 "approve_send": ("Approve and Send to Responsible", "اعتماد وإرسال إلى الجهة المسؤولة"), "return_user": ("Return to User", "إعادة إلى المستخدم"),
 "return_note": ("Reason for returning (shown to the user)", "سبب الإعادة (يظهر للمستخدم)"),
 "need_reason": ("Please write the reason first.", "الرجاء كتابة السبب أولاً."),
 "step1": ("Submitted", "تم الإرسال"), "step2": ("Admin Approval", "اعتماد المسؤول"), "step3": ("Responsible Action", "إجراء الجهة المسؤولة"), "step4": ("Final Decision", "القرار النهائي"),
 "final_dec": ("Final Decision", "القرار النهائي"), "resp_reply": ("Responsible Reply", "رد الجهة المسؤولة"), "sol_note": ("Solution / Action Note", "الحل / الإجراء المتخذ"),
 "no_reply": ("No reply yet.", "لا يوجد رد بعد."), "close_report": ("Close Report", "إغلاق البلاغ"), "more_action": ("Request More Action", "طلب إجراء إضافي"),
 "more_note": ("What more is needed?", "ما المطلوب إضافياً؟"),
 "assigned_report": ("Assigned Report", "البلاغ المسند"), "admin_note_l": ("Admin Note", "ملاحظة المسؤول"),
 "your_response": ("Your Response", "ردّك"), "solution": ("Solution / Actions Taken", "الحل / الإجراءات المتخذة"),
 "exp_date": ("Expected Completion Date", "تاريخ الإنجاز المتوقع"), "evidence": ("Attach Evidence (Optional)", "إرفاق دليل (اختياري)"),
 "send_admin": ("Send to Admin", "إرسال إلى المسؤول"), "tab_new": ("New", "جديد"), "tab_prog": ("In Progress", "قيد المعالجة"), "tab_done": ("Done", "تم"),
 "need_solution": ("Please describe the solution / actions taken.", "الرجاء وصف الحل / الإجراءات المتخذة."),
 "add_user": ("Add user", "إضافة مستخدم"), "full_name": ("Full name", "الاسم الكامل"), "create": ("Create", "إنشاء"),
 "del_user": ("Delete selected user", "حذف المستخدم المحدد"), "user_exists": ("Username already exists.", "اسم المستخدم موجود مسبقاً."),
 "user_created": ("User created.", "تم إنشاء المستخدم."), "need_all": ("Fill all fields.", "املأ جميع الحقول."),
 "cant_del_self": ("You cannot delete your own account.", "لا يمكنك حذف حسابك."),
 "tbl_name": ("Name", "الاسم"), "tbl_username": ("Username", "اسم المستخدم"), "tbl_role": ("Role", "الدور"),
 "settings_ai": ("AI model & training data", "نموذج الذكاء الاصطناعي وبيانات التدريب"),
 "history_empty": ("No history yet.", "لا يوجد سجل بعد."), "returned_msg": ("Returned to you:", "أُعيد إليك:"),
 "pick_row": ("Select a report from the table.", "اختر بلاغاً من الجدول."),
 "sent_ok": ("Done.", "تم."),
})
VAL.update({
 "Sent to Responsible": "أُرسل للجهة المسؤولة", "In Progress": "قيد المعالجة", "Done": "تم", "Returned": "أُعيد للمستخدم",
 "Submitted": "تم الإرسال",
})
