"""
Ecotech-12 Industries Association — Member Directory PDF generator.
Corporate / industrial aesthetic: navy + gold, A4.
"""
import csv
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------- Theme ----------------
NAVY      = HexColor('#0F2A4A')
NAVY_DARK = HexColor('#081B33')
GOLD      = HexColor('#C9A961')
GOLD_DARK = HexColor('#A8893F')
INK       = HexColor('#1A1A1A')
GREY_TXT  = HexColor('#5A6470')
GREY_LINE = HexColor('#D8DEE5')
BG_TINT   = HexColor('#F4F6F9')
PAPER     = HexColor('#FBFAF6')
ACCENT    = HexColor('#B23A48')

PAGE_W, PAGE_H = A4
MARGIN = 18*mm

# ---------------- CSV parsing ----------------
INPUT = '/sessions/keen-charming-dijkstra/mnt/uploads/LIST OF MEMEBERS ECOTECH 12 - List of members.csv'

def clean(s):
    if s is None: return ''
    return re.sub(r'\s+', ' ', s).strip()

def parse_members():
    rows = []
    with open(INPUT, 'r', encoding='utf-8') as f:
        for r in csv.reader(f):
            rows.append([clean(c) for c in r])
    # skip 4 header rows
    data_rows = rows[4:]
    members = []   # list of dicts: plot, name, contacts:[(person,phone)]
    current = None
    for row in data_rows:
        if len(row) < 7:
            row = row + ['']*(7-len(row))
        sr, plot, name, plot2, prefix, person, phone = row[:7]
        plot_val = plot or plot2
        person = person.strip()
        phone = phone.strip()
        # if both plot and name are empty, this is a continuation line for previous member
        if not plot_val and not name:
            if current and (person or phone):
                current['contacts'].append((person, phone))
            continue
        # new member row
        if current is not None:
            members.append(current)
        current = {
            'plot': plot_val,
            'name': name,
            'contacts': []
        }
        if person or phone:
            current['contacts'].append((person, phone))
    if current is not None:
        members.append(current)
    # normalize name "Cancelled" → vacant
    for m in members:
        if m['name'].lower() in ('cancelled', 'cancelled ', ''):
            pass
    return members

# ---------------- Drawing helpers ----------------
def draw_geo_pattern(c, x, y, w, h, color, opacity=0.08):
    c.saveState()
    c.setFillColor(color)
    c.setFillAlpha(opacity)
    c.setStrokeColor(color)
    c.setStrokeAlpha(opacity)
    step = 10*mm
    for i in range(int(w/step)+2):
        for j in range(int(h/step)+2):
            cx = x + i*step
            cy = y + j*step
            if (i+j) % 2 == 0:
                c.circle(cx, cy, 1.2, stroke=0, fill=1)
            else:
                c.rect(cx-0.6, cy-0.6, 1.2, 1.2, stroke=0, fill=1)
    c.restoreState()

def draw_corner_marks(c):
    """Subtle gold corner ornaments."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    L = 14*mm
    # top-left
    c.line(MARGIN, PAGE_H-MARGIN, MARGIN+L, PAGE_H-MARGIN)
    c.line(MARGIN, PAGE_H-MARGIN, MARGIN, PAGE_H-MARGIN-L)
    # top-right
    c.line(PAGE_W-MARGIN, PAGE_H-MARGIN, PAGE_W-MARGIN-L, PAGE_H-MARGIN)
    c.line(PAGE_W-MARGIN, PAGE_H-MARGIN, PAGE_W-MARGIN, PAGE_H-MARGIN-L)
    # bottom-left
    c.line(MARGIN, MARGIN, MARGIN+L, MARGIN)
    c.line(MARGIN, MARGIN, MARGIN, MARGIN+L)
    # bottom-right
    c.line(PAGE_W-MARGIN, MARGIN, PAGE_W-MARGIN-L, MARGIN)
    c.line(PAGE_W-MARGIN, MARGIN, PAGE_W-MARGIN, MARGIN+L)

def draw_page_chrome(c, page_label, section_label):
    """Header/footer used on directory pages. page_label is a string."""
    # Top band
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H-12*mm, PAGE_W, 12*mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, PAGE_H-13*mm, PAGE_W, 1*mm, stroke=0, fill=1)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 9)
    c.drawString(MARGIN, PAGE_H-8*mm, 'ECOTECH-12 INDUSTRIES ASSOCIATION')
    c.setFont('Helvetica', 8)
    c.setFillColor(GOLD)
    c.drawRightString(PAGE_W-MARGIN, PAGE_H-8*mm, section_label.upper())
    # Footer
    c.setFillColor(GREY_TXT)
    c.setFont('Helvetica', 7.5)
    c.drawString(MARGIN, 10*mm, 'Member Directory  ·  Greater Noida')
    c.drawRightString(PAGE_W-MARGIN, 10*mm, f'Page {page_label}')
    c.setStrokeColor(GREY_LINE)
    c.setLineWidth(0.3)
    c.line(MARGIN, 13*mm, PAGE_W-MARGIN, 13*mm)

# ---------------- Shared helpers for new pages ----------------
def _wrap(text, font, size, max_w, c):
    """Word-wrap a string of text against pdf string widths. Returns list of lines."""
    if not text: return []
    out_lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split()
        cur = ''
        for w in words:
            trial = (cur + ' ' + w).strip()
            if c.stringWidth(trial, font, size) <= max_w:
                cur = trial
            else:
                if cur: out_lines.append(cur)
                cur = w
        out_lines.append(cur)
    return out_lines

def _roman(n):
    table = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),
             (50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
    out = ''
    for v, s in table:
        while n >= v:
            out += s; n -= v
    return out

def page_header(c, eyebrow, title, subtitle=None):
    """Standard heading frame on a paper page. Returns y where body content starts."""
    c.setFillColor(PAPER); c.rect(0,0,PAGE_W,PAGE_H,stroke=0,fill=1)
    draw_corner_marks(c)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-12*mm, eyebrow.upper())
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 28)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-26*mm, title)
    c.setStrokeColor(GOLD); c.setLineWidth(1.2)
    c.line(MARGIN+2*mm, PAGE_H-MARGIN-30*mm, MARGIN+22*mm, PAGE_H-MARGIN-30*mm)
    y = PAGE_H-MARGIN-40*mm
    if subtitle:
        c.setFillColor(GREY_TXT); c.setFont('Helvetica', 10)
        c.drawString(MARGIN+2*mm, y, subtitle)
        y -= 14
    return y - 4

def page_footer_label(c, label):
    """Small centred Roman/Arabic numeral at the bottom of front-matter pages."""
    c.setFillColor(GREY_TXT); c.setFont('Helvetica', 8)
    c.drawCentredString(PAGE_W/2, MARGIN-2*mm, label)

def draw_pending_callout(c, x, y, w, h, note=None):
    """Dashed [ PENDING DATA ] box for content the association will supply."""
    c.saveState()
    c.setFillColor(BG_TINT)
    c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeColor(NAVY); c.setLineWidth(0.8); c.setDash(4, 3)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.restoreState()
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(x+w/2, y+h-14, '[ PENDING DATA ]')
    if note:
        c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 9)
        c.drawCentredString(x+w/2, y+h-28, note)

def draw_table(c, x, y, w, headers, rows, row_h=8.5*mm, col_widths=None):
    """Ruled table. Returns final bottom y."""
    n = len(headers)
    if col_widths is None:
        col_widths = [w/n]*n
    # header
    c.setFillColor(NAVY); c.rect(x, y-row_h, w, row_h, stroke=0, fill=1)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 8.5)
    cx = x
    for i, hd in enumerate(headers):
        c.drawString(cx+2.5*mm, y-row_h+3*mm, hd.upper())
        cx += col_widths[i]
    y -= row_h
    # rows
    for r_i, row in enumerate(rows):
        c.setFillColor(HexColor('#FFFFFF') if r_i % 2 == 0 else BG_TINT)
        c.rect(x, y-row_h, w, row_h, stroke=0, fill=1)
        c.setFillColor(INK); c.setFont('Helvetica', 9)
        cx = x
        for i, cell in enumerate(row):
            text = cell if cell else '—'
            # truncate per column
            max_t = col_widths[i] - 4*mm
            while c.stringWidth(text, 'Helvetica', 9) > max_t and len(text) > 1:
                text = text[:-2] + '…'
            c.drawString(cx+2.5*mm, y-row_h+3*mm, text)
            cx += col_widths[i]
        y -= row_h
    # outer border
    c.setStrokeColor(GREY_LINE); c.setLineWidth(0.5)
    c.rect(x, y, w, (len(rows)+1)*row_h, stroke=1, fill=0)
    return y

def draw_fillin(c, x, y, w, label):
    """Form field: small label above an underline."""
    c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 7)
    c.drawString(x, y+3, label.upper())
    c.setStrokeColor(GREY_TXT); c.setLineWidth(0.5)
    c.line(x, y, x+w, y)

def draw_half_page_ad(c, x, y, w, h, label):
    """Branded placeholder for a half/strip ad."""
    c.saveState()
    c.setFillColor(BG_TINT); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeColor(NAVY); c.setLineWidth(0.6); c.setDash(3, 2)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.restoreState()
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(x+w/2, y+h/2+3, label.upper())
    c.setFillColor(GREY_TXT); c.setFont('Helvetica', 7.5)
    c.drawCentredString(x+w/2, y+h/2-9, f'{int(w/mm)} × {int(h/mm)} mm  ·  member or sponsor ad')

# ---------------- Pages ----------------
def page_cover(c):
    # full-bleed navy
    c.setFillColor(NAVY_DARK)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    # geometric pattern overlay
    draw_geo_pattern(c, 0, 0, PAGE_W, PAGE_H, GOLD, opacity=0.06)
    # diagonal accent band (placed lower, below the title block)
    c.saveState()
    p = c.beginPath()
    p.moveTo(0, PAGE_H*0.34)
    p.lineTo(PAGE_W, PAGE_H*0.42)
    p.lineTo(PAGE_W, PAGE_H*0.435)
    p.lineTo(0, PAGE_H*0.355)
    p.close()
    c.setFillColor(GOLD)
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()
    # large monogram E-12 watermark
    c.saveState()
    c.setFont('Helvetica-Bold', 380)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFillAlpha(0.04)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.18, 'E12')
    c.restoreState()
    # top eyebrow
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(PAGE_W/2, PAGE_H-50*mm, 'GREATER NOIDA  ·  UTTAR PRADESH')
    # rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(PAGE_W/2-30*mm, PAGE_H-54*mm, PAGE_W/2+30*mm, PAGE_H-54*mm)
    # main title
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 56)
    c.drawCentredString(PAGE_W/2, PAGE_H-90*mm, 'ECOTECH-12')
    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_W/2, PAGE_H-104*mm, 'INDUSTRIES ASSOCIATION')
    # subtitle
    c.setFillColor(HexColor('#E6E9EF'))
    c.setFont('Helvetica', 14)
    c.drawCentredString(PAGE_W/2, PAGE_H-118*mm, 'Member Directory')
    # year block
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    bw, bh = 60*mm, 22*mm
    bx = (PAGE_W-bw)/2
    by = PAGE_H-160*mm
    c.rect(bx, by, bw, bh, stroke=1, fill=0)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(PAGE_W/2, by+8*mm, 'EDITION 2026')
    # footer caption
    c.setFillColor(HexColor('#8FA3BE'))
    c.setFont('Helvetica', 9)
    c.drawCentredString(PAGE_W/2, 30*mm, 'A directory of 125 member units of the Ecotech-12 industrial estate')
    c.setFont('Helvetica-Oblique', 8)
    c.drawCentredString(PAGE_W/2, 22*mm, 'Built · Made · Manufactured  ·  in Greater Noida')

def page_inside_cover(c, page_label):
    """Publisher / printer credits, copyright notice."""
    c.setFillColor(PAPER); c.rect(0,0,PAGE_W,PAGE_H,stroke=0,fill=1)
    draw_corner_marks(c)
    # masthead
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.82, 'ECOTECH-12 INDUSTRIES ASSOCIATION')
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.line(PAGE_W/2-22*mm, PAGE_H*0.82-5*mm, PAGE_W/2+22*mm, PAGE_H*0.82-5*mm)
    c.setFillColor(INK); c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.76, 'Member Directory')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 12)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.735, 'Edition 2026  ·  First Edition')

    # credits block
    cw = 140*mm; ch = 100*mm
    bx = (PAGE_W-cw)/2; by = (PAGE_H-ch)/2 - 18*mm
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.rect(bx, by, cw, ch, stroke=1, fill=0)
    c.setStrokeColor(NAVY); c.setLineWidth(0.4)
    c.rect(bx+3*mm, by+3*mm, cw-6*mm, ch-6*mm, stroke=1, fill=0)

    rows = [
        ('Published by',  'Ecotech-12 Industries Association'),
        ('Compiled by',   'The Executive Committee'),
        ('Edited by',     '[ editor / committee member ]'),
        ('Designed by',   '[ designer / agency credit ]'),
        ('Printed by',    '[ printer name & full address ]'),
        ('Print run',     '[ number of copies ]'),
        ('Edition',       '2026  ·  First Edition'),
        ('Office address','Ecotech-12, Greater Noida — 201310, U.P.'),
        ('Contact',       'office@ecotech12.in  ·  +91 — — — — — — — — —'),
    ]
    y = by + ch - 10*mm
    for k, v in rows:
        c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 8)
        c.drawString(bx+8*mm, y, k.upper())
        c.setFillColor(INK); c.setFont('Helvetica', 10)
        c.drawString(bx+50*mm, y, v)
        y -= 9.5*mm

    # disclaimer
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 8)
    body = ('All information has been provided by members and is believed correct at the time of going '
            'to press. The Association assumes no liability for errors or omissions. © Ecotech-12 '
            'Industries Association. For internal circulation among members and partners.')
    lines = _wrap(body, 'Helvetica-Oblique', 8, 150*mm, c)
    y = MARGIN+26*mm
    for ln in lines:
        c.drawCentredString(PAGE_W/2, y, ln); y -= 10
    page_footer_label(c, f'— {page_label} —')

def page_toc(c, page_label, toc_entries):
    """toc_entries: list of (label, page_label_str) tuples."""
    y = page_header(c, 'Contents', 'Table of Contents',
                    subtitle='A complete guide to this edition')
    line_h = 7*mm
    for label, num in toc_entries:
        if y < MARGIN + 18*mm:
            break  # safety; one-page TOC
        c.setFillColor(INK); c.setFont('Helvetica', 10.5)
        c.drawString(MARGIN+2*mm, y, label)
        text_w = c.stringWidth(label, 'Helvetica', 10.5)
        num_w = c.stringWidth(num, 'Helvetica-Bold', 10.5)
        dot_start = MARGIN+2*mm + text_w + 3*mm
        dot_end = PAGE_W-MARGIN-2*mm - num_w - 3*mm
        if dot_end > dot_start:
            c.saveState()
            c.setStrokeColor(GREY_LINE); c.setLineWidth(0.6); c.setDash(1, 2)
            c.line(dot_start, y+1.5, dot_end, y+1.5)
            c.restoreState()
        c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 10.5)
        c.drawRightString(PAGE_W-MARGIN-2*mm, y, num)
        y -= line_h
    page_footer_label(c, f'— {page_label} —')

def page_office_bearers(c, page_label):
    """Photo grid of the Executive Committee."""
    y_top = page_header(c, 'Leadership', 'Office Bearers',
                        subtitle='Executive Committee — Ecotech-12 Industries Association')

    roles_top = [
        ('President', 'Mr. [ Name ]'),
        ('Vice President', 'Mr. [ Name ]'),
        ('General Secretary', 'Mr. [ Name ]'),
        ('Treasurer', 'Mr. [ Name ]'),
    ]
    roles_bot = [
        ('Joint Secretary', 'Mr. [ Name ]'),
        ('EC Member', 'Mr. [ Name ]'),
        ('EC Member', 'Mr. [ Name ]'),
        ('EC Member', 'Mr. [ Name ]'),
    ]
    avail_w = PAGE_W - 2*MARGIN
    gap = 3*mm
    card_w = (avail_w - gap*3) / 4
    card_h = 56*mm

    def draw_role_card(x, y, role, name, primary):
        c.setFillColor(HexColor('#FFFFFF'))
        c.setStrokeColor(GREY_LINE); c.setLineWidth(0.5)
        c.rect(x, y, card_w, card_h, stroke=1, fill=1)
        if primary:
            c.setFillColor(NAVY); c.rect(x, y+card_h-4, card_w, 4, stroke=0, fill=1)
            c.setFillColor(GOLD); c.rect(x, y+card_h-5, card_w, 1, stroke=0, fill=1)
        # photo placeholder
        pw, ph = card_w-12*mm, 30*mm
        px = x + (card_w-pw)/2
        py = y + card_h - 12*mm - ph
        c.setFillColor(BG_TINT); c.rect(px, py, pw, ph, stroke=0, fill=1)
        c.setStrokeColor(GREY_LINE); c.setLineWidth(0.4)
        c.rect(px, py, pw, ph, stroke=1, fill=0)
        c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 7)
        c.drawCentredString(px+pw/2, py+ph/2-2, '[ photo ]')
        # role
        c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 7.5)
        c.drawCentredString(x+card_w/2, y+10*mm, role.upper())
        # name
        c.setFillColor(INK); c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(x+card_w/2, y+4.5*mm, name)

    row1_y = y_top - card_h
    for i, (role, name) in enumerate(roles_top):
        draw_role_card(MARGIN + i*(card_w+gap), row1_y, role, name, primary=(i == 0))
    row2_y = row1_y - card_h - 6*mm
    for i, (role, name) in enumerate(roles_bot):
        draw_role_card(MARGIN + i*(card_w+gap), row2_y, role, name, primary=False)

    # contact strip
    cy = MARGIN + 20*mm
    c.setFillColor(NAVY); c.rect(MARGIN, cy, PAGE_W-2*MARGIN, 20*mm, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(MARGIN, cy+20*mm-1, PAGE_W-2*MARGIN, 1, stroke=0, fill=1)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 9)
    c.drawString(MARGIN+4*mm, cy+12*mm, 'ASSOCIATION OFFICE')
    c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica', 9)
    c.drawString(MARGIN+4*mm, cy+5*mm,
                 'Ecotech-12, Greater Noida — 201310, U.P.   ·   office@ecotech12.in   ·   +91 — — — — — — — — —')

    page_footer_label(c, f'— {page_label} —')

def page_president_message(c, page_label):
    """President's message — first of two split foreword pages."""
    c.setFillColor(PAPER); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_corner_marks(c)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-12*mm, 'FROM THE PRESIDENT')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 32)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-26*mm, 'A Word of Welcome')
    c.setStrokeColor(GOLD); c.setLineWidth(1.2)
    c.line(MARGIN+2*mm, PAGE_H-MARGIN-30*mm, MARGIN+22*mm, PAGE_H-MARGIN-30*mm)

    body = [
        "Ecotech-12 is one of Greater Noida's most diverse industrial estates — home to manufacturers,",
        "exporters, engineering houses, packaging companies, garment makers, food processors and",
        "service businesses. This directory brings all 125 member units together in one place: plot",
        "numbers, points of contact, and a map of the estate so visitors, vendors and members can",
        "find each other quickly.",
        "",
        "We hope this becomes the everyday handbook for the estate — a quick reference at the gate,",
        "in the office, and on the move. Our thanks to the sponsors who made this edition possible,",
        "and to every member who shared their details.",
        "",
        "With warm regards,",
    ]
    c.setFillColor(INK); c.setFont('Helvetica', 11)
    y = PAGE_H-MARGIN-46*mm
    for line in body:
        c.drawString(MARGIN+2*mm, y, line); y -= 14
    c.setFont('Helvetica-Bold', 12); c.setFillColor(NAVY)
    c.drawString(MARGIN+2*mm, y-12, '[ President ]')
    c.setFont('Helvetica-Oblique', 10); c.setFillColor(GREY_TXT)
    c.drawString(MARGIN+2*mm, y-26, 'President, Ecotech-12 Industries Association')

    # decorative side block
    bx = PAGE_W-MARGIN-60*mm
    by = MARGIN+30*mm
    c.setFillColor(NAVY); c.rect(bx, by, 60*mm, 70*mm, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(bx, by+70*mm-1*mm, 60*mm, 1*mm, stroke=0, fill=1)
    c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica-Bold', 11)
    c.drawString(bx+6*mm, by+62*mm, 'AT A GLANCE')
    rows = [
        ('Member units', '125'),
        ('Location', 'Greater Noida'),
        ('Estate', 'Ecotech-12'),
        ('Edition', '2026'),
    ]
    yy = by+50*mm
    c.setFont('Helvetica', 10)
    for k, v in rows:
        c.setFillColor(HexColor('#B9C6D8')); c.drawString(bx+6*mm, yy, k)
        c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica-Bold', 11)
        c.drawString(bx+6*mm, yy-12, v)
        c.setFont('Helvetica', 10)
        yy -= 24

    page_footer_label(c, f'— {page_label} —')

def page_secretary_message(c, page_label):
    """Secretary's message — companion page to President's message."""
    c.setFillColor(PAPER); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_corner_marks(c)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-12*mm, 'FROM THE GENERAL SECRETARY')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 32)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-26*mm, "Secretary's Note")
    c.setStrokeColor(GOLD); c.setLineWidth(1.2)
    c.line(MARGIN+2*mm, PAGE_H-MARGIN-30*mm, MARGIN+22*mm, PAGE_H-MARGIN-30*mm)

    body = [
        "This directory has been compiled over [ months ] of fieldwork: walking the estate plot by",
        "plot, speaking with promoters, verifying phone numbers and reconciling our records with the",
        "allotment list. What you have in your hands is the most current, complete view of who is",
        "doing what — and where — in Ecotech-12.",
        "",
        "Members who notice any error or change in their entry are requested to write to the office",
        "so it can be corrected in the next edition. Several sections in this book — products,",
        "brands, certifications, EOU and MSME status — depend on member self-declaration. Please",
        "share these details with the office so the directory becomes more useful with every edition.",
        "",
        "On behalf of the Executive Committee, I thank every member who participated.",
        "",
        "With regards,",
    ]
    c.setFillColor(INK); c.setFont('Helvetica', 11)
    y = PAGE_H-MARGIN-46*mm
    for line in body:
        c.drawString(MARGIN+2*mm, y, line); y -= 14
    c.setFont('Helvetica-Bold', 12); c.setFillColor(NAVY)
    c.drawString(MARGIN+2*mm, y-12, '[ General Secretary ]')
    c.setFont('Helvetica-Oblique', 10); c.setFillColor(GREY_TXT)
    c.drawString(MARGIN+2*mm, y-26, 'General Secretary, Ecotech-12 Industries Association')

    # side stamp
    bx = PAGE_W-MARGIN-60*mm
    by = MARGIN+30*mm
    c.setStrokeColor(GOLD); c.setLineWidth(1.0)
    c.rect(bx, by, 60*mm, 60*mm, stroke=1, fill=0)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(bx+30*mm, by+50*mm, 'OFFICE SEAL')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 8)
    c.drawCentredString(bx+30*mm, by+30*mm, '[ official stamp ]')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica', 8)
    c.drawCentredString(bx+30*mm, by+8*mm, 'Date:  __ /__ /2026')

    page_footer_label(c, f'— {page_label} —')

def page_about(c, page_label):
    """History, objectives, milestones, achievements."""
    y = page_header(c, 'Heritage', 'About the Association',
                    subtitle='Who we are, what we stand for, and what we have built')

    # Two-column structured layout
    col_w = (PAGE_W - 2*MARGIN - 8*mm) / 2
    lx = MARGIN
    rx = MARGIN + col_w + 8*mm

    def section(x, y, title, lines):
        c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 9)
        c.drawString(x, y, title.upper())
        c.setStrokeColor(GOLD); c.setLineWidth(0.6)
        c.line(x, y-3, x+18*mm, y-3)
        c.setFillColor(INK); c.setFont('Helvetica', 9.5)
        yy = y - 12
        for ln in lines:
            for w in _wrap(ln, 'Helvetica', 9.5, col_w, c):
                c.drawString(x, yy, w); yy -= 12
            yy -= 2
        return yy

    # Left column — History + Objectives
    yl = y
    yl = section(lx, yl, 'Our History', [
        'Ecotech-12 Industries Association was formed by the unit holders of the Ecotech-12 '
        'industrial estate in Greater Noida to act as a single voice for the estate before '
        'government, infrastructure providers and the wider business community.',
        '[ Founding year, founding members, and a brief history of the estate to be added. ]',
    ])
    yl -= 6
    yl = section(lx, yl, 'Our Objectives', [
        '◆  Represent member units before UPSIDA, DIC, pollution and labour authorities.',
        '◆  Coordinate common services — security, sanitation, road and drainage upkeep.',
        '◆  Promote inter-member trade, sourcing and skill development within the estate.',
        '◆  Maintain an authoritative member directory and signage for visitors and vendors.',
        '◆  Champion safety, environmental compliance and statutory awareness.',
    ])

    # Right column — Milestones + Achievements
    yr = y
    yr = section(rx, yr, 'Milestones', [
        '[ Year ]   Association incorporated and bye-laws adopted.',
        '[ Year ]   Estate signage and plot numbering project completed.',
        '[ Year ]   Common security & sanitation contract operationalised.',
        '[ Year ]   First member directory published.',
        '[ Year ]   Estate-wide CCTV / safety initiative launched.',
    ])
    yr -= 6
    yr = section(rx, yr, 'Achievements', [
        '◆  Active membership of 125 manufacturing and service units.',
        '◆  Continued engagement with UPSIDA on estate maintenance.',
        '◆  Annual general body and member-networking events.',
        '◆  [ Other awards / recognitions to be added. ]',
    ])

    # Bottom band — values
    by = MARGIN + 18*mm
    bh = 26*mm
    c.setFillColor(NAVY); c.rect(MARGIN, by, PAGE_W-2*MARGIN, bh, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(MARGIN, by+bh-1, PAGE_W-2*MARGIN, 1, stroke=0, fill=1)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 9)
    c.drawString(MARGIN+4*mm, by+bh-10, 'WHAT WE STAND FOR')
    c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica-Bold', 14)
    c.drawString(MARGIN+4*mm, by+8*mm,
                 'Collaboration  ·  Compliance  ·  Craftsmanship  ·  Community')

    page_footer_label(c, f'— {page_label} —')

def page_map(c, page_label):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_corner_marks(c)
    # title
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-12*mm, 'ESTATE LAYOUT')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 28)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-26*mm, 'Map of Ecotech-12')
    c.setStrokeColor(GOLD); c.setLineWidth(1.2)
    c.line(MARGIN+2*mm, PAGE_H-MARGIN-30*mm, MARGIN+22*mm, PAGE_H-MARGIN-30*mm)
    c.setFillColor(GREY_TXT); c.setFont('Helvetica', 10)
    c.drawString(MARGIN+2*mm, PAGE_H-MARGIN-38*mm,
                 'Plots 1 through 117 — Ecotech-12 industrial estate, Greater Noida.')

    # Map frame — placeholder. User will paste actual map image.
    fx = MARGIN
    fw = PAGE_W - 2*MARGIN
    fy = MARGIN + 20*mm
    fh = PAGE_H - MARGIN - 52*mm - fy
    c.setFillColor(HexColor('#FFFFFF'))
    c.setStrokeColor(NAVY); c.setLineWidth(1.4)
    c.rect(fx, fy, fw, fh, stroke=1, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(2)
    tk = 8*mm
    c.line(fx, fy+fh, fx+tk, fy+fh); c.line(fx, fy+fh, fx, fy+fh-tk)
    c.line(fx+fw, fy+fh, fx+fw-tk, fy+fh); c.line(fx+fw, fy+fh, fx+fw, fy+fh-tk)
    c.line(fx, fy, fx+tk, fy); c.line(fx, fy, fx, fy+tk)
    c.line(fx+fw, fy, fx+fw-tk, fy); c.line(fx+fw, fy, fx+fw, fy+tk)
    c.saveState()
    c.setStrokeColor(HexColor('#E5EAF1')); c.setLineWidth(0.4)
    gstep = 12*mm
    nx = int(fw/gstep); ny = int(fh/gstep)
    for i in range(1, nx): c.line(fx+i*gstep, fy, fx+i*gstep, fy+fh)
    for j in range(1, ny): c.line(fx, fy+j*gstep, fx+fw, fy+j*gstep)
    c.restoreState()
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(fx+fw/2, fy+fh/2+4, '[ Estate map to be inserted ]')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 10)
    c.drawCentredString(fx+fw/2, fy+fh/2-12, 'Paste the official Ecotech-12 layout image here.')

    # legend
    ly = fy - 14*mm
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 10)
    c.drawString(fx, ly, 'LEGEND')
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.line(fx, ly-2, fx+22*mm, ly-2)

    items = [
        (NAVY,      'Active member unit'),
        (GOLD,      'Sponsor / featured'),
        (GREY_LINE, 'Vacant / unallocated'),
        (ACCENT,    'Common facility'),
    ]
    cx = fx
    for color, label in items:
        c.setFillColor(color); c.rect(cx, ly-12, 5*mm, 5*mm, stroke=0, fill=1)
        c.setFillColor(INK); c.setFont('Helvetica', 9)
        c.drawString(cx+7*mm, ly-10, label)
        cx += 46*mm

    page_footer_label(c, f'— {page_label} —')

def page_govt_authorities(c, page_label):
    """Directory of relevant government authorities."""
    y = page_header(c, 'Reference', 'Government Authorities',
                    subtitle='Whom to approach, for what — within and around the estate')

    rows = [
        ('District Industries Centre',   'GB Nagar / Gr. Noida',  '[ Officer name ]',  '[ Phone ]'),
        ('UPSIDA Regional Office',       'Greater Noida',         '[ RM / officer ]',  '[ Phone ]'),
        ('UP Pollution Control Board',   'Regional Office',       '[ Officer name ]',  '[ Phone ]'),
        ('Labour Department',            'GB Nagar',              '[ Officer name ]',  '[ Phone ]'),
        ('Fire Services',                'Gr. Noida station',     '[ SO / OIC ]',      '[ Phone ]'),
        ('Electricity (Discom)',         'PVVNL Greater Noida',   '[ XEN / SDO ]',     '[ Phone ]'),
        ('Police (Local Thana)',         'Ecotech / Surajpur',    '[ SHO ]',           '[ Phone ]'),
        ('MSME Development Institute',   'Noida / Delhi NCR',     '[ Officer name ]',  '[ Phone ]'),
        ('GST / Commercial Tax',         'Greater Noida zone',    '[ Officer name ]',  '[ Phone ]'),
        ('ESIC / EPFO',                  'Regional Office',       '[ Officer name ]',  '[ Phone ]'),
        ('Factory Inspector',            'GB Nagar',              '[ Officer name ]',  '[ Phone ]'),
        ('Weights & Measures',           'GB Nagar',              '[ Officer name ]',  '[ Phone ]'),
    ]
    col_widths = [60*mm, 38*mm, 42*mm, (PAGE_W-2*MARGIN) - 140*mm]
    draw_table(c, MARGIN, y, PAGE_W-2*MARGIN,
               ['Authority', 'Office', 'Contact person', 'Phone'],
               rows, col_widths=col_widths)

    # Note
    ny = MARGIN + 36*mm
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 9)
    c.drawString(MARGIN, ny+10*mm,
                 'Member queries should be routed through the Association office where possible —')
    c.drawString(MARGIN, ny+6*mm,
                 'this gives a unified channel and a written record. Direct contacts above are for emergencies and field visits.')

    draw_pending_callout(c, MARGIN, MARGIN+14*mm, PAGE_W-2*MARGIN, 18*mm,
                         'Officer names and direct phone numbers to be filled in by the Secretariat.')
    page_footer_label(c, f'— {page_label} —')

def page_emergency_contacts(c, page_label):
    """Fire, ambulance, hospital, police, electricity complaint."""
    y = page_header(c, 'Safety First', 'Emergency Contacts',
                    subtitle='Keep this page near the gate, the office and on the shop floor')

    # Big call-grid: 3 columns × 3 rows of bold tiles
    tiles = [
        ('FIRE',         '101',                'Fire Services'),
        ('AMBULANCE',    '102 / 108',          'Government ambulance'),
        ('POLICE',       '112',                'Universal emergency'),
        ('LOCAL THANA',  '[ Phone ]',          'Ecotech / Surajpur PS'),
        ('FIRE STATION', '[ Phone ]',          'Greater Noida'),
        ('HOSPITAL',     '[ Phone ]',          '[ Nearest hospital name ]'),
        ('ELECTRICITY',  '1912',               'Discom complaint number'),
        ('PVVNL LOCAL',  '[ Phone ]',          'Local SDO / lineman'),
        ('ASSN. OFFICE', '[ Phone ]',          'Ecotech-12 office'),
    ]
    cols, rows = 3, 3
    gap = 5*mm
    avail_w = PAGE_W - 2*MARGIN
    tile_w = (avail_w - gap*(cols-1)) / cols
    tile_h = 36*mm
    grid_top = y - 4*mm
    for i, (label, num, sub) in enumerate(tiles):
        r = i // cols
        col = i % cols
        x = MARGIN + col*(tile_w+gap)
        ty = grid_top - (r+1)*tile_h - r*gap
        # tile
        c.setFillColor(NAVY); c.rect(x, ty, tile_w, tile_h, stroke=0, fill=1)
        c.setFillColor(GOLD); c.rect(x, ty+tile_h-3, tile_w, 3, stroke=0, fill=1)
        c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 9)
        c.drawString(x+4*mm, ty+tile_h-12, label)
        c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica-Bold', 24)
        c.drawString(x+4*mm, ty+tile_h-30, num)
        c.setFillColor(HexColor('#B9C6D8')); c.setFont('Helvetica', 9)
        c.drawString(x+4*mm, ty+6, sub)

    # Procedural note at bottom
    by = MARGIN + 14*mm
    c.setFillColor(BG_TINT); c.rect(MARGIN, by, PAGE_W-2*MARGIN, 22*mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.rect(MARGIN, by, PAGE_W-2*MARGIN, 22*mm, stroke=1, fill=0)
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 9)
    c.drawString(MARGIN+4*mm, by+15*mm, 'IN AN EMERGENCY')
    c.setFillColor(INK); c.setFont('Helvetica', 9)
    c.drawString(MARGIN+4*mm, by+9*mm,
                 '1. Call the relevant number above.   2. Inform the Association office.   3. Note time, caller and response.')
    c.drawString(MARGIN+4*mm, by+4*mm,
                 'Every member is requested to display this page at the security cabin and in the supervisor’s office.')

    page_footer_label(c, f'— {page_label} —')

def page_utilities(c, page_label):
    """Key utilities & service providers in/around the estate."""
    y = page_header(c, 'Reference', 'Utilities & Service Providers',
                    subtitle='Common service providers active on the estate')

    rows = [
        ('Electricity (Discom)',         'PVVNL — Greater Noida',         '[ Office ]',         '[ Phone ]'),
        ('Water supply',                 '[ Provider ]',                  '[ Office ]',         '[ Phone ]'),
        ('Sewerage / drainage',          'UPSIDA',                        '[ Office ]',         '[ Phone ]'),
        ('Estate maintenance',           'UPSIDA / Association',          '[ Officer ]',        '[ Phone ]'),
        ('Security (estate-wide)',       '[ Agency name ]',               '[ Supervisor ]',     '[ Phone ]'),
        ('Sanitation / housekeeping',    '[ Agency name ]',               '[ Supervisor ]',     '[ Phone ]'),
        ('Solid-waste pickup',           '[ Vendor ]',                    '[ Contact ]',        '[ Phone ]'),
        ('Hazardous-waste handling',     '[ Authorised TSDF ]',           '[ Contact ]',        '[ Phone ]'),
        ('Internet / leased lines',      '[ ISPs serving estate ]',       '[ Sales rep ]',      '[ Phone ]'),
        ('Courier & logistics',          '[ Major couriers active ]',     '[ Branch ]',         '[ Phone ]'),
        ('Banks on estate',              '[ Branches in the vicinity ]',  '[ Branch manager ]', '[ Phone ]'),
        ('Petrol / diesel station',      '[ Nearest pump ]',              '—',                  '[ Phone ]'),
    ]
    col_widths = [55*mm, 50*mm, 38*mm, (PAGE_W-2*MARGIN) - 143*mm]
    draw_table(c, MARGIN, y, PAGE_W-2*MARGIN,
               ['Service', 'Provider', 'Contact', 'Phone'],
               rows, col_widths=col_widths)

    draw_pending_callout(c, MARGIN, MARGIN+14*mm, PAGE_W-2*MARGIN, 22*mm,
                         'Provider names and phone numbers to be supplied by the Secretariat.')
    page_footer_label(c, f'— {page_label} —')

def page_sponsor(c, slot_label):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_geo_pattern(c, 0, 0, PAGE_W, PAGE_H, NAVY, opacity=0.025)
    inset = 12*mm
    c.setStrokeColor(NAVY); c.setLineWidth(0.6)
    c.rect(inset, inset, PAGE_W-2*inset, PAGE_H-2*inset, stroke=1, fill=0)
    inset2 = 16*mm
    c.setStrokeColor(GOLD); c.setLineWidth(0.4)
    c.rect(inset2, inset2, PAGE_W-2*inset2, PAGE_H-2*inset2, stroke=1, fill=0)

    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(PAGE_W/2, PAGE_H-40*mm, slot_label.upper())
    c.setStrokeColor(GOLD); c.setLineWidth(0.8)
    c.line(PAGE_W/2-18*mm, PAGE_H-42*mm, PAGE_W/2+18*mm, PAGE_H-42*mm)

    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 44)
    c.drawCentredString(PAGE_W/2, PAGE_H-72*mm, 'Sponsor')
    c.setFont('Helvetica-Bold', 44)
    c.drawCentredString(PAGE_W/2, PAGE_H-90*mm, 'Showcase')

    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 12)
    c.drawCentredString(PAGE_W/2, PAGE_H-104*mm, 'This page is reserved for a sponsor advertisement.')

    bw, bh = 130*mm, 80*mm
    bx = (PAGE_W-bw)/2
    by = (PAGE_H-bh)/2 - 18*mm
    c.saveState()
    c.setStrokeColor(NAVY); c.setLineWidth(1.0); c.setDash(4, 3)
    c.rect(bx, by, bw, bh, stroke=1, fill=0)
    c.restoreState()
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(PAGE_W/2, by+bh/2+4, 'YOUR LOGO  ·  YOUR MESSAGE')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica', 9)
    c.drawCentredString(PAGE_W/2, by+bh/2-10, '210 × 297 mm full-page  ·  CMYK 300 dpi')

    c.setFillColor(GREY_TXT); c.setFont('Helvetica', 9)
    c.drawCentredString(PAGE_W/2, MARGIN+4*mm,
                       'For sponsorship enquiries, contact the Ecotech-12 Industries Association office.')

def page_half_strip_ads(c, page_label):
    """A page that hosts one half-page ad + two strip ads — interleaved between sections."""
    c.setFillColor(PAPER); c.rect(0,0,PAGE_W,PAGE_H,stroke=0,fill=1)
    draw_page_chrome(c, page_label, 'Advertisements')
    # half page (top)
    hw = PAGE_W - 2*MARGIN
    hh = (PAGE_H - 36*mm) * 0.55
    hy = PAGE_H - 18*mm - hh - 6*mm
    draw_half_page_ad(c, MARGIN, hy, hw, hh, 'Half-page advertisement')
    # two strips (bottom)
    sh = 32*mm
    sgap = 6*mm
    sy1 = hy - sh - 10*mm
    draw_half_page_ad(c, MARGIN, sy1, hw, sh, 'Strip advertisement')
    sy2 = sy1 - sh - sgap
    draw_half_page_ad(c, MARGIN, sy2, hw, sh, 'Strip advertisement')

def directory_card(c, x, y, w, h, sr, member):
    """Card representing one member."""
    plot = member['plot'] or '—'
    name = member['name'] or '(Vacant Plot)'
    vacant = (member['name'].strip() == '') or member['name'].lower().startswith('cancelled')

    # base card
    c.setFillColor(HexColor('#FFFFFF'))
    c.setStrokeColor(GREY_LINE); c.setLineWidth(0.5)
    c.rect(x, y, w, h, stroke=1, fill=1)
    # left ribbon
    ribbon_w = 16*mm
    c.setFillColor(NAVY if not vacant else GREY_LINE)
    c.rect(x, y, ribbon_w, h, stroke=0, fill=1)
    c.setFillColor(GOLD if not vacant else HexColor('#BEC6D2'))
    c.rect(x, y+h-3, ribbon_w, 3, stroke=0, fill=1)

    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(x+ribbon_w/2, y+h-10, 'PLOT')
    c.setFont('Helvetica-Bold', 14 if len(plot) <= 4 else 11)
    c.drawCentredString(x+ribbon_w/2, y+h-24, plot)
    c.setFont('Helvetica', 6.5)
    c.setFillColor(HexColor('#A7B6CC'))
    c.drawCentredString(x+ribbon_w/2, y+6, f'#{sr:03d}')

    tx = x + ribbon_w + 4*mm
    tw = w - ribbon_w - 8*mm
    ty = y + h - 8*mm

    c.setFillColor(NAVY if not vacant else GREY_TXT)
    c.setFont('Helvetica-Bold', 10)
    words = name.split()
    line1 = ''; line2 = ''; rem = words[:]
    while rem and c.stringWidth(line1+' '+rem[0], 'Helvetica-Bold', 10) <= tw:
        line1 = (line1+' '+rem.pop(0)).strip()
    while rem and c.stringWidth(line2+' '+rem[0], 'Helvetica-Bold', 10) <= tw:
        line2 = (line2+' '+rem.pop(0)).strip()
    if rem:
        while rem and c.stringWidth(line2+' '+rem[0]+'…', 'Helvetica-Bold', 10) <= tw:
            line2 = (line2+' '+rem.pop(0)).strip()
        line2 = line2 + '…'
    c.drawString(tx, ty, line1)
    if line2:
        c.drawString(tx, ty-12, line2); ty -= 22
    else:
        ty -= 12

    c.setStrokeColor(GREY_LINE); c.setLineWidth(0.4)
    c.line(tx, ty-2, tx+tw, ty-2)
    ty -= 8

    c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 7)
    c.drawString(tx, ty, 'CONTACT')
    ty -= 9

    contacts = member['contacts']
    if not contacts and vacant:
        c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 9)
        c.drawString(tx, ty, 'Plot details not on record.')
    elif not contacts:
        c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 9)
        c.drawString(tx, ty, 'Contact details to be updated.')
    else:
        c.setFont('Helvetica', 9)
        for person, phone in contacts[:2]:
            if not person and not phone: continue
            line_p = person.replace('Mr.', '').strip()
            c.setFillColor(INK); c.setFont('Helvetica-Bold', 9)
            text = line_p if line_p else 'Contact'
            while c.stringWidth(text, 'Helvetica-Bold', 9) > tw:
                text = text[:-2]+'…'
            c.drawString(tx, ty, text)
            ty -= 10
            if phone:
                c.setFillColor(GREY_TXT); c.setFont('Helvetica', 8.5)
                c.drawString(tx, ty, phone)
                ty -= 10
        if len(contacts) > 2:
            c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 8)
            c.drawString(tx, ty, f'+ {len(contacts)-2} more contact(s)')
            ty -= 8

    c.setStrokeColor(GREY_LINE); c.setLineWidth(0.3)
    c.line(tx, y+10*mm, tx+tw, y+10*mm)
    c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 6.5)
    c.drawString(tx, y+6*mm, 'PRIMARY PRODUCTS')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 8)
    c.drawString(tx, y+2*mm, '_______________________________________')

def page_section_divider(c, title, subtitle):
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_geo_pattern(c, 0, 0, PAGE_W, PAGE_H, GOLD, opacity=0.05)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.58, subtitle.upper())
    c.setStrokeColor(GOLD); c.setLineWidth(0.6)
    c.line(PAGE_W/2-26*mm, PAGE_H*0.575, PAGE_W/2+26*mm, PAGE_H*0.575)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont('Helvetica-Bold', 48)
    c.drawCentredString(PAGE_W/2, PAGE_H*0.5, title)

def page_section_index(c, members_indexed, start_sr, end_sr, page_label):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_page_chrome(c, page_label, 'Index')
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN, PAGE_H-MARGIN-18*mm, 'HOW TO USE THIS DIRECTORY')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 22)
    c.drawString(MARGIN, PAGE_H-MARGIN-32*mm, 'Directory at a glance')
    c.setStrokeColor(GOLD); c.setLineWidth(1.0)
    c.line(MARGIN, PAGE_H-MARGIN-36*mm, MARGIN+22*mm, PAGE_H-MARGIN-36*mm)

    c.setFillColor(INK); c.setFont('Helvetica', 11)
    notes = [
        "Entries are ordered by plot number — the same order in which plots are laid out on the estate.",
        "Each card shows: plot number, member name, point-of-contact and phone, and a blank line where",
        "the unit's primary products will be added. Some plots are vacant or have not yet shared",
        "details — they appear with a muted ribbon and a blank contact block, ready for an update.",
        "",
        "Sponsor pages appear at four points through the book. The map of the estate is in the front",
        "matter. Use it together with this directory to navigate Ecotech-12 quickly.",
        "",
        "After the member cards you will find indexes by name, plot, sector, products and brands —",
        "and supplementary sections (bye-laws, membership form, calendar, acknowledgements).",
    ]
    y = PAGE_H-MARGIN-48*mm
    for line in notes:
        c.drawString(MARGIN, y, line); y -= 14

    sy = MARGIN+40*mm
    sh = 40*mm
    c.setFillColor(NAVY)
    c.rect(MARGIN, sy, PAGE_W-2*MARGIN, sh, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(MARGIN, sy+sh-1, PAGE_W-2*MARGIN, 1, stroke=0, fill=1)
    stats = [
        ('125', 'Member units listed'),
        ('117', 'Numbered plots'),
        ('8',   'Sub-plot suffixes (A/B/C/D)'),
        ('4',   'Sponsor showcases'),
    ]
    cw = (PAGE_W-2*MARGIN)/len(stats)
    for i, (n, label) in enumerate(stats):
        cx = MARGIN + i*cw + cw/2
        c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 26)
        c.drawCentredString(cx, sy+sh-18, n)
        c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica', 9)
        c.drawCentredString(cx, sy+8, label)

# ---------------- Generated indexes (real data) ----------------
def _two_col_lookup(c, page_label, eyebrow, title, subtitle, rows, headers):
    """Two-column lookup table page used by alpha + plot indexes."""
    y = page_header(c, eyebrow, title, subtitle=subtitle)
    half = len(rows) // 2 + len(rows) % 2
    left_rows = rows[:half]
    right_rows = rows[half:]
    col_gap = 8*mm
    col_w = (PAGE_W - 2*MARGIN - col_gap) / 2
    line_h = 5*mm

    def draw_col(x, items):
        yy = y
        # header
        c.setFillColor(NAVY); c.rect(x, yy-line_h, col_w, line_h, stroke=0, fill=1)
        c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 7.5)
        c.drawString(x+2*mm, yy-line_h+1.5*mm, headers[0].upper())
        c.drawString(x+col_w*0.78, yy-line_h+1.5*mm, headers[1].upper())
        yy -= line_h
        c.setFillColor(INK); c.setFont('Helvetica', 8.5)
        for i, (a, b) in enumerate(items):
            if i % 2 == 1:
                c.setFillColor(BG_TINT); c.rect(x, yy-line_h, col_w, line_h, stroke=0, fill=1)
            c.setFillColor(INK)
            # left field (truncated)
            txt = a
            while c.stringWidth(txt, 'Helvetica', 8.5) > col_w*0.74 and len(txt) > 1:
                txt = txt[:-2]+'…'
            c.drawString(x+2*mm, yy-line_h+1.5*mm, txt)
            # right field
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(x+col_w*0.78, yy-line_h+1.5*mm, b)
            c.setFont('Helvetica', 8.5)
            yy -= line_h
            if yy < MARGIN + 16*mm:
                break
        # outer
        c.setStrokeColor(GREY_LINE); c.setLineWidth(0.4)
        c.rect(x, yy, col_w, y-yy, stroke=1, fill=0)

    draw_col(MARGIN, left_rows)
    draw_col(MARGIN + col_w + col_gap, right_rows)
    page_footer_label(c, f'— {page_label} —')

def page_alpha_index(c, page_label, members):
    """Members listed alphabetically with plot numbers — quick lookup."""
    listed = []
    for m in members:
        nm = (m['name'] or '').strip()
        plot = (m['plot'] or '—').strip()
        if not nm or nm.lower().startswith('cancelled'):
            continue
        listed.append((nm, plot))
    listed.sort(key=lambda r: r[0].upper())
    _two_col_lookup(c, page_label,
                    'Quick Lookup',
                    'Alphabetical Index',
                    f'All {len(listed)} listed members in A-Z order — find the plot from the name.',
                    listed, ['Member', 'Plot'])

def page_plot_index(c, page_label, members):
    """Members listed by plot number — compact quick lookup variant."""
    def plot_key(s):
        s = (s or '').strip()
        m = re.match(r'(\d+)(.*)$', s)
        if m: return (int(m.group(1)), m.group(2))
        return (10_000, s)
    listed = []
    for m in members:
        plot = (m['plot'] or '').strip()
        nm = (m['name'] or 'Vacant').strip()
        if not plot: continue
        listed.append((plot, nm))
    listed.sort(key=lambda r: plot_key(r[0]))
    # render as (plot, name) but headers swapped
    rows = [(f"Plot {p}", n) for p, n in listed]
    _two_col_lookup(c, page_label,
                    'Quick Lookup',
                    'Plot Number Index',
                    f'{len(rows)} entries — find the member from the plot number.',
                    rows, ['Plot', 'Member'])

# ---------------- Stub pages (pending data) ----------------
def _stub_with_bullets(c, page_label, eyebrow, title, subtitle, intro, bullets, note):
    y = page_header(c, eyebrow, title, subtitle=subtitle)
    c.setFillColor(INK); c.setFont('Helvetica', 11)
    for line in _wrap(intro, 'Helvetica', 11, PAGE_W-2*MARGIN-4*mm, c):
        c.drawString(MARGIN+2*mm, y, line); y -= 14
    y -= 6
    if bullets:
        c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 8)
        c.drawString(MARGIN+2*mm, y, 'TO BE INCLUDED'); y -= 12
        for b in bullets:
            c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
            c.drawString(MARGIN+2*mm, y, '◆')
            c.setFillColor(INK); c.setFont('Helvetica', 10)
            wrapped = _wrap(b, 'Helvetica', 10, PAGE_W-2*MARGIN-12*mm, c)
            for j, ln in enumerate(wrapped):
                c.drawString(MARGIN+8*mm, y, ln); y -= 12
            y -= 2
    callout_h = 28*mm
    cy = max(MARGIN + 16*mm, y - callout_h - 4*mm)
    draw_pending_callout(c, MARGIN, cy, PAGE_W-2*MARGIN, callout_h, note)
    page_footer_label(c, f'— {page_label} —')

def page_sector_index(c, page_label):
    _stub_with_bullets(c, page_label,
        'Yellow Pages', 'Sector / Industry Classification',
        'Members grouped by what they make or do — for buyers, vendors and visitors.',
        'Once each member declares their primary industry, plots will be grouped under these heads. '
        'Categories below are indicative — final taxonomy will be set by the Executive Committee.',
        ['Cables, wires, electricals',
         'Plastics & polymer products',
         'Engineering, fabrication, sheet-metal',
         'Food & beverage processing',
         'Packaging & printing',
         'Garments & textiles',
         'Chemicals & allied',
         'Pharmaceuticals & medical products',
         'Auto components & ancillaries',
         'Other manufacturing & services'],
        'Member self-declarations to be collected and tabulated against this list.')

def page_products_index(c, page_label):
    _stub_with_bullets(c, page_label,
        'Yellow Pages', 'Products & Services Index',
        'A who-makes-what reference — alphabetical by product or service.',
        'Buyers and visitors will use this section first. Each member is requested to share three to five '
        'primary product or service lines. These will be alphabetised and cross-referenced to plot numbers.',
        ['Submit primary products to the office on the membership form (see Membership Application).',
         'Entries will be cross-listed with brand names and sector classification.',
         'Generic terms are preferred (e.g. "PVC flexible pipes", "MS structural fabrication") '
         'so a buyer searching the directory finds the right cluster of members.'],
        'Per-member product lines to be collected before this section is typeset.')

def page_brands_index(c, page_label):
    _stub_with_bullets(c, page_label,
        'Yellow Pages', 'Brand Names Index',
        'Trade marks and brand names operated by member units — alphabetical.',
        'Many member units sell under one or more brand names that differ from the registered company. '
        'This index links those brand names back to the manufacturing unit and plot number.',
        ['Submit brand / trade-mark names along with the parent company name to the office.',
         'Indicate registered (®) vs unregistered marks where applicable.',
         'Each brand will appear with: brand name, parent company, plot number.'],
        'Brand-name declarations to be collected from members.')

def page_eou_list(c, page_label):
    _stub_with_bullets(c, page_label,
        'Trade Reference', 'Export-Oriented Units',
        'Member units engaged in exports — IEC-registered or 100% EOU.',
        'A separate listing of export-active members helps trade visitors and buyers find them quickly. '
        'Recognition basis: IEC code on file, with declared export markets and HS-code groupings.',
        ['IEC code (Importer-Exporter Code) on record.',
         'Primary export markets (regions / countries).',
         'Primary HS-code clusters or product groups.',
         'Year of first export and current export share of turnover (optional, self-declared).'],
        'EOU declarations to be collected through the membership form.')

def page_msme_list(c, page_label):
    _stub_with_bullets(c, page_label,
        'Trade Reference', 'MSME-Classified Units',
        'Member units holding a valid Udyam registration — Micro, Small or Medium.',
        'A separate index of MSME-registered members. Helps with vendor preference under government '
        'procurement and supports inter-member sourcing under MSME credit / receivables programmes.',
        ['Udyam Registration Number (URN).',
         'Classification — Micro / Small / Medium.',
         'Date of Udyam registration.',
         'NIC code(s) — primary activity declared on Udyam.'],
        'Udyam details to be collected from members on the membership form.')

def page_byelaws(c, page_label):
    _stub_with_bullets(c, page_label,
        'Governance', 'Bye-Laws & Membership Rules',
        'A summary of the Association\'s bye-laws and the rules of membership.',
        'The full bye-laws are filed with the Registrar of Societies and a copy is available at the '
        'Association office. The summary below sets out the items most relevant to day-to-day membership.',
        ['Eligibility for membership — unit holder of a plot on Ecotech-12 industrial estate.',
         'Categories of membership — Ordinary, Associate, Patron (if applicable).',
         'Membership fees — admission, annual subscription, late-payment provisions.',
         'Rights and duties of members — voting, AGM attendance, code of conduct.',
         'Office bearers — composition, term, election procedure, casual-vacancy filling.',
         'Meetings — General Body, Executive Committee, quorum and notice periods.',
         'Accounts & audit — financial year, auditor appointment, annual return filings.',
         'Dispute resolution, suspension / termination of membership, amendment procedure.'],
        'Bye-laws summary text to be supplied by the Executive Committee / legal advisor.')

def page_membership_form(c, page_label):
    """A printable membership application form."""
    y = page_header(c, 'Apply', 'Membership Application Form',
                    subtitle='Photocopy this page, fill in by hand, and submit to the Association office.')

    # Form note
    c.setFillColor(INK); c.setFont('Helvetica', 9.5)
    c.drawString(MARGIN+2*mm, y,
                 'To: The General Secretary, Ecotech-12 Industries Association, Greater Noida — 201310, U.P.')
    y -= 10
    c.setFont('Helvetica', 9.5)
    c.drawString(MARGIN+2*mm, y,
                 'I/we wish to apply for membership of the Association. The particulars of our unit are:')
    y -= 6*mm

    # Field rows
    fields = [
        [('Company / firm name', 0.70), ('Plot number', 0.28)],
        [('Promoter / proprietor name', 0.70), ('Designation', 0.28)],
        [('Year of establishment', 0.30), ('GST / Udyam / CIN', 0.66)],
        [('Office address', 1.00)],
        [('Factory address (if different)', 1.00)],
        [('Mobile (primary)', 0.30), ('Mobile (alternate)', 0.30), ('Landline', 0.34)],
        [('Email', 0.50), ('Website', 0.46)],
        [('Industry / sector', 0.50), ('Year established', 0.20), ('Employees', 0.24)],
        [('Primary products / services', 1.00)],
        [('Brand names (if any)', 1.00)],
        [('Certifications (ISO, BIS, etc.)', 0.60), ('Export markets', 0.36)],
        [('Banker name & branch', 0.60), ('IEC code (if applicable)', 0.36)],
    ]
    avail_w = PAGE_W - 2*MARGIN - 4*mm
    field_h = 11*mm
    fx = MARGIN + 2*mm
    for row in fields:
        total_frac = sum(frac for _, frac in row)
        gap = 4*mm
        usable = avail_w - gap*(len(row)-1)
        x = fx
        for label, frac in row:
            w = usable * (frac/total_frac)
            draw_fillin(c, x, y, w, label)
            x += w + gap
        y -= field_h
        if y < MARGIN + 42*mm:
            break

    # Declaration + signature
    y_decl = MARGIN + 30*mm
    c.setFillColor(INK); c.setFont('Helvetica', 8.5)
    decl = ('Declaration: I/we have read the bye-laws of the Association and agree to abide by them. '
            'The particulars above are true to the best of my/our knowledge.')
    for ln in _wrap(decl, 'Helvetica', 8.5, PAGE_W-2*MARGIN-4*mm, c):
        c.drawString(fx, y_decl, ln); y_decl -= 11

    sy = MARGIN + 16*mm
    draw_fillin(c, fx, sy, 50*mm, 'Date')
    draw_fillin(c, fx+60*mm, sy, 70*mm, 'Authorised signatory & seal')

    page_footer_label(c, f'— {page_label} —')

def page_calendar(c, page_label):
    """Calendar of association events."""
    y = page_header(c, 'Save the Date', 'Calendar of Events',
                    subtitle='Member meetings, training programmes and Association events for 2026')

    rows = [
        ('Q1 2026',  '[ Date ]',  'Annual General Meeting',           'Members + invitees'),
        ('Q1 2026',  '[ Date ]',  'Fire & safety drill — estate-wide','Member representatives'),
        ('Q2 2026',  '[ Date ]',  'Compliance workshop (GST / Labour)','Members + accounts'),
        ('Q2 2026',  '[ Date ]',  'Members\' family day / networking', 'Members + families'),
        ('Q3 2026',  '[ Date ]',  'Independence Day flag hoisting',   'Estate-wide'),
        ('Q3 2026',  '[ Date ]',  'Skill-development tie-up programme','Workforce / HR heads'),
        ('Q4 2026',  '[ Date ]',  'Estate cleanliness & green drive', 'Members'),
        ('Q4 2026',  '[ Date ]',  'Year-end Executive Committee meet', 'EC members'),
    ]
    col_widths = [22*mm, 28*mm, 80*mm, (PAGE_W-2*MARGIN) - 130*mm]
    draw_table(c, MARGIN, y, PAGE_W-2*MARGIN,
               ['Quarter', 'Date', 'Event', 'Open to'],
               rows, col_widths=col_widths)

    draw_pending_callout(c, MARGIN, MARGIN+14*mm, PAGE_W-2*MARGIN, 22*mm,
                         'Exact dates and venues to be confirmed by the Executive Committee.')
    page_footer_label(c, f'— {page_label} —')

def page_acknowledgements(c, page_label):
    """Thanks page."""
    y = page_header(c, 'With Gratitude', 'Acknowledgements',
                    subtitle='To everyone who made this directory possible')

    sections = [
        ('Executive Committee',
         'Our President, Vice President, General Secretary, Treasurer and EC members — '
         'for their leadership, the time given to this directory, and for steering the '
         'Association through the year.'),
        ('Sponsors',
         'The four sponsor units who supported this edition financially — without their '
         'contribution the directory would not have been printed. Their advertisements '
         'appear on the cover-page slots and at four interior showcases through the book.'),
        ('Members',
         'Every member unit that shared their contact details, plot information and verified '
         'their listing — and welcomed the directory team into their factory premises.'),
        ('Compilation team',
         'The compilation team that walked the estate plot-by-plot, the design and layout '
         'partners, the editors who proofed each page, and the printer who produced the book.'),
        ('Authorities',
         'UPSIDA, District Industries Centre, Pollution Control Board, Fire Services, Police '
         'and PVVNL — for their continued engagement with the Ecotech-12 estate.'),
    ]
    c.setFillColor(INK)
    for title, body in sections:
        c.setFillColor(GOLD_DARK); c.setFont('Helvetica-Bold', 9)
        c.drawString(MARGIN+2*mm, y, title.upper())
        c.setStrokeColor(GOLD); c.setLineWidth(0.6)
        c.line(MARGIN+2*mm, y-3, MARGIN+22*mm, y-3)
        y -= 14
        c.setFillColor(INK); c.setFont('Helvetica', 10)
        for ln in _wrap(body, 'Helvetica', 10, PAGE_W-2*MARGIN-4*mm, c):
            c.drawString(MARGIN+2*mm, y, ln); y -= 12
        y -= 8

    # Sign-off
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(PAGE_W/2, MARGIN+22*mm, 'Thank you.')
    c.setFillColor(GREY_TXT); c.setFont('Helvetica-Oblique', 9)
    c.drawCentredString(PAGE_W/2, MARGIN+14*mm, '— The Ecotech-12 Industries Association —')

    page_footer_label(c, f'— {page_label} —')

def page_notes(c, page_label):
    """Lined notes page."""
    c.setFillColor(PAPER); c.rect(0,0,PAGE_W,PAGE_H,stroke=0,fill=1)
    draw_page_chrome(c, page_label, 'Notes')
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 10)
    c.drawString(MARGIN, PAGE_H-MARGIN-18*mm, 'NOTES')
    c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 22)
    c.drawString(MARGIN, PAGE_H-MARGIN-32*mm, 'Jot, sketch, plan')
    c.setStrokeColor(GOLD); c.setLineWidth(1.0)
    c.line(MARGIN, PAGE_H-MARGIN-36*mm, MARGIN+22*mm, PAGE_H-MARGIN-36*mm)
    # ruled lines
    top = PAGE_H-MARGIN-44*mm
    bottom = MARGIN + 18*mm
    line_gap = 8*mm
    c.setStrokeColor(GREY_LINE); c.setLineWidth(0.4)
    y = top
    while y > bottom:
        c.line(MARGIN, y, PAGE_W-MARGIN, y); y -= line_gap

def page_back_cover(c):
    c.setFillColor(NAVY_DARK)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_geo_pattern(c, 0, 0, PAGE_W, PAGE_H, GOLD, opacity=0.05)
    c.setFillColor(GOLD)
    c.rect(MARGIN, PAGE_H-MARGIN-2, PAGE_W-2*MARGIN, 1.5, stroke=0, fill=1)
    c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica-Bold', 12)
    c.drawString(MARGIN, PAGE_H-MARGIN-14, 'ECOTECH-12 INDUSTRIES ASSOCIATION')
    c.setFillColor(HexColor('#B9C6D8')); c.setFont('Helvetica', 10)
    c.drawString(MARGIN, PAGE_H-MARGIN-28, 'Greater Noida  ·  Uttar Pradesh  ·  India')

    c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica-Bold', 30)
    lines = ['One estate.', '125 enterprises.', 'Built together.']
    y = PAGE_H*0.58
    for line in lines:
        c.drawCentredString(PAGE_W/2, y, line); y -= 36

    # Premium ad slot below the quote
    aw, ah = 130*mm, 70*mm
    ax = (PAGE_W-aw)/2
    ay = MARGIN + 95*mm
    c.saveState()
    c.setStrokeColor(GOLD); c.setLineWidth(0.8); c.setDash(4, 3)
    c.rect(ax, ay, aw, ah, stroke=1, fill=0)
    c.restoreState()
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(PAGE_W/2, ay+ah/2+4, 'BACK-COVER AD SLOT')
    c.setFillColor(HexColor('#B9C6D8')); c.setFont('Helvetica', 8.5)
    c.drawCentredString(PAGE_W/2, ay+ah/2-10, 'Premium full-page advertisement  ·  enquiries: Association office')

    # Contact card
    bw, bh = 130*mm, 40*mm
    bx = (PAGE_W-bw)/2
    by = MARGIN+40*mm
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFillAlpha(0.06); c.rect(bx, by, bw, bh, stroke=0, fill=1); c.setFillAlpha(1)
    c.setStrokeColor(GOLD); c.setLineWidth(0.6); c.rect(bx, by, bw, bh, stroke=1, fill=0)
    c.setFillColor(GOLD); c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(PAGE_W/2, by+bh-12, 'ASSOCIATION OFFICE')
    c.setFillColor(HexColor('#FFFFFF')); c.setFont('Helvetica', 10)
    c.drawCentredString(PAGE_W/2, by+bh-26, 'Ecotech-12, Greater Noida — 201310, U.P.')
    c.drawCentredString(PAGE_W/2, by+bh-38, 'office@ecotech12.in   ·   +91 — — — — — — — —')

    c.setFillColor(HexColor('#8FA3BE')); c.setFont('Helvetica', 8)
    c.drawCentredString(PAGE_W/2, MARGIN+18, 'Published by the Ecotech-12 Industries Association  ·  Edition 2026')
    c.drawCentredString(PAGE_W/2, MARGIN+8, 'For internal circulation among members and partners')

# ---------------- Main ----------------
def build():
    members = parse_members()
    N = len(members)
    COLS, ROWS = 2, 3
    CARDS_PER_PAGE = COLS * ROWS
    dir_total = (N + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
    sponsor_after_dir = {7, 14}

    # ---- Plan pages (two-pass: build plan then render so TOC has page numbers) ----
    pages = []

    def add(kind, render, toc=None, numbering='arabic'):
        pages.append({'kind': kind, 'render': render, 'toc': toc, 'numbering': numbering})

    # Front matter — Roman numerals (cover excluded from numbering)
    add('cover',           lambda c, p: page_cover(c),                            toc=None,                                  numbering='cover')
    add('inside_cover',    lambda c, p: page_inside_cover(c, p),                  toc='Publisher & Printer',                 numbering='roman')
    add('toc',             lambda c, p: page_toc(c, p, _toc_data),                toc='Table of Contents',                   numbering='roman')
    add('office_bearers',  lambda c, p: page_office_bearers(c, p),                toc='Office Bearers',                      numbering='roman')
    add('president',       lambda c, p: page_president_message(c, p),             toc="President's Message",                 numbering='roman')
    add('secretary',       lambda c, p: page_secretary_message(c, p),             toc="Secretary's Message",                 numbering='roman')
    add('about',           lambda c, p: page_about(c, p),                         toc='About the Association',               numbering='roman')
    add('map',             lambda c, p: page_map(c, p),                           toc='Map of the Estate',                   numbering='roman')
    add('govt',            lambda c, p: page_govt_authorities(c, p),              toc='Government Authorities',              numbering='roman')
    add('emergency',       lambda c, p: page_emergency_contacts(c, p),            toc='Emergency Contacts',                  numbering='roman')
    add('utilities',       lambda c, p: page_utilities(c, p),                     toc='Utilities & Service Providers',       numbering='roman')
    add('sponsor_1',       lambda c, p: page_sponsor(c, 'Sponsor Showcase — I'),  toc='Sponsor Showcase — I',                numbering='roman')

    # Main matter — Arabic
    add('divider',         lambda c, p: page_section_divider(c, 'The Members', 'Plots 1 to 117  ·  Ecotech-12'),
                                                                                  toc='Member Directory',                    numbering='arabic')
    add('how_to_use',      lambda c, p: page_section_index(c, members, 1, N, p),  toc='How to Use This Directory',           numbering='arabic')

    # Member cards interleaved with mid-book sponsors
    sponsor_label_iter = iter(['Sponsor Showcase — II', 'Sponsor Showcase — III'])
    for di in range(1, dir_total + 1):
        start_i = (di - 1) * CARDS_PER_PAGE
        end_i = min(start_i + CARDS_PER_PAGE, N)
        sub = members[start_i:end_i]
        start_sr = start_i + 1

        def render_dir(c, p, sub=sub, start_sr=start_sr):
            c.setFillColor(PAPER); c.rect(0,0,PAGE_W,PAGE_H,stroke=0,fill=1)
            draw_page_chrome(c, p, 'Members')
            top = PAGE_H - 18*mm - 10*mm
            bottom = 16*mm
            avail_h = top - bottom
            avail_w = PAGE_W - 2*MARGIN
            gap_x = 6*mm; gap_y = 6*mm
            card_w = (avail_w - gap_x*(COLS-1))/COLS
            card_h = (avail_h - gap_y*(ROWS-1))/ROWS
            i = 0
            for r in range(ROWS):
                for col in range(COLS):
                    if i >= len(sub): break
                    m = sub[i]
                    cx = MARGIN + col*(card_w+gap_x)
                    cy = top - (r+1)*card_h - r*gap_y
                    directory_card(c, cx, cy, card_w, card_h, start_sr + i, m)
                    i += 1
                if i >= len(sub): break

        add('dir_page', render_dir, toc=None, numbering='arabic')
        if di in sponsor_after_dir:
            label = next(sponsor_label_iter)
            add('sponsor', (lambda c, p, lbl=label: page_sponsor(c, lbl)), toc=label, numbering='arabic')

    # Half / strip ad page between members and indexes
    add('ads_strip',       lambda c, p: page_half_strip_ads(c, p),               toc='Member Advertisements',                numbering='arabic')

    # Trade-reference indexes
    add('alpha_index',     lambda c, p: page_alpha_index(c, p, members),         toc='Alphabetical Member Index',            numbering='arabic')
    add('plot_index',      lambda c, p: page_plot_index(c, p, members),          toc='Plot Number Index',                    numbering='arabic')
    add('sector_index',    lambda c, p: page_sector_index(c, p),                 toc='Sector / Industry Classification',     numbering='arabic')
    add('products_index',  lambda c, p: page_products_index(c, p),               toc='Products & Services Index',            numbering='arabic')
    add('brands_index',    lambda c, p: page_brands_index(c, p),                 toc='Brand Names Index',                    numbering='arabic')
    add('eou_list',        lambda c, p: page_eou_list(c, p),                     toc='Export-Oriented Units',                numbering='arabic')
    add('msme_list',       lambda c, p: page_msme_list(c, p),                    toc='MSME-Classified Units',                numbering='arabic')

    # Supplementary
    add('byelaws',         lambda c, p: page_byelaws(c, p),                      toc='Bye-Laws & Membership Rules',          numbering='arabic')
    add('membership_form', lambda c, p: page_membership_form(c, p),              toc='Membership Application Form',          numbering='arabic')
    add('calendar',        lambda c, p: page_calendar(c, p),                     toc='Calendar of Events',                   numbering='arabic')
    add('ack',             lambda c, p: page_acknowledgements(c, p),             toc='Acknowledgements',                     numbering='arabic')

    # Final sponsor + back matter
    add('sponsor_4',       lambda c, p: page_sponsor(c, 'Sponsor Showcase — IV'), toc='Sponsor Showcase — IV',               numbering='arabic')
    add('notes_1',         lambda c, p: page_notes(c, p),                        toc='Notes',                                numbering='arabic')
    add('notes_2',         lambda c, p: page_notes(c, p),                        toc=None,                                   numbering='arabic')
    add('back_cover',      lambda c, p: page_back_cover(c),                      toc=None,                                   numbering='cover')

    # Assign page labels
    roman_i = 0
    arabic_i = 0
    for pg in pages:
        if pg['numbering'] == 'roman':
            roman_i += 1
            pg['page_label'] = _roman(roman_i).lower()
        elif pg['numbering'] == 'arabic':
            arabic_i += 1
            pg['page_label'] = str(arabic_i)
        else:
            pg['page_label'] = ''

    # Build TOC data
    _toc_data = []
    for pg in pages:
        if pg['toc']:
            _toc_data.append((pg['toc'], pg['page_label']))
    # Capture into the toc closure by reassigning the toc page's render lambda
    for pg in pages:
        if pg['kind'] == 'toc':
            pg['render'] = (lambda c, p, data=_toc_data: page_toc(c, p, data))
            break

    # ---- Render ----
    out_path = '/sessions/keen-charming-dijkstra/mnt/outputs/Ecotech-12_Member_Directory_v2.pdf'
    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle('Ecotech-12 Industries Association — Member Directory')
    c.setAuthor('Ecotech-12 Industries Association')
    for pg in pages:
        pg['render'](c, pg['page_label'])
        c.showPage()
    c.save()
    print('Wrote', out_path)
    print('Total pages:', len(pages))
    print('Total members parsed:', N)

if __name__ == '__main__':
    build()
