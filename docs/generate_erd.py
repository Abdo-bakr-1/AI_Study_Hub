#!/usr/bin/env python3
"""Generate a portrait (A4-style) crow's-foot ERD for AI Study Hub.

Reads the model schema documented in the Django apps and draws a
vertical/portrait ERD with Pillow, colored per feature module.

Run:  python generate_erd.py   (or from repo root: python docs/generate_erd.py)
Output: docs/erd.png
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
DEJAVU = "/usr/share/fonts/truetype/dejavu"
F_TITLE = ImageFont.truetype(f"{DEJAVU}/DejaVuSans-Bold.ttf", 52)
F_SUB = ImageFont.truetype(f"{DEJAVU}/DejaVuSans.ttf", 25)
F_TABNAME = ImageFont.truetype(f"{DEJAVU}/DejaVuSans-Bold.ttf", 23)
F_FIELD = ImageFont.truetype(f"{DEJAVU}/DejaVuSans.ttf", 18)
F_TAG = ImageFont.truetype(f"{DEJAVU}/DejaVuSans-Bold.ttf", 13)
F_BADGE = ImageFont.truetype(f"{DEJAVU}/DejaVuSans-Bold.ttf", 21)
F_CARD = ImageFont.truetype(f"{DEJAVU}/DejaVuSans-Bold.ttf", 19)
F_LEGEND = ImageFont.truetype(f"{DEJAVU}/DejaVuSans.ttf", 21)
F_BAR = ImageFont.truetype(f"{DEJAVU}/DejaVuSans-Bold.ttf", 18)
F_BARFIELD = ImageFont.truetype(f"{DEJAVU}/DejaVuSans.ttf", 18)

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
INK = (44, 62, 80)          # #2C3E50 dark text
MUTED = (93, 109, 126)      # #5D6D7E
EDGE = (127, 140, 141)      # #7F8C8D
SPINE = (189, 195, 199)     # #BDC3C7
USER_HDR = (44, 62, 80)
USER_BG = (236, 240, 241)

MODULES = {
    "accounts":   {"hdr": (41, 128, 185),  "bg": (234, 242, 248)},   # blue
    "planner":    {"hdr": (39, 174, 96),   "bg": (233, 247, 239)},   # green
    "notes":      {"hdr": (214, 137, 16),  "bg": (252, 243, 227)},   # amber
    "resources":  {"hdr": (192, 57, 43),   "bg": (251, 234, 233)},   # red
    "ai":         {"hdr": (108, 92, 231),  "bg": (239, 237, 252)},   # indigo
    "core":       {"hdr": (127, 140, 141), "bg": (240, 243, 244)},   # gray
}

# ---------------------------------------------------------------------------
# Data model (mirrors the Django models exactly)
# ---------------------------------------------------------------------------
# Each table: (name, module, [ (field, type, flags) ])
# flags: {"pk"} primary key, {"fk"} foreign key, {"u"} unique
PK = {"pk"}
FK = {"fk"}
PK_FK = {"pk", "fk"}

TABLES = [
    # ---- Accounts ------------------------------------------------------
    ("accounts_profile", "accounts", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("full_name", "varchar(150)", set()),
        ("bio", "text", set()),
        ("profile_picture", "image", set()),
        ("date_of_birth", "date", set()),
        ("phone", "varchar(30)", set()),
        ("location", "varchar(120)", set()),
        ("created_at", "datetime", set()),
        ("updated_at", "datetime", set()),
    ]),
    ("accounts_emailverification", "accounts", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("token", "varchar(64)", {"u"}),
        ("is_verified", "bool", set()),
        ("created_at", "datetime", set()),
        ("expires_at", "datetime", set()),
    ]),
    ("accounts_passwordresettoken", "accounts", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("token", "varchar(64)", {"u"}),
        ("is_used", "bool", set()),
        ("created_at", "datetime", set()),
        ("expires_at", "datetime", set()),
    ]),

    # ---- Planner --------------------------------------------------------
    ("planner_taskcategory", "planner", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("name", "varchar(80)", set()),
        ("created_at", "datetime", set()),
    ]),
    ("planner_task_categories", "planner", [   # M2M join table
        ("id", "int", PK),
        ("taskcategory_id", "FK → planner_taskcategory", FK),
        ("task_id", "FK → planner_task", FK),
    ]),
    ("planner_task", "planner", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("title", "varchar(200)", set()),
        ("description", "text", set()),
        ("due_date", "date", set()),
        ("priority", "varchar(10)", set()),
        ("status", "varchar(10)", set()),
        ("is_completed", "bool", set()),
        ("created_at", "datetime", set()),
        ("updated_at", "datetime", set()),
    ]),

    # ---- Notes ----------------------------------------------------------
    ("notes_notecategory", "notes", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("name", "varchar(80)", set()),
        ("created_at", "datetime", set()),
    ]),
    ("notes_note_categories", "notes", [      # M2M join table
        ("id", "int", PK),
        ("notecategory_id", "FK → notes_notecategory", FK),
        ("note_id", "FK → notes_note", FK),
    ]),
    ("notes_note", "notes", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("title", "varchar(200)", set()),
        ("content", "text", set()),
        ("image", "image", set()),
        ("created_at", "datetime", set()),
        ("updated_at", "datetime", set()),
    ]),

    # ---- Resources ------------------------------------------------------
    ("resources_resourcecategory", "resources", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("name", "varchar(80)", set()),
        ("created_at", "datetime", set()),
    ]),
    ("resources_resource_categories", "resources", [  # M2M join table
        ("id", "int", PK),
        ("resourcecategory_id", "FK → resources_resourcecategory", FK),
        ("resource_id", "FK → resources_resource", FK),
    ]),
    ("resources_resource", "resources", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("title", "varchar(200)", set()),
        ("description", "text", set()),
        ("link", "url(500)", set()),
        ("resource_type", "varchar(20)", set()),
        ("thumbnail", "image", set()),
        ("created_at", "datetime", set()),
        ("updated_at", "datetime", set()),
    ]),

    # ---- AI Assistant ---------------------------------------------------
    ("ai_assistant_conversation", "ai", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("title", "varchar(200)", set()),
        ("created_at", "datetime", set()),
        ("updated_at", "datetime", set()),
    ]),
    ("ai_assistant_message", "ai", [
        ("id", "int", PK),
        ("conversation_id", "FK → ai_assistant_conversation", FK),
        ("sender", "varchar(10)", set()),
        ("message", "text", set()),
        ("created_at", "datetime", set()),
    ]),

    # ---- Core -----------------------------------------------------------
    ("core_activitylog", "core", [
        ("id", "int", PK),
        ("user_id", "FK → auth_user", FK),
        ("action", "varchar(20)", set()),
        ("content_type", "varchar(50)", set()),
        ("object_id", "int", set()),
        ("description", "varchar(255)", set()),
        ("created_at", "datetime", set()),
    ]),
]

# Relationship types for the module (spine) edges: table -> "1:1" or "1:N"
USER_EDGES = {
    "accounts_profile": "1:1",
    "accounts_emailverification": "1:N",
    "accounts_passwordresettoken": "1:N",
    "planner_taskcategory": "1:N",
    "planner_task": "1:N",
    "notes_notecategory": "1:N",
    "notes_note": "1:N",
    "resources_resourcecategory": "1:N",
    "resources_resource": "1:N",
    "ai_assistant_conversation": "1:N",
    "core_activitylog": "1:N",
}

# Vertical (intra-column) edges: (from_table, to_table, from_card, to_card)
VERT_EDGES = [
    ("planner_taskcategory", "planner_task_categories", "N", "1"),
    ("planner_task_categories", "planner_task", "1", "M"),
    ("notes_notecategory", "notes_note_categories", "N", "1"),
    ("notes_note_categories", "notes_note", "1", "M"),
    ("resources_resourcecategory", "resources_resource_categories", "N", "1"),
    ("resources_resource_categories", "resources_resource", "1", "M"),
    ("ai_assistant_conversation", "ai_assistant_message", "1", "N"),
]

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
W, H = 1800, 3000
PAD = 90
SPINE_LEFT, SPINE_RIGHT = 540, 1260
CX_LEFT, CX_RIGHT = 810, 1530
TAB_W = 500
TAB_GAP = 46
ROW_TOP = 380
ROW_GAP = 130
FIELD_H = 27
HDR_H = 34
TAB_PAD = 9

MODULE_LABEL = {
    "accounts": "Accounts",
    "planner": "Planner",
    "notes": "Notes",
    "resources": "Resources",
    "ai": "AI Assistant",
    "core": "Core",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def table_height(table):
    return HDR_H + len(table[2]) * FIELD_H + 2 * TAB_PAD


def draw_one(draw, x, y, horizontal):
    """Small circle marking the 'exactly one' end of an edge."""
    r = 4
    if horizontal:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=EDGE)
    else:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=EDGE)


def crow_foot(draw, tip, horizontal, outward):
    """Three-prong crow's foot. tip=(x,y) at the table edge; `outward` is
    +1 / -1 giving the direction the prongs fan toward the table."""
    if horizontal:  # stub runs left->right into a box; +1 = prongs go INTO box (right)
        d = outward * 12
        base = (tip[0] + d, tip[1])
        draw.line([tip, (base[0], base[1] - 10)], fill=EDGE, width=2)
        draw.line([tip, (base[0], base[1] + 10)], fill=EDGE, width=2)
        draw.line([tip, (base[0] + 5, base[1])], fill=EDGE, width=2)
    else:  # vertical edge running top->bottom into a box
        d = outward * 12
        base = (tip[0], tip[1] - d)
        draw.line([tip, (base[0] - 10, base[1])], fill=EDGE, width=2)
        draw.line([tip, (base[0] + 10, base[1])], fill=EDGE, width=2)
        draw.line([tip, (base[0], base[1] - 5)], fill=EDGE, width=2)


def draw_field_tags(draw, x1, y_center, flags):
    tags = []
    if "pk" in flags:
        tags.append(("PK", (230, 176, 0), (255, 255, 255)))
    if "fk" in flags:
        tags.append(("FK", (41, 128, 185), (255, 255, 255)))
    if "u" in flags:
        tags.append(("U", (39, 174, 96), (255, 255, 255)))
    x = x1
    for label, bg, fg in tags:
        w = draw.textlength(label, font=F_TAG) + 14
        x -= w
        draw.rounded_rectangle([x, y_center - 10, x + w, y_center + 10],
                               radius=4, fill=bg)
        tw = draw.textlength(label, font=F_TAG)
        draw.text((x + (w - tw) / 2, y_center - 6), label,
                  font=F_TAG, fill=fg)
        x -= 8
    return x - 8  # left edge available for the type text


def draw_table(draw, name, module, fields, x0, y0):
    w = TAB_W
    h = table_height((name, module, fields))
    colors = MODULES[module]
    x1 = x0 + w
    y1 = y0 + h

    # body
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=colors["bg"],
                           outline=colors["hdr"], width=2)
    # header
    draw.rounded_rectangle([x0, y0, x1, y0 + HDR_H], radius=10, fill=colors["hdr"])
    draw.rectangle([x0, y0 + HDR_H - 10, x1, y0 + HDR_H], fill=colors["hdr"])
    draw.text((x0 + 12, y0 + (HDR_H - 23) / 2), name, font=F_TABNAME, fill="white")

    # fields
    y = y0 + HDR_H + TAB_PAD
    margin = 12
    for fname, ftype, flags in fields:
        cy = y + FIELD_H / 2
        draw.text((x0 + margin, y + 1), fname, font=F_FIELD, fill=INK)
        # tags right-aligned
        type_x = draw_field_tags(draw, x1 - margin, cy, flags)
        draw.text((type_x, y + 1), ftype, font=F_FIELD, fill=MUTED, anchor="ra")
        y += FIELD_H
    return (x0, y0, x1, y1)


def draw_badge(draw, cx, y, label, color):
    tw = draw.textlength(label, font=F_BADGE)
    w = tw + 34
    x0, x1 = cx - w / 2, cx + w / 2
    draw.rounded_rectangle([x0, y - 17, x1, y + 17], radius=17, fill=color)
    draw.text((cx, y - 11), label, font=F_BADGE, fill="white", anchor="ma")
    return x0, x1, y - 17, y + 17


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def main():
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # --- Title -----------------------------------------------------------
    draw.text((W / 2, 55), "AI Study Hub", font=F_TITLE, fill=INK, anchor="ma")
    draw.text((W / 2, 118), "Relational Database Schema (ERD) — PostgreSQL",
              font=F_SUB, fill=MUTED, anchor="ma")
    draw.line([PAD, 152, W - PAD, 152], fill=SPINE, width=2)

    # --- Root entity bar (auth_user) --------------------------------------
    bar_y0, bar_y1 = 178, 306
    draw.rounded_rectangle([PAD, bar_y0, W - PAD, bar_y1], radius=14,
                           fill=USER_HDR)
    draw.text((PAD + 20, bar_y0 + 22), "auth_user", font=F_TITLE, fill="white")
    draw.text((PAD + 22, bar_y0 + 86),
              "Django User — root entity of the whole schema",
              font=F_SUB, fill=(200, 210, 218))
    # fields zone (right side of the bar)
    div_x = 560
    draw.line([div_x, bar_y0 + 16, div_x, bar_y1 - 16], fill=(70, 88, 105), width=2)
    bar_fields = [
        "id  PK", "username  U", "password", "email  U", "first_name",
        "last_name", "is_active", "is_staff", "date_joined", "last_login",
    ]
    fx, fy = div_x + 22, bar_y0 + 26
    for f in bar_fields:
        fw = draw.textlength(f, font=F_BARFIELD) + 20
        if fx + fw > W - PAD - 12:
            fx = div_x + 22
            fy += 42
        draw.rounded_rectangle([fx, fy, fx + fw, fy + 30], radius=6,
                               fill=(58, 78, 96))
        draw.text((fx + 10, fy + 4), f, font=F_BARFIELD, fill=(220, 228, 236))
        fx += fw + 12

    # --- Spines (user connection) ------------------------------------------
    spine_bottom = 2470
    draw.line([SPINE_LEFT, bar_y1, SPINE_LEFT, spine_bottom], fill=SPINE, width=3)
    draw.line([SPINE_RIGHT, bar_y1, SPINE_RIGHT, spine_bottom], fill=SPINE, width=3)

    # --- Compute table positions -------------------------------------------
    boxes = {}          # name -> (x0, y0, x1, y1)
    column = {}         # name -> cx
    # Rows of module stacks: row1 accounts|planner, row2 notes|resources,
    # row3 ai|core.  Each entry is (side, [table names in stack order]).
    rows = [
        ("L", ["accounts_profile", "accounts_emailverification",
               "accounts_passwordresettoken"]),
        ("R", ["planner_taskcategory", "planner_task_categories", "planner_task"]),
        ("L", ["notes_notecategory", "notes_note_categories", "notes_note"]),
        ("R", ["resources_resourcecategory", "resources_resource_categories",
               "resources_resource"]),
        ("L", ["ai_assistant_conversation", "ai_assistant_message"]),
        ("R", ["core_activitylog"]),
    ]
    y_top = {side: ROW_TOP for side in ("L", "R")}
    for i, (side, names) in enumerate(rows):
        cx = CX_LEFT if side == "L" else CX_RIGHT
        y = y_top[side]
        for tname in names:
            tbl = next(t for t in TABLES if t[0] == tname)
            h = table_height(tbl)
            x0 = cx - TAB_W / 2
            boxes[tname] = (x0, y, x0 + TAB_W, y + h)
            column[tname] = cx
            y += h + TAB_GAP
        y_top[side] = y - TAB_GAP
        # advance the opposite side too so both sides of a row stay aligned
        other = "R" if side == "L" else "L"
        if y_top[other] <= ROW_TOP:           # other side not placed yet
            y_top[other] = y_top[side]
        elif i % 2 == 1:                       # end of a visual row
            nxt = max(y_top["L"], y_top["R"]) + ROW_GAP
            y_top["L"] = y_top["R"] = nxt

    # --- Module regions (soft tinted grouping) ------------------------------
    def region_box(names):
        xs0 = min(boxes[n][0] for n in names)
        xs1 = max(boxes[n][2] for n in names)
        ys0 = min(boxes[n][1] for n in names) - 38
        ys1 = max(boxes[n][3] for n in names)
        return (xs0 - 18, ys0, xs1 + 18, ys1 + 18)

    # draw regions behind, per module (each module appears once)
    seen = set()
    for tname in boxes:
        module = next(t for t in TABLES if t[0] == tname)[1]
        if module in seen:
            continue
        seen.add(module)
        names = [n for n in boxes
                 if next(t for t in TABLES if t[0] == n)[1] == module]
        r = region_box(names)
        col = MODULES[module]
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle(r, radius=18, fill=col["bg"] + (170,))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(r, radius=18, outline=col["hdr"], width=2)

    # --- Table boxes --------------------------------------------------------
    for tname, (x0, y0, x1, y1) in boxes.items():
        tbl = next(t for t in TABLES if t[0] == tname)
        draw_table(draw, tbl[0], tbl[1], tbl[2], x0, y0)

    # --- Badges -------------------------------------------------------------
    seen = set()
    for tname, (x0, y0, x1, y1) in boxes.items():
        module = next(t for t in TABLES if t[0] == tname)[1]
        if module in seen:
            continue
        seen.add(module)
        cx = column[tname]
        y0 = boxes[tname][1]
        draw_badge(draw, cx, y0 - 38, MODULE_LABEL[module], MODULES[module]["hdr"])

    # --- Spine (user) edges --------------------------------------------------
    for tname, (x0, y0, x1, y1) in boxes.items():
        if tname not in USER_EDGES:
            continue
        card = USER_EDGES[tname]
        cx = column[tname]
        cy = (y0 + y1) / 2
        spine_x = SPINE_LEFT if cx < SPINE_RIGHT else SPINE_RIGHT
        draw.line([spine_x, cy, x0, cy], fill=EDGE, width=3)
        # 'many' at table end, 'one' at the spine
        if card == "1:1":
            draw_one(draw, spine_x, cy, True)
            draw_one(draw, x0, cy, True)
        else:
            draw_one(draw, spine_x, cy, True)
            crow_foot(draw, (x0, cy), True, +1)
        # cardinality tag, right-aligned to the spine (clear of the table box)
        tw = draw.textlength(card, font=F_CARD)
        draw.text((spine_x - tw - 10, cy - 22), card, font=F_CARD, fill=USER_HDR)

    # --- Vertical (intra-module) edges ----------------------------------------
    for fr, to, fcard, tcard in VERT_EDGES:
        x0f, y0f, x1f, y1f = boxes[fr]
        x0t, y0t, x1t, y1t = boxes[to]
        cx = (x0f + x1f) / 2
        draw.line([cx, y1f, cx, y0t], fill=EDGE, width=3)
        # 'many' at the bottom end, 'one' at the top end
        if fcard == "1":
            draw_one(draw, cx, y1f, False)
        else:
            crow_foot(draw, (cx, y1f), False, +1)
        if tcard == "1":
            draw_one(draw, cx, y0t, False)
        else:
            crow_foot(draw, (cx, y0t), False, -1)
        draw.text((cx, (y1f + y0t) / 2 - 10), f"{fcard} : {tcard}",
                  font=F_CARD, fill=USER_HDR, anchor="ma")

    # --- Legend ----------------------------------------------------------------
    ly = 2530
    draw.rounded_rectangle([PAD, ly, W - PAD, ly + 150], radius=14,
                           fill=(246, 247, 249), outline=SPINE, width=2)
    draw.text((PAD + 24, ly + 14), "Modules", font=F_LEGEND, fill=INK)
    lx = PAD + 24
    for key in ("accounts", "planner", "notes", "resources", "ai", "core"):
        col = MODULES[key]
        draw.rounded_rectangle([lx, ly + 52, lx + 26, ly + 78], radius=4,
                               fill=col["hdr"])
        draw.text((lx + 36, ly + 52), MODULE_LABEL[key], font=F_LEGEND, fill=INK)
        lx += 36 + draw.textlength(MODULE_LABEL[key], font=F_LEGEND) + 30

    draw.text((W - PAD - 24, ly + 14), "Relationships", font=F_LEGEND,
              fill=INK, anchor="ra")
    rx = W - PAD - 24
    rels = [("1 : 1", "exactly one"), ("1 : N", "one-to-many"),
            ("N : M", "many-to-many")]
    for card, desc in rels:
        tw = draw.textlength(card, font=F_CARD)
        rx -= (tw + 10)
        draw.text((rx, ly + 52), card, font=F_CARD, fill=USER_HDR)
        draw.text((rx + tw + 12, ly + 54), desc, font=F_LEGEND, fill=MUTED)
        rx -= (draw.textlength(desc, font=F_LEGEND) + 38)

    draw.text((W / 2, ly + 118), "PK primary key · FK foreign key · U unique",
              font=F_LEGEND, fill=MUTED, anchor="ma")

    # --- Footer ---------------------------------------------------------------
    draw.text((W / 2, H - 34), "AI Study Hub — ITI Final Project",
              font=F_LEGEND, fill=MUTED, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erd.png")
    img.save(out)
    print(f"Saved {out} ({W}x{H})")


if __name__ == "__main__":
    main()
