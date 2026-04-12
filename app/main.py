import subprocess
from pathlib import Path


from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.bigquery_client import (
    get_last_refresh_timestamp,
    get_latest_submission,
    get_revenue_by_store,
    get_submitted_orders_metrics,
    get_summary_metrics,
    save_csv_submissions,
    get_pipeline_observability_metrics,

)


app = FastAPI(title="Retail BigQuery Webapp", version="1.0.0")

DBT_DOCS_DIR = Path("target")
DBT_DOCS_ENABLED = DBT_DOCS_DIR.exists()

def _prepare_dbt_docs() -> None:
    index_path = DBT_DOCS_DIR / "index.html"
    if not index_path.exists():
        return

    html = index_path.read_text(encoding="utf-8")
    broken_favicon = "${require('./assets/favicons/favicon.ico')}"
    if broken_favicon in html:
        index_path.write_text(
            html.replace(broken_favicon, "data:,"),
            encoding="utf-8",
        )

if DBT_DOCS_ENABLED:
    _prepare_dbt_docs()
    app.mount("/dbt-docs", StaticFiles(directory=str(DBT_DOCS_DIR), html=True), name="dbt-docs")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/summary")
def summary() -> dict:
    try:
        return get_summary_metrics()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/chart/revenue-by-store")
def revenue_by_store() -> dict:
    try:
        return {"items": get_revenue_by_store()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _run_pipeline() -> str:
    result = subprocess.run(
        [
            "dbt",
            "run",
            "--profiles-dir",
            ".",
            "--select",
            "stg_json_submissions",
            "fct_submitted_orders",
            "fct_orders",
            "fct_order_items",
        ],
        cwd=".",
        capture_output=True,
        text=True,
        check=True,
    )

    message = "Pipeline processed successfully."
    if result.stdout:
        tail = result.stdout.strip().splitlines()[-1]
        if tail:
            message = f"{message} Last output: {tail}"

    return message


@app.post("/upload-csv")
async def upload_csv(csv_file: UploadFile = File(...)):
    try:
        if not csv_file.filename or not csv_file.filename.lower().endswith(".csv"):
            return RedirectResponse(
                url="/?message=Please upload a CSV file.",
                status_code=303,
            )

        file_bytes = await csv_file.read()
        result = save_csv_submissions(file_bytes)
        upload_message = (
            f"CSV uploaded successfully. "
            f"Rows saved: {result['row_count']} | Submitted at: {result['submitted_at']}"
        )
        pipeline_message = _run_pipeline()
        message = f"{upload_message} | {pipeline_message}"
        return RedirectResponse(url=f"/?message={message}", status_code=303)
    except subprocess.CalledProcessError as exc:
        error_text = exc.stderr.strip() if exc.stderr else str(exc)
        return RedirectResponse(
            url=f"/?message=CSV uploaded, but pipeline processing failed: {error_text}",
            status_code=303,
        )
    except Exception as exc:
        return RedirectResponse(url=f"/?message=Submission failed: {exc}", status_code=303)

@app.post("/process-pipeline")
def process_pipeline():
    try:
        message = _run_pipeline()
        return RedirectResponse(url=f"/?message={message}", status_code=303)

    except subprocess.CalledProcessError as exc:
        error_text = exc.stderr.strip() if exc.stderr else str(exc)
        return RedirectResponse(
            url=f"/?message=Pipeline processing failed: {error_text}",
            status_code=303,
        )
    except Exception as exc:
        return RedirectResponse(
            url=f"/?message=Pipeline processing failed: {exc}",
            status_code=303,
        )


@app.get("/", response_class=HTMLResponse)
def home(message: str = "") -> str:
    try:
        summary_data = get_summary_metrics()
        last_refresh = get_last_refresh_timestamp()
        latest_submission = get_latest_submission()
        submitted_orders_metrics = get_submitted_orders_metrics()
        observability_metrics = get_pipeline_observability_metrics()
    except Exception as exc:
        summary_data = {
            "project_id": "Unavailable",
            "dataset": "Unavailable",
            "total_customers": "-",
            "total_stores": "-",
            "total_orders": "-",
            "total_order_lines": "-",
            "total_revenue": "-",
        }
        last_refresh = f"Error: {exc}"
        latest_submission = {
            "submission_id": "Unavailable",
            "submitted_at": "Unavailable",
            "fields": {"error": str(exc)},
        }
        submitted_orders_metrics = {
            "total_submitted_orders": "-",
            "submitted_revenue": "-",
            "latest_submitted_order_date": "Unavailable",
        }
        observability_metrics = {
            "raw_submission_count": "-",
            "staged_submission_count": "-",
            "fact_submission_count": "-",
            "latest_raw_submission_at": "Unavailable",
            "latest_fact_submission_at": "Unavailable",
        }
    message_html = ""
    if message:
        message_html = f'<div class="status">{message}</div>'

    latest_fields_html = ""
    if latest_submission["fields"]:
        rows_html = "".join(
            f"<tr><th>{str(key).replace('_', ' ').title()}</th><td>{value}</td></tr>"
            for key, value in latest_submission["fields"].items()
        )
        latest_fields_html = f'<table class="record-table">{rows_html}</table>'
    else:
        latest_fields_html = "<p class='mini'>No submission fields available.</p>"

    docs_link_html = (
        '<div><strong>Technical docs:</strong> '
        '<a href="/dbt-docs/index.html" target="_blank" rel="noopener noreferrer" '
        'style="color: var(--accent); text-decoration: none; font-weight: 700;">'
        'View dbt Docs</a></div>'
        if DBT_DOCS_ENABLED
        else ""
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Retail Analytics Dashboard</title>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <style>
        html {{
          scroll-behavior: smooth;
        }}
        :root {{
          --bg: #0f1419;
          --bg-2: #151c24;
          --panel: rgba(24, 32, 42, 0.88);
          --hero: rgba(20, 28, 38, 0.92);
          --ink: #f4efe6;
          --muted: #aab7c4;
          --line: rgba(255, 255, 255, 0.10);
          --accent: #2ec4b6;
          --accent-2: #ff9f43;
          --accent-3: #7c83fd;
          --card: rgba(22, 30, 40, 0.92);
          --shadow: rgba(0, 0, 0, 0.35);
        }}

        * {{
          box-sizing: border-box;
        }}
        body {{
          margin: 0;
          font-family: Georgia, "Times New Roman", serif;
          background:
            radial-gradient(circle at top left, rgba(255, 159, 67, 0.20), transparent 22%),
            radial-gradient(circle at top right, rgba(46, 196, 182, 0.18), transparent 24%),
            radial-gradient(circle at bottom left, rgba(124, 131, 253, 0.16), transparent 22%),
            linear-gradient(160deg, var(--bg), var(--bg-2));
          color: var(--ink);
        }}

        .container {{
          width: 100%;
          max-width: none;
          margin: 0;
          padding: 0;
          position: relative;
        }}
        .page-shell {{
          position: relative;
          min-height: 100vh;
          padding: 32px 20px 64px 86px;
          transition: padding-left 0.28s ease;
        }}
        .page-shell.sidebar-expanded {{
          padding-left: 308px;
        }}
        .sidebar {{
          position: fixed;
          top: 0;
          left: 0;
          bottom: 0;
          z-index: 40;
          width: 54px;
          overflow: visible;
          background:
            linear-gradient(180deg, rgba(18, 25, 35, 0.98), rgba(11, 18, 26, 0.98)),
            radial-gradient(circle at top, rgba(124, 131, 253, 0.18), transparent 28%);
          border-right: 1px solid rgba(255, 255, 255, 0.06);
          box-shadow: 16px 0 44px rgba(0, 0, 0, 0.22);
          transition: width 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
        }}
        .sidebar.expanded {{
          width: 274px;
          border-color: rgba(124, 131, 253, 0.24);
          box-shadow: 18px 0 52px rgba(0, 0, 0, 0.3);
        }}
        .sidebar-inner {{
          display: flex;
          flex-direction: column;
          height: 100%;
          padding: 20px 14px 18px;
        }}
        .sidebar-brand {{
          display: flex;
          align-items: center;
          gap: 12px;
          min-height: 52px;
          margin-bottom: 20px;
          padding: 8px 8px 14px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .sidebar:not(.expanded) .sidebar-brand {{
          justify-content: center;
          padding: 0;
          min-height: 0;
          margin-bottom: 0;
          border-bottom: none;
        }}
        .sidebar-brand-mark {{
          display: grid;
          place-items: center;
          width: 44px;
          height: 44px;
          border-radius: 16px;
          background: linear-gradient(180deg, rgba(124, 131, 253, 0.24), rgba(46, 196, 182, 0.16));
          color: #dff8f4;
          font-size: 19px;
          font-weight: 700;
          flex-shrink: 0;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }}
        .sidebar-brand-copy {{
          opacity: 0;
          transform: translateX(8px);
          transition: opacity 0.2s ease, transform 0.2s ease;
          white-space: nowrap;
        }}
        .sidebar.expanded .sidebar-brand-copy {{
          opacity: 1;
          transform: translateX(0);
        }}
        .sidebar-brand-copy strong {{
          display: block;
          font-size: 17px;
          color: var(--ink);
        }}
        .sidebar-brand-copy span {{
          display: block;
          font-size: 11px;
          color: var(--muted);
          margin-top: 2px;
        }}
        .sidebar-toggle {{
          position: absolute;
          top: 112px;
          right: -15px;
          width: 36px;
          height: 36px;
          border-radius: 999px;
          border: 1px solid rgba(255, 255, 255, 0.08);
          background: #f6f1e8;
          color: #16202b;
          cursor: pointer;
          font-size: 18px;
          line-height: 1;
          box-shadow: 0 12px 26px rgba(0, 0, 0, 0.28);
          display: grid;
          place-items: center;
          transition: transform 0.18s ease;
        }}
        .sidebar:not(.expanded) .sidebar-toggle {{
          top: 50%;
          left: 50%;
          right: auto;
          transform: translate(-50%, -50%);
        }}
        .sidebar-toggle:hover {{
          transform: scale(1.04);
        }}
        .sidebar:not(.expanded) .sidebar-toggle:hover {{
          transform: translate(-50%, -50%) scale(1.04);
        }}
        .sidebar-nav {{
          display: grid;
          gap: 12px;
          margin-top: 22px;
          flex: 1;
          align-content: start;
        }}
        .sidebar:not(.expanded) .sidebar-nav {{
          margin-top: 0;
          gap: 0;
        }}
        .sidebar-link {{
          display: grid;
          grid-template-columns: 44px 1fr;
          align-items: center;
          min-height: 58px;
          padding: 10px 12px;
          border-radius: 20px;
          color: var(--ink);
          text-decoration: none;
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 255, 255, 0.06);
          transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
        }}
        .sidebar:not(.expanded) .sidebar-link {{
          display: none;
        }}
        .sidebar-link:hover {{
          transform: translateX(2px);
          border-color: rgba(124, 131, 253, 0.34);
          background: rgba(124, 131, 253, 0.09);
        }}
        .sidebar:not(.expanded) .sidebar-link:hover {{
          transform: none;
        }}
        .sidebar-icon {{
          display: grid;
          place-items: center;
          width: 36px;
          height: 36px;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.05);
          color: #dff8f4;
          font-size: 17px;
          font-weight: 700;
        }}
        .sidebar-copy {{
          min-width: 0;
          opacity: 0;
          transform: translateX(6px);
          transition: opacity 0.18s ease, transform 0.18s ease;
        }}
        .sidebar.expanded .sidebar-copy {{
          opacity: 1;
          transform: translateX(0);
        }}
        .sidebar-copy strong {{
          display: block;
          font-size: 15px;
          margin-bottom: 3px;
          white-space: nowrap;
        }}
        .sidebar-copy span {{
          display: block;
          font-size: 11px;
          color: var(--muted);
          line-height: 1.45;
        }}
        .sidebar-footer {{
          margin-top: auto;
          padding-top: 14px;
          border-top: 1px solid rgba(255, 255, 255, 0.06);
          display: grid;
          grid-template-columns: 44px 1fr;
          gap: 10px;
          align-items: center;
        }}
        .sidebar:not(.expanded) .sidebar-footer {{
          display: none;
        }}
        .sidebar-avatar {{
          display: grid;
          place-items: center;
          width: 40px;
          height: 40px;
          border-radius: 14px;
          background: rgba(255, 255, 255, 0.05);
          color: var(--accent-2);
          font-weight: 700;
        }}
        .sidebar-footer-copy {{
          opacity: 0;
          transform: translateX(8px);
          transition: opacity 0.2s ease, transform 0.2s ease;
          white-space: nowrap;
        }}
        .sidebar.expanded .sidebar-footer-copy {{
          opacity: 1;
          transform: translateX(0);
        }}
        .sidebar-footer-copy strong {{
          display: block;
          font-size: 14px;
        }}
        .sidebar-footer-copy span {{
          display: block;
          font-size: 11px;
          color: var(--muted);
          margin-top: 2px;
        }}
        .main-content {{
          min-width: 0;
          width: 100%;
          max-width: 1380px;
          margin: 0 auto;
        }}
        .sidebar-rail-spacer {{
          flex: 1;
        }}
        .hero {{
          background: linear-gradient(135deg, rgba(22, 30, 40, 0.95), rgba(15, 21, 29, 0.98));
          border: 1px solid var(--line);
          border-radius: 24px;
          padding: 28px;
          box-shadow: 0 20px 50px var(--shadow);
        }}

        .eyebrow {{
          display: inline-block;
          font-size: 12px;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: var(--accent);
          margin-bottom: 12px;
        }}
        h1 {{
          margin: 0 0 10px;
          font-size: 42px;
          line-height: 1.05;
        }}
        .sub {{
          margin: 0;
          max-width: 760px;
          color: var(--muted);
          font-size: 18px;
          line-height: 1.6;
        }}
        .meta {{
          margin-top: 20px;
          display: grid;
          gap: 10px;
          color: var(--muted);
          font-size: 14px;
        }}
        .section-header {{
          margin-top: 42px;
          padding: 0 2px 0;
        }}
        .section-divider {{
          width: 100%;
          height: 1px;
          margin: 18px 0 22px;
          background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0),
            rgba(124, 131, 253, 0.22),
            rgba(46, 196, 182, 0.28),
            rgba(255, 159, 67, 0.18),
            rgba(255, 255, 255, 0)
          );
        }}
        .section-kicker {{
          display: inline-block;
          font-size: 20px;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: var(--accent-2);
          margin-bottom: 10px;
          font-weight: 700;
        }}
        .section-header h2 {{
          margin: 0 0 8px;
          font-size: 28px;
        }}
        .section-copy {{
          margin: 0;
          color: var(--muted);
          line-height: 1.6;
          max-width: 760px;
        }}
        .grid {{
          display: grid;
          gap: 18px;
          margin-top: 24px;
        }}
        .cards {{
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        }}

        
        .card {{
          background: linear-gradient(180deg, rgba(28, 37, 49, 0.96), rgba(19, 26, 35, 0.96));
          border: 1px solid var(--line);
          border-radius: 20px;
          padding: 18px;
          box-shadow: 0 12px 28px var(--shadow);
        }}

        .card h3 {{
          margin: 0 0 8px;
          font-size: 14px;
          color: var(--muted);
          text-transform: uppercase;
          letter-spacing: 0.06em;
        }}
        .value {{
          font-size: 34px;
          font-weight: 700;
          color: var(--accent);
          text-shadow: 0 0 18px rgba(46, 196, 182, 0.18);
        }}

        .layout {{
          margin-top: 26px;
          display: grid;
          gap: 18px;
          grid-template-columns: 1.15fr 0.85fr;
        }}
        .panel {{
          background: linear-gradient(180deg, rgba(24, 32, 42, 0.95), rgba(17, 24, 32, 0.96));
          border: 1px solid var(--line);
          border-radius: 24px;
          padding: 22px;
          box-shadow: 0 16px 36px var(--shadow);
        }}

        .panel h2 {{
          margin: 0 0 10px;
          font-size: 24px;
        }}
        .panel p {{
          color: var(--muted);
          line-height: 1.6;
        }}
        textarea {{
          width: 100%;
          min-height: 220px;
          margin-top: 12px;
          border: 1px solid var(--line);
          border-radius: 16px;
          padding: 14px;
          background: rgba(10, 14, 20, 0.92);
          font-family: "SFMono-Regular", Consolas, monospace;
          font-size: 13px;
          color: #f7f3eb;
          resize: vertical;
        }}

        .button {{
          display: inline-block;
          margin-top: 14px;
          background: var(--accent);
          color: white;
          border: none;
          border-radius: 999px;
          padding: 12px 18px;
          font-size: 14px;
          cursor: pointer;
        }}
        .status {{
          margin-top: 14px;
          padding: 12px 14px;
          border-radius: 14px;
          background: rgba(255, 159, 67, 0.14);
          border: 1px solid rgba(255, 159, 67, 0.24);
          color: #ffd29b;
          font-size: 14px;
          line-height: 1.5;
        }}

        .list {{
          margin: 12px 0 0;
          padding-left: 18px;
          color: var(--muted);
          line-height: 1.7;
        }}
        .mini {{
          font-size: 13px;
          color: var(--muted);
        }}
        canvas {{
          margin-top: 10px;
          max-height: 320px;
        }}
        .footer-note {{
          margin-top: 12px;
          font-size: 13px;
          color: var(--muted);
        }}
        .record-table {{
          width: 100%;
          margin-top: 14px;
          border-collapse: collapse;
          background: rgba(10, 14, 20, 0.82);
          border: 1px solid var(--line);
          border-radius: 16px;
          overflow: hidden;
        }}

        .record-table th,
        .record-table td {{
          padding: 12px 14px;
          border-bottom: 1px solid var(--line);
          text-align: left;
          vertical-align: top;
          font-size: 14px;
        }}
        .record-table th {{
          width: 38%;
          background: rgba(46, 196, 182, 0.12);
          color: var(--ink);
          font-weight: 700;
        }}

        .record-table td {{
          color: var(--muted);
          word-break: break-word;
        }}


        @media (max-width: 920px) {{
          .page-shell {{
            padding: 24px 16px 56px 76px;
          }}
          .page-shell.sidebar-expanded {{
            padding-left: 258px;
          }}
          .sidebar {{
            width: 46px;
            left: 0;
            top: 0;
            bottom: 0;
          }}
          .sidebar.expanded {{
            width: 232px;
          }}
          .sidebar-toggle {{
            top: 106px;
          }}
          .layout {{
            grid-template-columns: 1fr;
          }}
          h1 {{
            font-size: 34px;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="page-shell">
          <aside class="sidebar expanded" id="sectionSidebar">
            <div class="sidebar-inner">
              <div class="sidebar-brand">
                <div class="sidebar-brand-mark">R</div>
                <div class="sidebar-brand-copy">
                  <strong>RetailFlow</strong>
                  <span>Data demo workspace</span>
                </div>
              </div>
              <button class="sidebar-toggle" type="button" aria-label="Toggle navigation" onclick="toggleSidebar()">‹</button>
              <nav class="sidebar-nav">
                <a class="sidebar-link" href="#pipeline-view">
                  <div class="sidebar-icon">↺</div>
                  <div class="sidebar-copy">
                    <strong>Pipeline View</strong>
                    <span>Submission, observability, and workflow status</span>
                  </div>
                </a>
                <a class="sidebar-link" href="#business-view">
                  <div class="sidebar-icon">◪</div>
                  <div class="sidebar-copy">
                    <strong>Business View</strong>
                    <span>KPIs, incremental results, and chart output</span>
                  </div>
                </a>
              </nav>
              <div class="sidebar-rail-spacer"></div>
              <div class="sidebar-footer">
                <div class="sidebar-avatar">dbt</div>
                <div class="sidebar-footer-copy">
                  <strong>Analytics App</strong>
                  <span>FastAPI + BigQuery</span>
                </div>
              </div>
            </div>
          </aside>

          <main class="main-content">
        <section class="hero">
          <div class="eyebrow">Retail Analytics Demo</div>
          <h1>dbt + BigQuery + FastAPI Dashboard</h1>
          <p class="sub">
            This public dashboard is the first layer of the workflow app. It already exposes
            live analytics from dbt-built mart tables, and the JSON submission area below is
            the next step toward demonstrating incremental processing.
          </p>
          <div class="meta">
            <div><strong>Project:</strong> {summary_data["project_id"]}</div>
            <div><strong>Dataset:</strong> {summary_data["dataset"]}</div>
            <div><strong>Last analytics refresh:</strong> {last_refresh}</div>
            <div><strong>Latest submission:</strong> {latest_submission["submitted_at"]}</div>
            <div><strong>Latest submission ID:</strong> {latest_submission["submission_id"]}</div>
            {docs_link_html}
          </div>
        </section>

        <div class="section-divider"></div>
        <section class="section-header" id="pipeline-view">
          <div class="section-kicker">Workflow View</div>
          <h2>Submission and Pipeline Monitoring</h2>
          <p class="section-copy">
            This section focuses on the ingestion workflow: receiving uploaded CSV data, recording the latest
            submission, and showing whether the pipeline is moving data from raw intake into dbt
            staging and the incremental fact table.
          </p>
        </section>

        <section class="layout">
          <div class="panel">
            <h2>CSV Submission Intake</h2>
            <p>
              Upload a retail-style CSV file where each row represents one order line. Repeated
              order header fields let the same file update both order-level and order-item facts.
            </p>
            <form
              id="csv-upload-form"
              method="post"
              action="/upload-csv"
              enctype="multipart/form-data"
              style="display: block; width: 100%;"
            >
              <div style="margin-top: 14px; border: 1px dashed var(--line); border-radius: 16px; padding: 18px; background: rgba(10, 14, 20, 0.55);">
                <label for="csv_file" style="display: block; font-weight: 700; color: var(--ink); margin-bottom: 8px;">Upload CSV file</label>
                <input
                  id="csv_file"
                  name="csv_file"
                  type="file"
                  accept=".csv,text/csv"
                  style="display: block; width: 100%; color: var(--muted);"
                  required
                />
                <p class="mini" style="margin: 12px 0 0;">
                  Required columns: order_id, customer_id, store_id, order_date, order_amount, order_status,
                  order_line_id, product_id, quantity, unit_price, line_amount
                </p>
              </div>
            </form>
            <div style="display: flex; gap: 12px; align-items: center; margin-top: 14px; flex-wrap: nowrap;">
              <button type="submit" form="csv-upload-form" class="button" style="margin-top: 0;">Upload and Process</button>
            </div>

            {message_html}
          </div>

          <div class="panel">
            <h2>Latest Submitted Record</h2>
            <p>This is the newest record saved into the intake table.</p>
            {latest_fields_html}
            <p class="footer-note">
              Technical users can inspect the API at <strong>/summary</strong> and <strong>/docs</strong>{' or open <a href="/dbt-docs/index.html" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: none; font-weight: 700;">dbt Docs</a>' if DBT_DOCS_ENABLED else ''}.
            </p>
          </div>
        </section>

        <section class="panel" style="margin-top: 18px;">
          <h2>Pipeline Observability</h2>
          <p class="mini">
            These checks help confirm whether the intake, staging, and incremental fact layers are aligned.
          </p>
          <table class="record-table">
            <tr>
              <th>Raw submission count</th>
              <td>{observability_metrics["raw_submission_count"]}</td>
            </tr>
            <tr>
              <th>Staged submission count</th>
              <td>{observability_metrics["staged_submission_count"]}</td>
            </tr>
            <tr>
              <th>Incremental fact count</th>
              <td>{observability_metrics["fact_submission_count"]}</td>
            </tr>
            <tr>
              <th>Latest raw submission</th>
              <td>{observability_metrics["latest_raw_submission_at"]}</td>
            </tr>
            <tr>
              <th>Latest fact submission</th>
              <td>{observability_metrics["latest_fact_submission_at"]}</td>
            </tr>
          </table>
        </section>

        <div class="section-divider"></div>
        <section class="section-header" id="business-view">
          <div class="section-kicker">Business View</div>
          <h2>Business KPIs and Outcome Metrics</h2>
          <p class="section-copy">
            This section shows the business-facing analytics layer. It combines your broader mart
            KPIs with the newer submission-driven incremental metrics so viewers can connect the
            pipeline work to visible business outcomes.
          </p>
        </section>

        <section class="grid cards">
          <div class="card">
            <h3>Total Customers</h3>
            <div class="value">{summary_data["total_customers"]}</div>
          </div>
          <div class="card">
            <h3>Total Stores</h3>
            <div class="value">{summary_data["total_stores"]}</div>
          </div>
          <div class="card">
            <h3>Total Orders</h3>
            <div class="value">{summary_data["total_orders"]}</div>
          </div>
          <div class="card">
            <h3>Order Lines</h3>
            <div class="value">{summary_data["total_order_lines"]}</div>
          </div>
          <div class="card">
            <h3>Total Revenue</h3>
            <div class="value">{summary_data["total_revenue"]}</div>
          </div>
        </section>

        <section class="grid cards">
          <div class="card">
            <h3>Submitted Orders</h3>
            <div class="value">{submitted_orders_metrics["total_submitted_orders"]}</div>
          </div>
          <div class="card">
            <h3>Submitted Revenue</h3>
            <div class="value">{submitted_orders_metrics["submitted_revenue"]}</div>
          </div>
          <div class="card">
            <h3>Latest Submitted Order Date</h3>
            <div class="value" style="font-size: 24px;">{submitted_orders_metrics["latest_submitted_order_date"]}</div>
          </div>
        </section>

        <section class="panel" style="margin-top: 18px;">
          <h2>Revenue by Store</h2>
          <p class="mini">
            Simple live chart from the analytics mart layer. This gives the dashboard a quick,
            easy-to-see public view before we add submission tracking and richer workflow state.
          </p>
          <canvas id="revenueChart"></canvas>
        </section>
          </main>
        </div>
      </div>

      <script>
        async function loadRevenueChart() {{
          const response = await fetch("/chart/revenue-by-store");
          const payload = await response.json();

          const labels = payload.items.map(item => item.store_name);
          const values = payload.items.map(item => item.revenue);

          const ctx = document.getElementById("revenueChart").getContext("2d");
          new Chart(ctx, {{
            type: "bar",
            data: {{
              labels,
              datasets: [{{
                label: "Revenue",
                data: values,
                backgroundColor: [
                  "#1d6b52",
                  "#d98c2b",
                  "#316b83",
                  "#8e5a9f",
                  "#bc5a45",
                  "#6d8a2e"
                ],
                borderRadius: 8
              }}]
            }},
            options: {{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {{
                legend: {{
                  display: false
                }}
              }},
              scales: {{
                y: {{
                  beginAtZero: true
                }}
              }}
            }}
          }});
        }}

        function toggleSidebar() {{
          const sidebar = document.getElementById("sectionSidebar");
          const shell = document.querySelector(".page-shell");
          sidebar.classList.toggle("expanded");
          shell.classList.toggle("sidebar-expanded", sidebar.classList.contains("expanded"));
          const toggle = sidebar.querySelector(".sidebar-toggle");
          toggle.textContent = sidebar.classList.contains("expanded") ? "‹" : "›";
        }}

        function syncSidebarForViewport() {{
          const sidebar = document.getElementById("sectionSidebar");
          const shell = document.querySelector(".page-shell");
          const toggle = sidebar.querySelector(".sidebar-toggle");
          const desktop = window.innerWidth > 920;

          if (desktop) {{
            sidebar.classList.add("expanded");
            shell.classList.add("sidebar-expanded");
            toggle.textContent = "‹";
          }} else {{
            sidebar.classList.remove("expanded");
            shell.classList.remove("sidebar-expanded");
            toggle.textContent = "›";
          }}
        }}

        window.addEventListener("resize", syncSidebarForViewport);
        syncSidebarForViewport();
        loadRevenueChart();
      </script>
    </body>
    </html>
    """
