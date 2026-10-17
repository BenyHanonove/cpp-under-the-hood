"""
styles.py - CSS styling for the Silicon Hardware Security Engineering Guide
"""

CSS_STYLES = """
@page {
    size: A4;
    margin: 18mm 14mm 18mm 14mm;
}

@page :first {
    margin: 0;
}

* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Liberation Sans", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
}

/* Cover Page */
.cover-page {
    page-break-after: always;
    height: 100vh;
    min-height: 290mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 40mm 25mm 25mm 25mm;
    background: linear-gradient(135deg, #091e3a 0%, #102a4e 50%, #1a365d 100%);
    color: #ffffff;
    box-sizing: border-box;
}

.cover-badge {
    display: inline-block;
    background: rgba(217, 119, 6, 0.25);
    border: 1px solid #d97706;
    color: #fbbf24;
    font-weight: 700;
    font-size: 11pt;
    letter-spacing: 2px;
    padding: 6px 16px;
    border-radius: 4px;
    text-transform: uppercase;
    margin-bottom: 25px;
}

.cover-title {
    font-size: 32pt;
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 15px 0;
    color: #ffffff;
    letter-spacing: -0.5px;
}

.cover-subtitle {
    font-size: 15pt;
    font-weight: 400;
    line-height: 1.4;
    color: #94a3b8;
    margin: 0 0 35px 0;
    max-width: 90%;
}

.cover-divider {
    width: 80px;
    height: 4px;
    background: #d97706;
    margin-bottom: 35px;
    border-radius: 2px;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 20px;
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.cover-meta-item h4 {
    margin: 0 0 5px 0;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #38bdf8;
}

.cover-meta-item p {
    margin: 0;
    font-size: 10pt;
    color: #e2e8f0;
}

.cover-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 20px;
    display: flex;
    justify-content: space-between;
    font-size: 9pt;
    color: #64748b;
}

/* Part Break Pages */
.part-page {
    page-break-before: always;
    page-break-after: always;
    min-height: 250mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 30mm 20mm;
    background: #f8fafc;
    border-left: 12px solid #0f2b48;
}

.part-number {
    font-size: 14pt;
    font-weight: 800;
    color: #d97706;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.part-title {
    font-size: 28pt;
    font-weight: 800;
    color: #0f2b48;
    line-height: 1.2;
    margin: 0 0 20px 0;
}

.part-desc {
    font-size: 12pt;
    color: #475569;
    line-height: 1.6;
    max-width: 90%;
}

.part-chapters-list {
    margin-top: 30px;
    padding: 20px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

.part-chapters-list h4 {
    margin: 0 0 12px 0;
    color: #0f2b48;
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.part-chapters-list ul {
    margin: 0;
    padding-left: 20px;
}

.part-chapters-list li {
    margin-bottom: 8px;
    color: #334155;
    font-size: 10pt;
}

/* Headings */
h1 {
    font-size: 20pt;
    font-weight: 800;
    color: #0f2b48;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 25px;
    margin-bottom: 15px;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-top: 22px;
    margin-bottom: 10px;
    page-break-after: avoid;
    border-left: 4px solid #3b82f6;
    padding-left: 10px;
}

h3 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

p {
    margin: 0 0 10px 0;
    text-align: justify;
}

/* Code & Preformatted */
code {
    font-family: "Liberation Mono", "DejaVu Sans Mono", Consolas, monospace;
    font-size: 8.8pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}

pre {
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 12px 14px;
    border-radius: 6px;
    font-family: "Liberation Mono", "DejaVu Sans Mono", Consolas, monospace;
    font-size: 8.2pt;
    line-height: 1.45;
    overflow-x: auto;
    page-break-inside: avoid;
    break-inside: avoid;
    margin: 12px 0 16px 0;
    border: 1px solid #1e293b;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
}

/* Syntax Highlighting Colors */
.kwd { color: #f472b6; font-weight: 600; }  /* Pink for keywords */
.typ { color: #38bdf8; font-weight: 600; }  /* Cyan for types */
.fn  { color: #c084fc; }                    /* Purple for functions */
.com { color: #94a3b8; font-style: italic; }/* Slate for comments */
.str { color: #4ade80; }                    /* Green for strings */
.num { color: #fbbf24; }                    /* Amber for numbers */
.reg { color: #f87171; font-weight: 600; }  /* Red for HW registers */
.dir { color: #e879f9; }                    /* Violet for preprocessor */

/* Callout Boxes */
.callout {
    margin: 14px 0;
    padding: 12px 14px;
    border-radius: 6px;
    page-break-inside: avoid;
    break-inside: avoid;
    font-size: 9.3pt;
}

.callout-header {
    display: flex;
    align-items: center;
    font-weight: 700;
    margin-bottom: 6px;
    text-transform: uppercase;
    font-size: 8.5pt;
    letter-spacing: 0.8px;
}

.callout-def {
    background-color: #f0fdf4;
    border-left: 4px solid #10b981;
    color: #064e3b;
}
.callout-def .callout-header { color: #047857; }

.callout-why {
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e3a8a;
}
.callout-why .callout-header { color: #1d4ed8; }

.callout-hw {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #78350f;
}
.callout-hw .callout-header { color: #b45309; }

.callout-sec {
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #7f1d1d;
}
.callout-sec .callout-header { color: #b91c1c; }

.callout-arm {
    background-color: #faf5ff;
    border-left: 4px solid #a855f7;
    color: #581c87;
}
.callout-arm .callout-header { color: #7e22ce; }

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
    break-inside: avoid;
}

th, td {
    padding: 8px 10px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

th {
    background-color: #0f2b48;
    color: #ffffff;
    font-weight: 600;
    letter-spacing: 0.5px;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

tr:hover td {
    background-color: #f1f5f9;
}

/* ASCII Diagrams */
.diagram {
    background-color: #09131f;
    color: #38bdf8;
    padding: 12px;
    border-radius: 6px;
    font-family: "Liberation Mono", Consolas, monospace;
    font-size: 8pt;
    line-height: 1.25;
    margin: 12px 0;
    page-break-inside: avoid;
    break-inside: avoid;
    border: 1px solid #1e3a5f;
    white-space: pre;
}

/* Metadata bar for Chapters */
.chapter-meta {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 8.5pt;
    color: #475569;
}

.chapter-meta-tag {
    font-weight: 600;
    color: #0f2b48;
}

/* Utility */
.page-break {
    page-break-after: always;
}

.no-break {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Table of Contents */
.toc-page {
    page-break-after: always;
    padding: 10mm 5mm;
}

.toc-title {
    font-size: 22pt;
    font-weight: 800;
    color: #0f2b48;
    border-bottom: 3px solid #0f2b48;
    padding-bottom: 8px;
    margin-bottom: 20px;
}

.toc-part-row {
    font-size: 11pt;
    font-weight: 700;
    color: #0f2b48;
    margin-top: 15px;
    margin-bottom: 6px;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 3px;
    display: flex;
    justify-content: space-between;
}

.toc-chapter-row {
    font-size: 9.2pt;
    color: #334155;
    padding: 3px 0 3px 12px;
    display: flex;
    justify-content: space-between;
}

.toc-chapter-row:hover {
    color: #0284c7;
}

.toc-dots {
    flex-grow: 1;
    border-bottom: 1px dotted #94a3b8;
    margin: 0 8px 3px 8px;
}

/* Glossary Index */
.glossary-entry {
    margin-bottom: 12px;
    page-break-inside: avoid;
    break-inside: avoid;
}

.glossary-term {
    font-size: 9.8pt;
    font-weight: 700;
    color: #0f2b48;
    font-family: "Liberation Mono", monospace;
    display: inline-block;
    background: #e2e8f0;
    padding: 1px 6px;
    border-radius: 4px;
}

.glossary-category {
    font-size: 8pt;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-left: 8px;
}

.glossary-desc {
    margin-top: 4px;
    font-size: 8.8pt;
    color: #334155;
}
"""
