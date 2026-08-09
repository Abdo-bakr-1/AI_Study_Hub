# تقرير مشروع AI Study Hub — كل اللي اتعمل في المشروع

> وثيقة تحضيرية للمناقشة: بتلخص فكرة المشروع، البنية، كل الميزات، أعمال الإصلاح والتدقيق،
> وشات الذكاء الاصطناعي — عشان تقدر تشرح "عملت إيه في المشروع" بثقة.

---

## 1) فكرة المشروع (Elevator Pitch)

مشروع **AI Study Hub**: منصة ويب لإدارة الدراسة بشل متكامل — الطالب يعمل حساب، يشوف
Dashboard فيه إحصائياته ورسوم بيانية، ينظم **مهامه** (Study Planner) و**ملاحظاته** (Notes)
و**موارد التعلم** (Resources)، وكمان يتكلم مع **مساعد ذكاء اصطناعي** مدمج عشان يساعده في
الشرح والإجابات ووضع خطط المذاكرة.

مبني بـ **Django (MVT) + PostgreSQL**، بدون REST Framework وبدون أي Framework للفرونت —
الواجهات بـ **Django Templates + HTML/CSS + Vanilla JavaScript**.

---

## 2) التقنيات المستخدمة

| التقنية | الاستخدام |
|---|---|
| Python 3.12 | لغة البرمجة |
| Django 5.1 (MVT) | إطار العمل الأساسي (Models / Views / Templates) |
| PostgreSQL | قاعدة البيانات الرئيسية |
| django-environ | قراءة الإعدادات الحساسة من `.env` |
| requests | التواصل مع مزوّد الذكاء الاصطناعي |
| reportlab | تصدير الملاحظات PDF |
| Pillow | رفع الصور (صورة البروفايل) |
| Chart.js (CDN) | الرسوم البيانية في الداشبورد |
| HTML/CSS/JS | الواجهات (بدون أي framework) |

---

## 3) بنية المشروع

```
Project/
├── manage.py
├── requirements.txt
├── .env.example          # كوبي لـ .env (الأسرار متخزناش في الكود)
├── config/               # إعدادات المشروع + الـ urls الرئيسية
├── core/                 # الصفحة الرئيسية + ActivityLog (سجل النشاط) + معالجات الأخطاء
├── accounts/             # التسجيل / الدخول / البروفايل / التحقق من الإيميل / استرجاع كلمة المرور
├── dashboard/            # صفحة الإحصائيات والرسوم البيانية
├── planner/              # المهام (Tasks + Categories) — CRUD كامل
├── notes/                # الملاحظات + البحث المباشر + تصدير PDF
├── resources/            # موارد التعلم + روابط خارجية آمنة
├── ai_assistant/         # محادثات الـ AI + service layer + context
├── templates/            # كل صفحات HTML + صفحات الأخطاء (403/404/500)
├── static/               # CSS + JS (charts / chat / search ...)
├── media/                # الصور المرفوعة
└── docs/                 # التوثيق
```

كل تطبيق مقسّم نظيف: `models.py / forms.py / views.py / urls.py / admin.py`.
منطق الـ AI معزول لوحده في `ai_assistant/services.py`.

---

## 4) قاعدة البيانات (الموديلات)

| التطبيق | الموديل | أهم الحقول |
|---|---|---|
| accounts | `Profile` | full_name, bio, profile_picture, date_of_birth, phone, location |
| accounts | `EmailVerification` | token, is_verified, expires_at |
| accounts | `PasswordResetToken` | token, is_used, expires_at |
| core | `ActivityLog` | user, action, content_type, description, created_at |
| planner | `Task` | title, description, due_date, priority (Low/Med/High), status, is_completed |
| planner | `TaskCategory` | name (لكل مستخدم) |
| notes | `Note` | title, content, image, categories (M2M) |
| notes | `NoteCategory` | name (لكل مستخدم) |
| resources | `Resource` | title, description, link, resource_type, thumbnail |
| resources | `ResourceCategory` | name (لكل مستخدم) |
| ai_assistant | `Conversation` | title, user |
| ai_assistant | `Message` | sender (user/assistant), message, conversation (FK) |

**ملاحظة مهمة للنقاش:** كل موديل مربوط بـ `user` (ForeignKey) — وكل الـ Querysets متفلترة
بـ `request.user`، يعني **عزل كامل بين بيانات المستخدمين**: أي مستخدم مش شايف غير بياناته هو،
وأي محاولة للوصول لبيانات حد تاني بترجع 404. الـ Categories مكررة per-user مش مشتركة.

---

## 5) الميزات بالتفصيل

### 🔐 المصادقة (accounts)
- Register / Login / Logout
- صفحة بروفايل + رفع صورة + تعديل البيانات
- تغيير كلمة المرور
- **التحقق من الإيميل** (token + انتهاء صلاحية)
- **استرجاع كلمة المرور** (token)
- رسائل التحقق بتتطبع في الـ terminal (Console Email Backend) في التطوير

### 📊 الداشبورد
- كروت إحصائيات: إجمالي / مكتمل / معلّق من المهام، عدد الملاحظات، عدد الموارد
- **رسوم بيانية Chart.js**: مكتمل vs معلّق، المهام حسب الأولوية، الملاحظات حسب التصنيف
- سجل النشاط الحديث (ActivityLog)
- إجراءات سريعة (إضافة مهمة / ملاحظة / مورد / فتح الـ AI)

### 🗓️ المهام (planner) — CRUD كامل
- إضافة / تعديل / حذف / عرض + mark complete/uncomplete
- الأولوية (Low/Medium/High) + التصنيفات (M2M) + الموعد النهائي
- فلاتر حسب الحالة والأولوية والتصنيف + pagination

### 📝 الملاحظات (notes) — CRUD كامل
- **بحث مباشر (Live Search) بجافاسكريبت** في العنوان والمحتوى
- فلاتر حسب التصنيف + pagination
- **تصدير PDF** بكل ملاحظات المستخدم (reportlab)

### 🔗 الموارد (resources) — CRUD كامل
- نوع المورد (Article/Video/Documentation/Course/Book/Other)
- رابط خارجي + **معالجة آمنة** (فتح في tab جديد، تحقق من الرابط)
- فلاتر + pagination

### 🤖 شات الـ AI (`/ai-chat/`)
- واجهة شات حديثة: محادثات متعددة لكل مستخدم، فقاعات user/AI، حالة تحميل وأخطاء
- **عزل بين المستخدمين**: كل واحد شايف محادثاته هو بس
- **Service layer** معزول في `ai_assistant/services.py` — كل تواصل مع مزوّد الـ AI هناك
- **Context ذكي اختياري**: الـ AI بيستقبل ملخص لبيانات المستخدم نفسه (مهام معلّقة قرب موعدها،
  ملاحظات حديثة) من `context.py` — مثلاً: "إيه المهام اللي مستحقة الأسبوع ده؟"
- يدعم أي مزوّد **OpenAI-compatible** (OpenAI / Groq / OpenRouter / local)
- **Offline fallback**: لو مفيش API key، بيرد بردود جاهزة عشان الشات يفضل شغال في التطوير

### 🎨 عام
- Dark mode toggle (بيتحفظ في localStorage)
- تصميم Responsive (موبايل → ديسكتوب)
- صفحات أخطاء ودية 403 / 404 / 500
- Django admin لكل الموديلات
- حماية: CSRF، فحوصات دخول، ملكية البيانات، الأسرار في `.env`

---

## 6) أهم جزء للنقاش: تدقيق المشروع وإصلاح 9 مشاكل

ده أهم جزء يفرق في المناقشة. المشروع اتعرض **لتدقيق كامل** (Project Audit) وقبل أي إصلاح
اتحدد الـ Root Cause، واتصلح **9 مشاكل** من غير ما نتخلى عن أي ميزة ومن غير ما نغير
المعمارية. دي قايمة بالمشاكل واللي اتعمل فيها:

### [أ] أخطاء بتبوّظ الإنتاج (Production-breaking)
1. **صفحات الأخطاء**: `core/views.py` كان بيشاور على قوالب
   `errors/404.html / 403.html / 500.html` — **مش موجودة**! والملفات الحقيقية في
   `templates/{404,403,500}.html`. مع `DEBUG=False` أي خطأ كان بيرمي خطأ تاني
   (TemplateDoesNotExist). ✅ **الإصلاح**: تصحيح أسماء القوالب في `core/views.py`.

2. **`templates/notes/note_list.html`**: بيستخدم `{% static %}` في بلوك `extra_js`
   **من غير `{% load static %}`** → صفحة `/notes/` كانت بترمي 500.
   ✅ **الإصلاح**: إضافة `{% load static %}`. (الدرس: `manage.py check` مش بيلمّش ده،
   لازم تعرض الصفحة فعليًا).

### [ب] أخطاء وظيفية
3. **رسوم الداشبورد كانت فاضية دايماً**: `dashboard/views.py` كان بيبعت JSON **متدرج**
   (nested) لكن `charts.js` بيقرأ **مفاتيح مسطّحة** (completed_tasks, pending_tasks,
   priority_low/medium/high, notes_categories...). النتيجة: كل الرسوم "No data yet."
   ✅ **الإصلاح**: توحيد المفاتيح في `dashboard/views.py` عشان تطابق `charts.js`.

4. **تاريخ محادثة الـ AI**: كان بيستبعد **كل رسالة قديمة** نصها مطابق للرسالة الجديدة،
   بدل ما يستبعد الرسالة اللي اتضافت لسه بس → تكرار نفس السؤال كان بيسقط رسائل قديمة
   من سياق الـ AI. ✅ **الإصلاح**: الاستبعاد بالـ pk بتاع الرسالة الجديدة فقط
   في `ai_assistant/views.py`.

5. **`smoke_test.py`**: كان بيستخدم `django.test.Client` اللي بيبعت host اسمه
   `testserver` مش موجود في `ALLOWED_HOSTS` → كل طلب بيرجع 400. وكمان فيه **رابطين غلط**:
   `/export/notes/pdf/` (الصحيح `/notes/export/pdf/`) و `/ai-chat/new/send/` (الصحيح
   `/ai-chat/send/`). ✅ **الإصلاح**: إضافة `testserver` لـ ALLOWED_HOSTS + تصحيح الرابطين.

### [ج] مشاكل أمنية
6. **Open Redirect في تسجيل الدخول**: باراميتر `?next=` كان بيتحط مباشرة في `redirect()` —
   يعني بعد الدخول يوصلك لموقع خارجي خبيث (اتتحقق منها فعلًا). ✅ **الإصلاح**:
   فحص الـ `next` بحيث ميقبلش غير مسارات داخلية (مش مواقع خارجية) في `accounts/views.py`.

7. **ثغرة XSS مخزّنة في الداشبورد**: `{{ charts_json|safe }}` جوه `<script>` — لو اسم
   تصنيف فيه `</script><script>...` ممكن يكسر الـ JSON ويحقن كود. ✅ **الإصلاح**:
   استخدام فلتر `json_script` في `templates/dashboard/home.html` (طريقة آمنة رسميًا).

### [د] مشاكل بسيطة
8. **إعدادات DEBUG متناقضة** في `config/settings.py`: `environ.Env(DEBUG=(bool, False))`
   مقابل `env.bool("DEBUG", default=True)` — لو `.env` ناقص كان هيشتغل بوضع التطوير.
   ✅ **الإصلاح**: الافتراضي بقى `False`.

9. **صورة الأفاتار مكسورة**: `Profile.image_url` كان بيشاور على
   `/static/images/default-avatar.svg` **مش موجود**. ✅ **الإصلاح**: إنشاء
   `static/images/default-avatar.svg`.

### الملفات اللي اتغيرت (8 ملفات + ملف جديد)
```
core/views.py                  → تصحيح أسماء قوالب الأخطاء
templates/notes/note_list.html → إضافة {% load static %}
dashboard/views.py             → مفاتيح مسطحة متوافقة مع charts.js
templates/dashboard/home.html  → json_script (حماية XSS)
ai_assistant/views.py          → استبعاد الرسالة بالـ pk
accounts/views.py              → حماية الـ open redirect
config/settings.py             → DEBUG الافتراضي False
smoke_test.py                  → إصلاح host + الروابط
static/images/default-avatar.svg  (جديد)
```

### الأوامر والتجارب اللي اتنفذت للتحقق
- `python manage.py check` → نظيف (0 مشاكل)
- `python manage.py makemigrations --check --dry-run` → مفيش تغييرات ناقصة
- `python manage.py test` → 0 تيستات (كل tests.py placeholder)
- `python smoke_test.py` → كل الصفحات 200، تصدير PDF → application/pdf، AI → application/json
- **اختبار وظيفي يدوي**: CRUD كامل للمهام/الملاحظات/الموارد + عزل المستخدمين
  (وصول مستخدم لبيانات غيره → 404 صح)
- **اختبار وضع الإنتاج (DEBUG=False)**: صفحات الأخطاء 403/404/500 بتشتغل،
  الـ open redirect مقفول، JSON الرسوم فيه المفاتيح الصح

---

## 7) ربط شات الـ AI بـ Groq (آخر إضافة)

الشات كان شغال بـ **Offline fallback** (ردود جاهزة) عشان مفيش API key. آخر حاجة في المشروع:
- اتضاف **Groq API key** في `.env` — Groq مزوّد مجاني سريع وOpenAI-compatible
- `AI_API_BASE_URL=https://api.groq.com/openai/v1`
- `AI_MODEL=llama-3.3-70b-versatile` (أقوى موديل مجاني على Groq)
- **اتعمل اختبار حقيقي**: طلب تجريبي لـ Groq رجّع رد سليم (`hello from groq`) ✅
- السيرفر اتعمل له restart

النتيجة: الشات دلوقتي بيرد **ردود ذكية حقيقية** بدل الردود الجاهزة.

---

## 8) مشاكل متبقية (غير مانعة — جاهزة كنقطة نقاش)

1. **مفيش automated tests** — كل `tests.py` مجرد placeholder ("Ran 0 tests")
2. `docs/` كان فاضي رغم إن README بيشاور على `docs/erd.png` و `docs/ai_study_hub_backup.sql`
   (مش متخليين حاجة)
3. `templates/includes/pagination.html` كود ميت (غير مستخدم — كل template بيعمل pagination
   لوحده)
4. `Resource.thumbnail` موجود في الموديل والفورم بس **مش مترندّر** في القوالب
5. التحقق من صورة البروفايل بيفحص الحجم بس (الـ README مدّعي type+size)
6. `.env` فيه SECRET_KEY وDB password للديف فقط (git-ignored) — **يتبدلوا قبل أي ديبلاي حقيقي**

---

## 9) طريقة التشغيل

```bash
source venv/bin/activate
python manage.py runserver
```

افتح http://127.0.0.1:8000/
- `/` → التسجيل/الدخول → `/dashboard/`
- الشات: `/ai-chat/`
- الأدمن: `/admin/`

متطلبات مسبقة: PostgreSQL شغال + قاعدة بيانات `ai_study_hub` + ملف `.env`.

---

## 10) أسئلة متوقعة في المناقشة + أجوبتها

**س: ليه اخترت Django من غير DRF؟**
ج: ده مشروع تدريب على الـ MVT الأساسي — مفيش حاجة محتاجة REST API. كل الصفحات
Server-rendered بـ Django Templates، والاستجابات الأجاكس (زي الشات) بتبعت JSON عادي.

**س: إزاي ضمنت أمان بيانات المستخدمين؟**
ج: كل موديل مربوط بـ `user`، وكل view بتفلتر بـ `request.user`، فمفيش حاجة تسقط
بحاجة غيره. وكمان بعد التدقيق: قفلنا ثغرة Open Redirect في اللوجين وثغرة XSS
في الداشبورد.

**س: إزاي الشات بيشتغل؟**
ج: Service layer معزول (services.py) بيكلم أي مزوّد OpenAI-compatible. لو مفيش
API key بيقع على offline fallback عشان الشات يفضل شغال في التطوير. وكمان بيبعت
Context ببيانات المستخدم نفسه لو سأل عن مهامه.

**س: إيه أكتر حاجة صعبة واجهتك؟**
ج: ثغرة الـ XSS في الداشبورد وثغرة Open Redirect في اللوجين — دول محتاجين فهم
عميق للـ security. وبرضه الـ mismatch بين JSON الداشبورد وcharts.js اللي كان
بخلي الرسوم فاضية.

**س: إيه خططك المستقبلية للمشروع؟**
ج: إضافة automated tests، عرض Resource.thumbnail، استرجاع كلمة المرور بـ SMTP
حقيقي، وتفعيل الـ AI مع Context أكتر تفصيلاً.

---

*تم إنشاء التقرير بتاريخ 2026-08-10 — محدّث بآخر تعديلات المشروع (تدقيق + إصلاحات + ربط Groq).*
