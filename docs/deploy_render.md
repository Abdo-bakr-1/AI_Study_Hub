# 🚀 نشر المشروع على Render — دليل خطوة بخطوة

> هذا الدليل يشرح كيف نُشر "AI Study Hub" على منصة Render (مجاني).
> كل ملفات النشر جاهزة في المشروع — المطلوب فقط اتباع الخطوات.

---

## 1) ما تم تجهيزه في الكود (من أجلك)

| الملف | وظيفته |
|---|---|
| `requirements.txt` | أُضيف `gunicorn` (سيرفر الإنتاج) + `whitenoise` (خدمة الملفات الثابتة) |
| `Procfile` | أمر تشغيل التطبيق: `gunicorn config.wsgi:application` |
| `build.sh` | خطوة البناء: `collectstatic` ثم `migrate` تلقائيًا |
| `runtime.txt` | تثبيت Python 3.12.3 |
| `render.yaml` | **Blueprint** — ينشئ Web Service + PostgreSQL بضغطة واحدة |
| `config/settings.py` | دعم `DATABASE_URL` (يُحقنه Render تلقائيًا) + whitenoise + `SECURE_PROXY_SSL_HEADER` |

## 2) الخطوات على موقع Render

1. **ارفع الكود على GitHub** (أول commit موجود، لكن لسه محتاج push للتعديلات).
2. ادخل على [render.com](https://render.com) وسجّل (تستطيع التسجيل بحساب GitHub).
3. اضغط **New +** ← **Blueprint**.
4. اختر مستودع `AI_Study_Hub`.
5. Render سيقرأ `render.yaml` تلقائيًا وينشئ:
   - **Web Service** باسم `ai-study-hub`
   - **PostgreSQL database** باسم `ai-study-hub-db` (مجاني)
6. اضغط **Apply** وانتظر البناء (دقيقتان تقريبًا).

## 3) المتغيرات التي يجب ضبطها يدويًا

`render.yaml` يضبط كل شيء ما عدا سر واحد:

- **`AI_API_KEY`** ← ضعه يدويًا من لوحة Render:
  Dashboard → الخدمة `ai-study-hub` → **Environment** → **Edit** →
  أضف `AI_API_KEY` = مفتاح Groq الخاص بك.

> كل المتغيرات الأخرى (`SECRET_KEY` يتولد تلقائيًا، `DATABASE_URL` من قاعدة البيانات،
> `AI_MODEL`، `DEBUG=False`...) مضبوطة من ملف `render.yaml`.

## 4) بعد النشر

- ستجد رابط الموقع مثل: `https://ai-study-hub.onrender.com`
- إذا غيّرت اسم الخدمة، حدّث `ALLOWED_HOSTS` بنفس الرابط في Environment.
- **البريد (verification / reset):** إعدادات console تطبع الروابط في **Logs** بالداشبورد.

## 5) ملاحظات مهمة

- **قاعدة البيانات** المجانية على Render تنتهي بعد 30 يومًا (كافية للعرض).
- **الملفات المرفوعة (صور البروفايل/الملاحظات)** تُحذف عند كل إعادة نشر لأن نظام
  ملفات Render مؤقت — لا داعي لخريطة تخزين خارجية للعرض.
- **لا تكشف أبدًا** `SECRET_KEY` أو `AI_API_KEY` في الكود أو في README.

---

*تم تجهيزه في 2026-08-10 أثناء تجهيز المشروع للنشر على Render.*
