"""
Storage-Location-3D-Display - DB Viewer
Web-based SQLite database browser for ZONMA, LOCMA, STKKA tables.
"""
import sqlite3
import json
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Storage-Location-3D-Display | DB Viewer</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; }
.header { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 16px 24px; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 16px; }
.header h1 { font-size: 18px; color: #38bdf8; font-weight: 600; }
.header .badge { background: #164e63; color: #67e8f9; font-size: 11px; padding: 3px 8px; border-radius: 4px; }
.container { display: flex; height: calc(100vh - 56px); }

/* Sidebar */
.sidebar { width: 280px; background: #1e293b; border-right: 1px solid #334155; overflow-y: auto; flex-shrink: 0; }
.sidebar h3 { padding: 16px 16px 8px; font-size: 11px; text-transform: uppercase; color: #64748b; letter-spacing: 1px; }
.table-item { padding: 10px 16px; cursor: pointer; border-left: 3px solid transparent; transition: all 0.15s; display: flex; justify-content: space-between; align-items: center; }
.table-item:hover { background: #334155; }
.table-item.active { background: #1e3a5f; border-left-color: #38bdf8; }
.table-item .name { font-size: 14px; font-weight: 500; }
.table-item .info { font-size: 11px; color: #64748b; }
.table-item .count { font-size: 11px; background: #334155; padding: 2px 8px; border-radius: 10px; color: #94a3b8; }

/* Main */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.toolbar { padding: 12px 20px; background: #1e293b; border-bottom: 1px solid #334155; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.sql-input { flex: 1; min-width: 300px; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 8px 14px; border-radius: 6px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; outline: none; }
.sql-input:focus { border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56,189,248,0.15); }
.btn { padding: 8px 18px; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; border: none; transition: all 0.15s; }
.btn-primary { background: #0ea5e9; color: white; }
.btn-primary:hover { background: #0284c7; }
.btn-secondary { background: #334155; color: #e2e8f0; }
.btn-secondary:hover { background: #475569; }

/* Results */
.results { flex: 1; overflow: auto; padding: 0; }
.result-info { padding: 8px 20px; background: #1e293b; font-size: 12px; color: #64748b; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { position: sticky; top: 0; background: #1e293b; color: #94a3b8; font-weight: 600; text-align: left; padding: 10px 12px; border-bottom: 2px solid #334155; white-space: nowrap; font-size: 12px; text-transform: uppercase; z-index:1; }
td { padding: 8px 12px; border-bottom: 1px solid #1e293b; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
tr:hover td { background: #1e293b; }
tr:nth-child(even) td { background: rgba(30,41,59,0.3); }
tr:nth-child(even):hover td { background: #1e293b; }
td.null { color: #64748b; font-style: italic; }

/* Schema view */
.schema-table { margin: 20px; }
.schema-table h3 { color: #38bdf8; margin-bottom: 12px; font-size: 16px; }
.col-row { display: grid; grid-template-columns: 30px 180px 120px 80px 1fr; gap: 8px; padding: 6px 12px; font-size: 13px; border-bottom: 1px solid #1e293b; }
.col-row.header-row { color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; border-bottom: 2px solid #334155; }
.col-pk { color: #fbbf24; font-weight: bold; }
.col-type { color: #a78bfa; }

/* Pagination */
.pagination { padding: 10px 20px; background: #1e293b; border-top: 1px solid #334155; display: flex; gap: 8px; align-items: center; justify-content: center; }
.pagination button { background: #334155; color: #e2e8f0; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }
.pagination button:hover { background: #475569; }
.pagination button.active { background: #0ea5e9; }
.pagination button:disabled { opacity: 0.4; cursor: default; }

/* Quick stats */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; padding: 20px; }
.stat-card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; }
.stat-card h4 { color: #64748b; font-size: 12px; text-transform: uppercase; margin-bottom: 4px; }
.stat-card .value { font-size: 28px; font-weight: 700; color: #38bdf8; }
.stat-card .sub { font-size: 12px; color: #64748b; margin-top: 4px; }

.error-msg { background: #7f1d1d; color: #fca5a5; padding: 12px 20px; margin: 10px 20px; border-radius: 6px; font-size: 13px; }
.loading { text-align: center; padding: 40px; color: #64748b; }
</style>
</head>
<body>
<div class="header">
  <h1>Storage-Location-3D-Display</h1>
  <span class="badge">DB Viewer</span>
  <span class="badge" style="background:#1e3a5f;color:#38bdf8;">SQLite (Mirrored from Oracle)</span>
  <a href="/structure" style="margin-left:auto;color:#38bdf8;text-decoration:none;font-size:13px;padding:6px 14px;background:#164e63;border-radius:6px;">📦 구조 조회 →</a>
</div>
<div class="container">
  <div class="sidebar">
    <h3>Tables</h3>
    <div id="tableList"></div>
    <h3 style="margin-top:16px;">Quick Queries</h3>
    <div class="table-item" onclick="runQuickQuery('SELECT * FROM ZONMA ORDER BY WAREKY, ZONEKY LIMIT 100')">
      <span class="name" style="font-size:12px;">ZONMA - All</span>
    </div>
    <div class="table-item" onclick="runQuickQuery('SELECT * FROM LOCMA ORDER BY WAREKY, LOCAKY LIMIT 100')">
      <span class="name" style="font-size:12px;">LOCMA - All</span>
    </div>
    <div class="table-item" onclick="runQuickQuery('SELECT * FROM STKKA ORDER BY ROWID LIMIT 100')">
      <span class="name" style="font-size:12px;">STKKA - All</span>
    </div>
    <div class="table-item" onclick="runQuickQuery('SELECT WAREKY, COUNT(*) as CNT FROM ZONMA GROUP BY WAREKY ORDER BY WAREKY')">
      <span class="name" style="font-size:12px;">ZONMA - Count by WAREKY</span>
    </div>
    <div class="table-item" onclick="runQuickQuery('SELECT ZONEKY, COUNT(*) as CNT FROM LOCMA GROUP BY ZONEKY ORDER BY CNT DESC LIMIT 20')">
      <span class="name" style="font-size:12px;">LOCMA - Top Zones</span>
    </div>
    <div class="table-item" onclick="runQuickQuery('SELECT WAREKY, LOCAKY, SKUKEY, QTSIWH, OWNRKY, DESC01 FROM STKKA WHERE QTSIWH > 0 ORDER BY QTSIWH DESC LIMIT 50')">
      <span class="name" style="font-size:12px;">STKKA - Top Stock Qty</span>
    </div>
    <div class="table-item" onclick="runQuickQuery('SELECT s.LOCAKY, s.SKUKEY, s.QTSIWH, s.DESC01, l.ZONEKY, l.SHORTX FROM STKKA s LEFT JOIN LOCMA l ON s.WAREKY=l.WAREKY AND s.LOCAKY=l.LOCAKY LIMIT 50')">
      <span class="name" style="font-size:12px;">STKKA + LOCMA JOIN</span>
    </div>
  </div>
  <div class="main">
    <div class="toolbar">
      <input class="sql-input" id="sqlInput" placeholder="SELECT * FROM ZONMA LIMIT 100" 
             onkeydown="if(event.key==='Enter')executeQuery()">
      <button class="btn btn-primary" onclick="executeQuery()">Execute (Enter)</button>
      <button class="btn btn-secondary" onclick="showDashboard()">Dashboard</button>
    </div>
    <div id="resultArea" class="results">
      <div class="loading">Select a table or enter a SQL query to begin.</div>
    </div>
  </div>
</div>

<script>
let currentPage = 0;
let pageSize = 100;
let lastQuery = '';

async function loadTables() {
  const resp = await fetch('/api/tables');
  const data = await resp.json();
  const list = document.getElementById('tableList');
  list.innerHTML = '';
  data.tables.forEach(t => {
    const div = document.createElement('div');
    div.className = 'table-item';
    div.innerHTML = `<div><div class="name">${t.name}</div><div class="info">${t.columns} columns</div></div><span class="count">${t.count.toLocaleString()} rows</span>`;
    div.onclick = () => showSchema(t.name);
    list.appendChild(div);
  });
}

async function showSchema(tableName) {
  document.querySelectorAll('.table-item').forEach(i => i.classList.remove('active'));
  event.currentTarget.classList.add('active');
  const resp = await fetch(`/api/schema/${tableName}`);
  const data = await resp.json();
  let html = `<div class="schema-table"><h3>${tableName} (${data.count.toLocaleString()} rows, ${data.columns.length} columns)</h3>`;
  html += `<div class="col-row header-row"><span>#</span><span>Column</span><span>Type</span><span>Nullable</span><span>Comment</span></div>`;
  data.columns.forEach((col, i) => {
    const pkMark = col.pk ? '<span class="col-pk">PK</span>' : '';
    html += `<div class="col-row"><span>${i+1}</span><span>${col.name} ${pkMark}</span><span class="col-type">${col.type}</span><span>${col.notnull ? 'NOT NULL' : 'NULL OK'}</span><span style="color:#64748b">${col.comment||''}</span></div>`;
  });
  html += `</div>`;
  html += `<div style="padding:12px 20px;"><button class="btn btn-primary" onclick="runQuickQuery('SELECT * FROM ${tableName} LIMIT 100')">View Data (Top 100)</button></div>`;
  document.getElementById('resultArea').innerHTML = html;
}

async function executeQuery() {
  const sql = document.getElementById('sqlInput').value.trim();
  if (!sql) return;
  lastQuery = sql;
  currentPage = 0;
  await runQuery(sql, 0);
}

function runQuickQuery(sql) {
  document.getElementById('sqlInput').value = sql;
  lastQuery = sql;
  currentPage = 0;
  runQuery(sql, 0);
}

async function runQuery(sql, page) {
  document.getElementById('resultArea').innerHTML = '<div class="loading">Executing query...</div>';
  try {
    const resp = await fetch('/api/query', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({sql, page, page_size: pageSize})
    });
    const data = await resp.json();
    if (data.error) {
      document.getElementById('resultArea').innerHTML = `<div class="error-msg">${data.error}</div>`;
      return;
    }
    renderResults(data);
  } catch(e) {
    document.getElementById('resultArea').innerHTML = `<div class="error-msg">${e.message}</div>`;
  }
}

function renderResults(data) {
  let html = `<div class="result-info"><span>${data.total_rows.toLocaleString()} rows returned | ${data.execution_time}ms</span><span>Page ${data.page+1} / ${Math.max(1,Math.ceil(data.total_rows/pageSize))}</span></div>`;
  if (data.columns.length === 0) {
    html += '<div class="loading">No results.</div>';
    document.getElementById('resultArea').innerHTML = html;
    return;
  }
  html += '<table><thead><tr>';
  html += '<th>#</th>';
  data.columns.forEach(c => { html += `<th title="${c}">${c}</th>`; });
  html += '</tr></thead><tbody>';
  data.rows.forEach((row, idx) => {
    html += '<tr>';
    html += `<td style="color:#64748b">${data.page * pageSize + idx + 1}</td>`;
    row.forEach(val => {
      if (val === null) {
        html += '<td class="null">NULL</td>';
      } else {
        const s = String(val);
        const display = s.length > 60 ? s.substring(0,57)+'...' : s;
        html += `<td title="${s.replace(/"/g,'&quot;')}">${display}</td>`;
      }
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  
  // Pagination
  const totalPages = Math.ceil(data.total_rows / pageSize);
  if (totalPages > 1) {
    html += '<div class="pagination">';
    html += `<button ${data.page===0?'disabled':''} onclick="goPage(0)">&laquo;</button>`;
    html += `<button ${data.page===0?'disabled':''} onclick="goPage(${data.page-1})">&lsaquo; Prev</button>`;
    html += `<span style="color:#64748b;font-size:12px;">${data.page+1} / ${totalPages}</span>`;
    html += `<button ${data.page>=totalPages-1?'disabled':''} onclick="goPage(${data.page+1})">Next &rsaquo;</button>`;
    html += `<button ${data.page>=totalPages-1?'disabled':''} onclick="goPage(${totalPages-1})">&raquo;</button>`;
    html += '</div>';
  }
  document.getElementById('resultArea').innerHTML = html;
}

function goPage(p) {
  currentPage = p;
  runQuery(lastQuery, p);
}

async function showDashboard() {
  const resp = await fetch('/api/dashboard');
  const data = await resp.json();
  let html = '<div class="stats-grid">';
  data.stats.forEach(s => {
    html += `<div class="stat-card"><h4>${s.label}</h4><div class="value">${s.value}</div><div class="sub">${s.sub||''}</div></div>`;
  });
  html += '</div>';
  document.getElementById('resultArea').innerHTML = html;
}

loadTables();
showDashboard();
</script>
</body>
</html>
"""

# Column comments mapping
COMMENTS = {
    'ZONMA': {'WAREKY':'거점','ZONEKY':'구역','ZONETY':'타입','SHORTX':'명칭','AREAKY':'영역',
              'CREDAT':'생성일','CRETIM':'생성시간','CREUSR':'생성자','LMODAT':'수정일','LMOTIM':'수정시간',
              'LMOUSR':'수정자','INDBZL':'지시정보','INDARC':'활서정보','UPDCHK':'갱신체크','PLNTKY':'플랜트','STLKY':'저장위치'},
    'LOCMA': {'WAREKY':'거점','LOCAKY':'지번','LOCATY':'지번유형','SHORTX':'지번명','TASKTY':'작업타입',
              'ZONEKY':'구역','AREAKY':'영역','TKZONE':'작업구역','FACLTY':'동/층','ARLVLL':'창고레벨',
              'INDCPC':'Capa체크','INDTUT':'팔렛타입체크','IBROUT':'입고순서','OBROUT':'출고순서','RPROUT':'보충순서',
              'STATUS':'상태','ABCANV':'ABC','LENGTH':'길이','WIDTHW':'가로','HEIGHT':'높이',
              'CUBICM':'CBM','MAXCPC':'팔렛Capa.','MAXQTY':'최대수량','MAXWGT':'최대중량','MAXLDR':'Max ratio',
              'MAXSEC':'최대섹션수','MIXSKU':'제품혼적','MIXLOT':'Lot.혼적','RPNCAT':'보충유형','INDQTC':'수량체크구분',
              'QTYCHK':'수량체크','NEDSID':'섹션아이디','INDUPA':'적치가능','INDUPK':'피킹가능','AUTLOC':'자동창고여부',
              'CREDAT':'생성일','CRETIM':'생성시간','CREUSR':'생성자','LMODAT':'수정일','LMOTIM':'수정시간',
              'LMOUSR':'수정자','INDBZL':'비지니스로직','INDARC':'아카이브구분자','UPDCHK':'수정체크'},
    'STKKA': {'STOKKY':'재고키','WAREKY':'거점','LOTNUM':'물류롯트넘버','LOCAKY':'지번','TRNUID':'Pallet ID',
              'SECTID':'Sect.ID','PACKID':'박스ID','QTSIWH':'수량','QTSALO':'할당수량','QTSPMO':'이동수량(OUT)',
              'QTSPMI':'이동수량(IN)','QTSBLK':'보류수량','QTYUOM':'Cross수량','TRUNTY':'팔렛타입','MEASKY':'품목코드',
              'UOMKEY':'단위','QTPUOM':'분자','DUOMKY':'단위','QTDUOM':'입수','TKFLKY':'작업흐름키',
              'STEPNO':'단계번호','LSTTFL':'최종스텝','SRCSKY':'Src.재고','UOMDOC':'참조문서단위','CNTBSK':'브런치재고수',
              'NUPDPS':'Not update to parent stock key','REFDKY':'참조문서','REFDIT':'참조문서It.','REFCAT':'참조문서유형',
              'REFDAT':'참조일자','PURCKY':'구매오더','PURCIT':'구매It.','ASNDKY':'ASN문서번호','ASNDIT':'ASN Item',
              'RECVKY':'입고키','RECVIT':'입고순서','SHPOKY':'출고문서번호','SHPOIT':'출고문서아이템','GRPOKY':'그룹오더',
              'GRPOIT':'그룹오더순서','TASKKY':'작업지시번호','TASKIT':'작업지시순서','SADJKY':'조정문서번호','SADJIT':'조정문서순서',
              'SDIFKY':'Diff.No.','SDIFIT':'Diff.It.','PHYIKY':'재고실사번호','PHYIIT':'재고실사순번','OWNRKY':'화주',
              'SKUKEY':'품목코드','LOTA01':'저장위치','LOTA02':'플랜트','LOTA03':'포장타입','LOTA04':'호기',
              'LOTA05':'LOTA05','LOTA06':'상태값','LOTA07':'MTO판매번호','LOTA08':'국가코드','LOTA09':'MTO판매처코드',
              'LOTA10':'보류사유명','LOTA11':'제조일자','LOTA12':'입고일자','LOTA13':'유통기한','LOTA14':'개별바코드',
              'LOTA15':'배치번호','LOTA16':'평량','LOTA17':'컨테이너유형','LOTA18':'LOTA18','LOTA19':'LOTA19',
              'LOTA20':'LOTA20','AWMSNO':'SEQ(MP)','DESC01':'품목명칭','DESC02':'규격','ASKU01':'ERP품번코드',
              'ASKU02':'브랜드','ASKU03':'제조상','ASKU04':'유통기한일','ASKU05':'Image등록유무','EANCOD':'88바코드',
              'GTINCD':'바코드','SKUG01':'품목유형','SKUG02':'즉시불출여부','SKUG03':'품목유형3','SKUG04':'상품구분',
              'SKUG05':'제품군','GRSWGT':'총중량','NETWGT':'KIT순중량','WGTUNT':'중량단위','LENGTH':'길이',
              'WIDTHW':'가로','HEIGHT':'높이','CUBICM':'CBM','CAPACT':'CAPA','ZONEKY':'구역',
              'TKZONE':'작업구역','AREAKY':'영역','SMANDT':'Client','SEBELN':'오더번호','SEBELP':'오더번호순서',
              'SZMBLNO':'B/L NO','SZMIPNO':'B/L Item NO','STRAID':'SCM주문번호','SVBELN':'출고오더번호','SPOSNR':'출고오더순번',
              'STKNUM':'선적번호','STPNUM':'토탈피킹선적','SWERKS':'출발지','SLGORT':'영업부문','SDATBG':'출하계획일시',
              'STDLNR':'작업장','SSORNU':'반품출하문서번호','SSORIT':'반품출하문서아이템','SMBLNR':'Mat.Doc.','SZEILE':'Mat.Doc.',
              'SMJAHR':'M/D년도','SXBLNR':'인터페이스번호','SAPSTS':'ERP Mvt','SBKTXT':'Text',
              'CREDAT':'생성일','CRETIM':'생성시간','CREUSR':'생성자','LMODAT':'수정일','LMOTIM':'수정시간',
              'LMOUSR':'수정자','INDBZL':'비지니스로직','INDARC':'아카이브구분자','UPDCHK':'수정체크','KEEPTS':'SMS'}
}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tables')
def api_tables():
    conn = get_db()
    tables = []
    for name in ['ZONMA', 'LOCMA', 'STKKA']:
        count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        tables.append({'name': name, 'count': count, 'columns': len(cols)})
    conn.close()
    return jsonify({'tables': tables})

@app.route('/api/schema/<table_name>')
def api_schema(table_name):
    if table_name not in ['ZONMA', 'LOCMA', 'STKKA']:
        return jsonify({'error': 'Invalid table name'}), 400
    conn = get_db()
    cols_raw = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    conn.close()
    comments_map = COMMENTS.get(table_name, {})
    columns = []
    for col in cols_raw:
        columns.append({
            'name': col['name'],
            'type': col['type'],
            'notnull': bool(col['notnull']),
            'pk': bool(col['pk']),
            'comment': comments_map.get(col['name'], '')
        })
    return jsonify({'table': table_name, 'count': count, 'columns': columns})

@app.route('/api/query', methods=['POST'])
def api_query():
    data = request.json
    sql = data.get('sql', '').strip()
    page = data.get('page', 0)
    page_size = min(data.get('page_size', 100), 500)
    
    if not sql:
        return jsonify({'error': 'Empty query'})
    
    # Basic safety checks (read-only)
    sql_upper = sql.upper().strip()
    if any(sql_upper.startswith(kw) for kw in ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']):
        return jsonify({'error': 'Only SELECT queries are allowed in this viewer.'})
    
    conn = get_db()
    import time
    start = time.time()
    try:
        # Get total count by wrapping query
        try:
            count_sql = f"SELECT COUNT(*) FROM ({sql})"
            total = conn.execute(count_sql).fetchone()[0]
        except:
            total = -1
        
        # Execute with pagination
        paginated_sql = f"{sql} LIMIT {page_size} OFFSET {page * page_size}"
        cursor = conn.execute(paginated_sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [list(row) for row in cursor.fetchall()]
        elapsed = round((time.time() - start) * 1000, 1)
        
        if total == -1:
            total = len(rows)
        
        conn.close()
        return jsonify({
            'columns': columns,
            'rows': rows,
            'total_rows': total,
            'page': page,
            'page_size': page_size,
            'execution_time': elapsed
        })
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)})

@app.route('/api/dashboard')
def api_dashboard():
    conn = get_db()
    stats = []
    
    # Table counts
    for name in ['ZONMA', 'LOCMA', 'STKKA']:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        label_map = {'ZONMA': 'ZONMA (Zone Master)', 'LOCMA': 'LOCMA (Location Master)', 'STKKA': 'STKKA (Stock)'}
        stats.append({'label': label_map[name], 'value': f'{cnt:,}', 'sub': f'{len(cols)} columns'})
    
    # Total records
    total = sum(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ['ZONMA','LOCMA','STKKA'])
    stats.append({'label': 'Total Records', 'value': f'{total:,}', 'sub': '3 tables'})
    
    # Distinct WAREKY
    wk = conn.execute("SELECT COUNT(DISTINCT WAREKY) FROM ZONMA").fetchone()[0]
    stats.append({'label': 'Distinct WAREKY (ZONMA)', 'value': str(wk), 'sub': 'Unique warehouse keys'})
    
    # Distinct Zones in LOCMA
    zn = conn.execute("SELECT COUNT(DISTINCT ZONEKY) FROM LOCMA").fetchone()[0]
    stats.append({'label': 'Distinct Zones (LOCMA)', 'value': str(zn), 'sub': 'Unique zone keys'})
    
    # Stock with quantity > 0
    sq = conn.execute("SELECT COUNT(*) FROM STKKA WHERE QTSIWH > 0").fetchone()[0]
    stats.append({'label': 'Active Stock (QTSIWH > 0)', 'value': f'{sq:,}', 'sub': 'STKKA records with stock'})
    
    # Distinct SKUs
    sk = conn.execute("SELECT COUNT(DISTINCT SKUKEY) FROM STKKA WHERE SKUKEY IS NOT NULL AND SKUKEY != ' '").fetchone()[0]
    stats.append({'label': 'Distinct SKUs (STKKA)', 'value': f'{sk:,}', 'sub': 'Unique product codes'})
    
    conn.close()
    return jsonify({'stats': stats})

###############################################################################
# Storage Location Structure API
###############################################################################

@app.route('/api/hierarchy/tree')
def api_hierarchy_tree():
    """Return the full hierarchy tree: 거점 > 플랜트 > 저장위치 > 영역 > 구역 > 지번"""
    conn = get_db()
    cur = conn.cursor()

    # ZONMA: WAREKY > PLNTKY > STLKY > AREAKY > ZONEKY mapping
    cur.execute("SELECT DISTINCT WAREKY, PLNTKY, STLKY, AREAKY, ZONEKY, SHORTX FROM ZONMA")
    zone_map = {}
    zone_names = {}
    for row in cur.fetchall():
        wareky, plntky, stlky, areaky, zoneky, shortx = row['WAREKY'], row['PLNTKY'], row['STLKY'], row['AREAKY'], row['ZONEKY'], row['SHORTX']
        plntky = (plntky or '').strip() or None
        stlky = (stlky or '').strip() or None
        zone_map[(wareky, areaky, zoneky)] = (plntky, stlky)
        zone_names[(wareky, zoneky)] = shortx

    # LOCMA: WAREKY + AREAKY + ZONEKY > LOCAKY
    cur.execute("SELECT DISTINCT WAREKY, AREAKY, ZONEKY, LOCAKY FROM LOCMA")
    locma_rows = cur.fetchall()

    # STKKA: WAREKY + LOTA02 + LOTA01 + AREAKY + ZONEKY + LOCAKY
    cur.execute("SELECT DISTINCT WAREKY, LOTA02, LOTA01, AREAKY, ZONEKY, LOCAKY FROM STKKA")
    stkka_rows = cur.fetchall()

    conn.close()

    # Build tree
    from collections import OrderedDict
    tree = {}

    for row in locma_rows:
        wareky, areaky, zoneky, locaky = row['WAREKY'], row['AREAKY'], row['ZONEKY'], row['LOCAKY']
        key = (wareky, areaky, zoneky)
        plntky, stlky = zone_map.get(key, (None, None))
        p = plntky or '(미지정)'
        s = stlky or '(미지정)'
        tree.setdefault(wareky, {}).setdefault(p, {}).setdefault(s, {}).setdefault(areaky, {}).setdefault(zoneky, set()).add(locaky)

    for row in stkka_rows:
        wareky = row['WAREKY']
        lota02 = (row['LOTA02'] or '').strip() or '(미지정)'
        lota01 = (row['LOTA01'] or '').strip() or '(미지정)'
        areaky, zoneky, locaky = row['AREAKY'], row['ZONEKY'], row['LOCAKY']
        tree.setdefault(wareky, {}).setdefault(lota02, {}).setdefault(lota01, {}).setdefault(areaky, {}).setdefault(zoneky, set()).add(locaky)

    # Convert to JSON-serializable format
    result = []
    for wareky in sorted(tree.keys()):
        ware_node = {'id': f'W{wareky}', 'label': str(wareky), 'type': 'warehouse', 'children': [], 'count': 0}
        for plntky in sorted(tree[wareky].keys()):
            plnt_node = {'id': f'W{wareky}_P{plntky}', 'label': plntky, 'type': 'plant', 'children': [], 'count': 0}
            for stlky in sorted(tree[wareky][plntky].keys()):
                stl_node = {'id': f'W{wareky}_P{plntky}_S{stlky}', 'label': stlky, 'type': 'storage', 'children': [], 'count': 0}
                for areaky in sorted(tree[wareky][plntky][stlky].keys()):
                    area_node = {'id': f'W{wareky}_P{plntky}_S{stlky}_A{areaky}', 'label': areaky, 'type': 'area', 'children': [], 'count': 0}
                    for zoneky in sorted(tree[wareky][plntky][stlky][areaky].keys()):
                        locs = sorted(tree[wareky][plntky][stlky][areaky][zoneky])
                        loc_count = len(locs)
                        zone_label = zoneky
                        name = zone_names.get((wareky, zoneky), '')
                        if name and name.strip():
                            zone_label = f"{zoneky} ({name.strip()})"
                        zone_node = {
                            'id': f'W{wareky}_P{plntky}_S{stlky}_A{areaky}_Z{zoneky}',
                            'label': zone_label,
                            'type': 'zone',
                            'locations': locs[:200],
                            'count': loc_count,
                            'truncated': loc_count > 200
                        }
                        area_node['children'].append(zone_node)
                        area_node['count'] += loc_count
                    stl_node['children'].append(area_node)
                    stl_node['count'] += area_node['count']
                plnt_node['children'].append(stl_node)
                plnt_node['count'] += stl_node['count']
            ware_node['children'].append(plnt_node)
            ware_node['count'] += plnt_node['count']
        result.append(ware_node)

    return jsonify({'tree': result})


@app.route('/api/hierarchy/locations')
def api_hierarchy_locations():
    """Return locations for a specific zone"""
    wareky = request.args.get('wareky')
    zoneky = request.args.get('zoneky')
    areaky = request.args.get('areaky')

    if not wareky or not zoneky:
        return jsonify({'error': 'wareky and zoneky required'}), 400

    conn = get_db()
    if areaky:
        rows = conn.execute(
            "SELECT DISTINCT LOCAKY FROM LOCMA WHERE WAREKY=? AND AREAKY=? AND ZONEKY=? ORDER BY LOCAKY",
            (wareky, areaky, zoneky)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT DISTINCT LOCAKY FROM LOCMA WHERE WAREKY=? AND ZONEKY=? ORDER BY LOCAKY",
            (wareky, zoneky)
        ).fetchall()

    locations = [r['LOCAKY'] for r in rows]
    conn.close()
    return jsonify({'locations': locations, 'count': len(locations)})


@app.route('/api/hierarchy/summary')
def api_hierarchy_summary():
    """Return summary statistics for the hierarchy"""
    conn = get_db()
    cur = conn.cursor()

    summary = {}
    summary['total_wareky'] = cur.execute("SELECT COUNT(DISTINCT WAREKY) FROM ZONMA").fetchone()[0]
    summary['total_zones_zonma'] = cur.execute("SELECT COUNT(*) FROM ZONMA").fetchone()[0]
    summary['total_locations'] = cur.execute("SELECT COUNT(*) FROM LOCMA").fetchone()[0]
    summary['total_stock'] = cur.execute("SELECT COUNT(*) FROM STKKA").fetchone()[0]
    summary['distinct_plants'] = cur.execute("SELECT COUNT(DISTINCT PLNTKY) FROM ZONMA WHERE TRIM(PLNTKY) != ''").fetchone()[0]
    summary['distinct_stlky'] = cur.execute("SELECT COUNT(DISTINCT STLKY) FROM ZONMA WHERE TRIM(STLKY) != ''").fetchone()[0]
    summary['distinct_areaky'] = cur.execute("SELECT COUNT(DISTINCT AREAKY) FROM LOCMA").fetchone()[0]
    summary['distinct_zoneky'] = cur.execute("SELECT COUNT(DISTINCT ZONEKY) FROM LOCMA").fetchone()[0]

    # Per warehouse stats
    ware_stats = []
    ware_rows = cur.execute("""
        SELECT z.WAREKY,
               COUNT(DISTINCT z.PLNTKY) as plants,
               COUNT(DISTINCT z.STLKY) as storages,
               COUNT(DISTINCT z.AREAKY) as areas,
               COUNT(DISTINCT z.ZONEKY) as zones
        FROM ZONMA z
        GROUP BY z.WAREKY
        ORDER BY z.WAREKY
    """).fetchall()
    for wr in ware_rows:
        loc_count = cur.execute("SELECT COUNT(DISTINCT LOCAKY) FROM LOCMA WHERE WAREKY=?", (wr['WAREKY'],)).fetchone()[0]
        stock_count = cur.execute("SELECT COUNT(*) FROM STKKA WHERE WAREKY=?", (wr['WAREKY'],)).fetchone()[0]
        ware_stats.append({
            'wareky': wr['WAREKY'],
            'plants': wr['plants'],
            'storages': wr['storages'],
            'areas': wr['areas'],
            'zones': wr['zones'],
            'locations': loc_count,
            'stocks': stock_count
        })
    summary['warehouse_stats'] = ware_stats
    conn.close()
    return jsonify(summary)


@app.route('/api/hierarchy/stock')
def api_hierarchy_stock():
    """Return aggregated stock quantities for children of a given hierarchy node.
    Parameters: level (warehouse|plant|storage|area|zone), wareky, plntky, stlky, areaky, zoneky
    """
    level = request.args.get('level', 'warehouse')
    wareky = request.args.get('wareky')
    plntky = request.args.get('plntky')
    stlky = request.args.get('stlky')
    areaky = request.args.get('areaky')
    zoneky = request.args.get('zoneky')

    conn = get_db()
    cur = conn.cursor()
    result = []

    if level == 'warehouse':
        # Show pallet qty (SUM(QTSIWH)/20) and MAXCPC per warehouse
        rows = cur.execute("""
            SELECT s.WAREKY as label,
                   CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as pallet_qty,
                   COUNT(*) as cnt,
                   COUNT(DISTINCT s.LOCAKY) as locs, COUNT(DISTINCT s.ZONEKY) as zones,
                   (SELECT COALESCE(SUM(l.MAXCPC), 0) FROM LOCMA l
                    WHERE l.WAREKY = s.WAREKY AND l.MAXCPC < 9999999
                   ) as maxcpc
            FROM STKKA s WHERE s.QTSIWH > 0 GROUP BY s.WAREKY ORDER BY s.WAREKY
        """).fetchall()
        for r in rows:
            capa = r['maxcpc'] or 0
            pq = r['pallet_qty'] or 0
            usage = round(pq * 100.0 / capa, 1) if capa > 0 else 0
            result.append({'label': str(r['label']), 'qty': pq, 'cnt': r['cnt'], 'locs': r['locs'], 'zones': r['zones'], 'maxcpc': capa, 'usage': usage})

    elif level == 'plant' and wareky:
        # Show pallet qty per plant for a warehouse
        rows = cur.execute("""
            SELECT s.LOTA02 as label,
                   CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as pallet_qty,
                   COUNT(*) as cnt,
                   COUNT(DISTINCT s.LOCAKY) as locs, COUNT(DISTINCT s.ZONEKY) as zones
            FROM STKKA s WHERE s.WAREKY=? AND s.QTSIWH > 0 GROUP BY s.LOTA02 ORDER BY s.LOTA02
        """, (wareky,)).fetchall()
        for r in rows:
            lbl = (r['label'] or '').strip() or '(미지정)'
            pq = r['pallet_qty'] or 0
            # Get MAXCPC sum for this plant's locations (DISTINCT to avoid duplication from multiple STKKA rows per location)
            capa_row = cur.execute("""
                SELECT COALESCE(SUM(capa), 0) as capa FROM (
                    SELECT DISTINCT l.LOCAKY, l.MAXCPC as capa FROM LOCMA l
                    INNER JOIN STKKA s ON l.WAREKY = s.WAREKY AND l.LOCAKY = s.LOCAKY
                    WHERE s.WAREKY=? AND s.LOTA02=? AND l.MAXCPC < 9999999
                )
            """, (wareky, r['label'] or '')).fetchone()
            capa = capa_row['capa'] if capa_row else 0
            usage = round(pq * 100.0 / capa, 1) if capa > 0 else 0
            result.append({'label': lbl, 'qty': pq, 'cnt': r['cnt'], 'locs': r['locs'], 'zones': r['zones'], 'maxcpc': capa, 'usage': usage})

    elif level == 'storage' and wareky and plntky:
        # Show pallet qty per storage location
        p_cond = "TRIM(s.LOTA02)=''" if plntky == '(미지정)' else f"s.LOTA02='{plntky}'"
        rows = cur.execute(f"""
            SELECT s.LOTA01 as label,
                   CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as pallet_qty,
                   COUNT(*) as cnt,
                   COUNT(DISTINCT s.LOCAKY) as locs, COUNT(DISTINCT s.ZONEKY) as zones
            FROM STKKA s WHERE s.WAREKY=? AND {p_cond} AND s.QTSIWH > 0 GROUP BY s.LOTA01 ORDER BY s.LOTA01
        """, (wareky,)).fetchall()
        for r in rows:
            lbl = (r['label'] or '').strip() or '(미지정)'
            pq = r['pallet_qty'] or 0
            capa_row = cur.execute(f"""
                SELECT COALESCE(SUM(capa), 0) as capa FROM (
                    SELECT DISTINCT l.LOCAKY, l.MAXCPC as capa FROM LOCMA l
                    INNER JOIN STKKA s ON l.WAREKY = s.WAREKY AND l.LOCAKY = s.LOCAKY
                    WHERE s.WAREKY=? AND {p_cond} AND s.LOTA01=? AND l.MAXCPC < 9999999
                )
            """, (wareky, r['label'] or '')).fetchone()
            capa = capa_row['capa'] if capa_row else 0
            usage = round(pq * 100.0 / capa, 1) if capa > 0 else 0
            result.append({'label': lbl, 'qty': pq, 'cnt': r['cnt'], 'locs': r['locs'], 'zones': r['zones'], 'maxcpc': capa, 'usage': usage})

    elif level == 'area' and wareky:
        # Show pallet qty per area
        conditions = ["s.WAREKY=?", "s.QTSIWH > 0"]
        params = [wareky]
        if plntky and plntky != '(미지정)':
            conditions.append("s.LOTA02=?")
            params.append(plntky)
        if stlky and stlky != '(미지정)':
            conditions.append("s.LOTA01=?")
            params.append(stlky)
        where = " AND ".join(conditions)
        rows = cur.execute(f"""
            SELECT s.AREAKY as label,
                   CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as pallet_qty,
                   COUNT(*) as cnt,
                   COUNT(DISTINCT s.LOCAKY) as locs, COUNT(DISTINCT s.ZONEKY) as zones
            FROM STKKA s WHERE {where} GROUP BY s.AREAKY ORDER BY s.AREAKY
        """, params).fetchall()
        for r in rows:
            pq = r['pallet_qty'] or 0
            capa_row = cur.execute("""
                SELECT COALESCE(SUM(l.MAXCPC), 0) as capa FROM LOCMA l
                WHERE l.WAREKY=? AND l.AREAKY=? AND l.MAXCPC < 9999999
            """, (wareky, r['label'])).fetchone()
            capa = capa_row['capa'] if capa_row else 0
            usage = round(pq * 100.0 / capa, 1) if capa > 0 else 0
            result.append({'label': r['label'], 'qty': pq, 'cnt': r['cnt'], 'locs': r['locs'], 'zones': r['zones'], 'maxcpc': capa, 'usage': usage})

    elif level == 'zone' and wareky and areaky:
        # Show pallet qty per zone
        conditions = ["s.WAREKY=?", "s.AREAKY=?", "s.QTSIWH > 0"]
        params = [wareky, areaky]
        where = " AND ".join(conditions)
        rows = cur.execute(f"""
            SELECT s.ZONEKY as label,
                   CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as pallet_qty,
                   COUNT(*) as cnt,
                   COUNT(DISTINCT s.LOCAKY) as locs
            FROM STKKA s WHERE {where} GROUP BY s.ZONEKY ORDER BY s.ZONEKY
        """, params).fetchall()
        for r in rows:
            pq = r['pallet_qty'] or 0
            capa_row = cur.execute("""
                SELECT COALESCE(SUM(l.MAXCPC), 0) as capa FROM LOCMA l
                WHERE l.WAREKY=? AND l.AREAKY=? AND l.ZONEKY=? AND l.MAXCPC < 9999999
            """, (wareky, areaky, r['label'])).fetchone()
            capa = capa_row['capa'] if capa_row else 0
            usage = round(pq * 100.0 / capa, 1) if capa > 0 else 0
            result.append({'label': r['label'], 'qty': pq, 'cnt': r['cnt'], 'locs': r['locs'], 'maxcpc': capa, 'usage': usage})

    elif level == 'location' and wareky and zoneky:
        # Show pallet qty per location within a zone
        conditions = ["s.WAREKY=?", "s.ZONEKY=?", "s.QTSIWH > 0"]
        params = [wareky, zoneky]
        if areaky:
            conditions.append("s.AREAKY=?")
            params.append(areaky)
        where = " AND ".join(conditions)
        rows = cur.execute(f"""
            SELECT s.LOCAKY as label,
                   CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as pallet_qty,
                   COUNT(*) as cnt,
                   GROUP_CONCAT(DISTINCT s.SKUKEY) as skus
            FROM STKKA s WHERE {where} GROUP BY s.LOCAKY ORDER BY s.LOCAKY
        """, params).fetchall()
        for r in rows:
            skus = (r['skus'] or '').split(',')[:5]
            pq = r['pallet_qty'] or 0
            capa_row = cur.execute("""
                SELECT COALESCE(l.MAXCPC, 0) as capa FROM LOCMA l
                WHERE l.WAREKY=? AND l.LOCAKY=? AND l.MAXCPC < 9999999
            """, (wareky, r['label'])).fetchone()
            capa = capa_row['capa'] if capa_row else 0
            usage = round(pq * 100.0 / capa, 1) if capa > 0 else 0
            result.append({'label': r['label'], 'qty': pq, 'cnt': r['cnt'], 'skus': skus, 'maxcpc': capa, 'usage': usage})

    conn.close()

    # Calculate max for scaling
    max_qty = max((r['qty'] for r in result), default=0)
    total_qty = sum(r['qty'] for r in result)
    return jsonify({'items': result, 'max_qty': max_qty, 'total_qty': total_qty, 'level': level})








@app.route('/structure')
def structure_page():
    return render_template_string(STRUCTURE_HTML)


STRUCTURE_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>저장 위치 구조 조회 | 적재율 히트맵</title>
<style>
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --border: #334155;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent: #38bdf8;
  --accent-dark: #0ea5e9;
  --green: #4ade80;
  --yellow: #fbbf24;
  --purple: #a78bfa;
  --pink: #f472b6;
  --orange: #fb923c;
  --red: #f87171;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', -apple-system, 'Malgun Gothic', sans-serif; background: var(--bg-primary); color: var(--text-primary); }

/* Header */
.header {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  padding: 14px 24px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 16px;
}
.header h1 { font-size: 18px; color: var(--accent); font-weight: 600; }
.header .badge { font-size: 11px; padding: 3px 10px; border-radius: 4px; }
.header .b1 { background: #164e63; color: #67e8f9; }
.header .b2 { background: #1e3a5f; color: #38bdf8; }
.header a { color: var(--text-secondary); text-decoration: none; font-size: 13px; margin-left: auto; }
.header a:hover { color: var(--accent); }

/* Layout */
.layout { display: flex; height: calc(100vh - 52px); }

/* Left panel - tree */
.tree-panel {
  width: 420px; min-width: 320px; max-width: 600px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  overflow: hidden;
}
.tree-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 8px;
}
.tree-toolbar h3 { font-size: 13px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
.search-box {
  width: 100%; padding: 8px 12px;
  background: var(--bg-primary); border: 1px solid var(--border);
  color: var(--text-primary); border-radius: 6px; font-size: 13px; outline: none;
}
.search-box:focus { border-color: var(--accent); }
.search-box::placeholder { color: var(--text-muted); }
.tree-actions { display: flex; gap: 6px; }
.tree-actions button {
  flex: 1; padding: 6px 10px; font-size: 11px;
  background: var(--bg-tertiary); color: var(--text-secondary);
  border: none; border-radius: 4px; cursor: pointer;
}
.tree-actions button:hover { background: #475569; color: var(--text-primary); }
.tree-container {
  flex: 1; overflow-y: auto; padding: 8px 0;
}
.tree-container::-webkit-scrollbar { width: 6px; }
.tree-container::-webkit-scrollbar-track { background: transparent; }
.tree-container::-webkit-scrollbar-thumb { background: var(--bg-tertiary); border-radius: 3px; }

/* Tree nodes */
.tree-node { user-select: none; }
.tree-row {
  display: flex; align-items: center; gap: 4px;
  padding: 5px 8px 5px 0; cursor: pointer;
  border-left: 3px solid transparent;
  transition: background 0.1s;
  white-space: nowrap;
}
.tree-row:hover { background: rgba(56,189,248,0.06); }
.tree-row.selected { background: rgba(56,189,248,0.12); border-left-color: var(--accent); }
.tree-toggle {
  width: 20px; height: 20px; display: flex; align-items: center; justify-content: center;
  font-size: 10px; color: var(--text-muted); flex-shrink: 0; transition: transform 0.15s;
}
.tree-toggle.open { transform: rotate(90deg); }
.tree-toggle.leaf { visibility: hidden; }
.tree-icon { font-size: 15px; flex-shrink: 0; width: 22px; text-align: center; }
.tree-label { font-size: 13px; flex: 1; overflow: hidden; text-overflow: ellipsis; }
.tree-count {
  font-size: 10px; padding: 1px 6px; border-radius: 8px;
  background: var(--bg-tertiary); color: var(--text-muted); flex-shrink: 0;
}
.tree-children { display: none; }
.tree-children.open { display: block; }

/* Type-specific colors */
.type-warehouse .tree-label { color: var(--yellow); font-weight: 600; }
.type-plant .tree-label { color: var(--green); font-weight: 500; }
.type-storage .tree-label { color: var(--purple); }
.type-area .tree-label { color: var(--orange); }
.type-zone .tree-label { color: var(--accent); }
.type-location .tree-label { color: var(--text-secondary); font-size: 12px; }

/* Right panel */
.detail-panel { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

/* Summary cards */
.summary-bar {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}
.s-card {
  background: var(--bg-primary); border: 1px solid var(--border);
  border-radius: 8px; padding: 10px 14px; text-align: center;
}
.s-card .s-val { font-size: 22px; font-weight: 700; color: var(--accent); }
.s-card .s-lbl { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* Breadcrumb */
.breadcrumb {
  padding: 14px 28px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  font-size: 18px; color: var(--text-muted);
  display: flex; align-items: center; gap: 9px; flex-wrap: wrap;
}
.breadcrumb span { cursor: pointer; color: var(--text-secondary); }
.breadcrumb span:hover { color: var(--accent); }
.breadcrumb .sep { color: var(--text-muted); font-size: 20px; }
.breadcrumb .current { color: var(--accent); font-weight: 600; }

/* Detail content */
.detail-content {
  flex: 1; overflow-y: auto; padding: 20px;
}

/* Detail table */
.detail-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--text-primary); }
.detail-subtitle { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  position: sticky; top: 0; background: var(--bg-secondary); color: var(--text-secondary);
  font-weight: 600; text-align: left; padding: 8px 12px;
  border-bottom: 2px solid var(--border); font-size: 11px; text-transform: uppercase;
}
.data-table td {
  padding: 7px 12px; border-bottom: 1px solid rgba(51,65,85,0.5);
}
.data-table tr:hover td { background: rgba(56,189,248,0.04); }
.data-table .clickable { cursor: pointer; color: var(--accent); }
.data-table .clickable:hover { text-decoration: underline; }

/* Location grid */
.loc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 6px; margin-top: 12px;
}
.loc-chip {
  padding: 6px 10px; background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: 6px; font-size: 12px; text-align: center;
  font-family: 'Consolas', monospace; color: var(--text-secondary);
  cursor: default; transition: all 0.15s;
}
.loc-chip:hover { border-color: var(--accent); color: var(--accent); }

/* View tabs */
.view-tabs {
  display: flex; border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
}
.view-tab {
  padding: 8px 20px; font-size: 13px; cursor: pointer;
  color: var(--text-muted); border-bottom: 2px solid transparent;
  transition: all 0.15s; background: none; border-top: none; border-left: none; border-right: none;
}
.view-tab:hover { color: var(--text-primary); background: rgba(56,189,248,0.05); }
.view-tab.active { color: var(--accent); border-bottom-color: var(--accent); }

/* Heatmap container */
.heatmap-container {
  position: relative; flex: 1; overflow: auto; background: var(--bg-primary);
  display: flex; flex-direction: column;
}
.heatmap-header {
  display: flex; align-items: center; gap: 16px; padding: 12px 20px;
  border-bottom: 1px solid var(--border); background: var(--bg-secondary); flex-shrink: 0; flex-wrap: wrap;
}
.heatmap-header .hm-title { font-size: 14px; font-weight: 600; color: var(--accent); }
.heatmap-header .hm-stat { font-size: 12px; color: var(--text-muted); }
.heatmap-header .hm-stat b { color: var(--text-primary); font-weight: 700; }
.heatmap-header .hm-sort { display: flex; align-items: center; gap: 6px; margin-left: auto; }
.heatmap-header .hm-sort label { font-size: 11px; color: var(--text-muted); }
.heatmap-header .hm-sort select {
  background: var(--bg-tertiary); border: 1px solid var(--border); color: var(--text-primary);
  padding: 4px 8px; border-radius: 4px; font-size: 11px; outline: none;
}

.heatmap-grid-wrap { flex: 1; overflow: auto; padding: 16px; }
.heatmap-grid { display: flex; flex-wrap: wrap; gap: 5px; align-content: flex-start; }

.hm-cell {
  border-radius: 6px; cursor: pointer; position: relative;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transition: transform 0.12s, box-shadow 0.12s;
  border: 1px solid rgba(255,255,255,0.06);
  overflow: hidden;
}
.hm-cell:hover { transform: scale(1.08); z-index: 2; box-shadow: 0 0 14px rgba(56,189,248,0.4); border-color: var(--accent); }
.hm-cell .hm-lbl {
  font-weight: 600; text-shadow: 0 1px 3px rgba(0,0,0,0.7);
  text-align: center; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; width: 100%; padding: 0 3px;
}
.hm-cell .hm-pct { font-weight: 800; text-shadow: 0 1px 3px rgba(0,0,0,0.7); }
.hm-cell .hm-sub { opacity: 0.85; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }

/* Heatmap legend */
.hm-legend {
  display: flex; align-items: center; gap: 12px; padding: 10px 20px;
  border-top: 1px solid var(--border); flex-shrink: 0;
  background: var(--bg-secondary); flex-wrap: wrap;
}
.hm-legend .leg-title { font-size: 11px; color: var(--text-muted); font-weight: 600; }
.hm-legend .leg-bar {
  width: 200px; height: 12px; border-radius: 6px;
  background: linear-gradient(90deg, #22c55e, #4ade80, #a3e635, #facc15, #fb923c, #f87171, #dc2626);
}
.hm-legend .leg-labels { display: flex; justify-content: space-between; width: 200px; font-size: 10px; color: var(--text-muted); margin-top: 1px; }
.hm-legend .leg-items { display: flex; gap: 10px; font-size: 11px; }
.hm-legend .leg-items span { display: flex; align-items: center; gap: 4px; }
.hm-legend .leg-items .dot { width: 10px; height: 10px; border-radius: 2px; }

/* Tooltip */
.hm-tooltip {
  position: fixed; display: none; background: rgba(15,23,42,0.96); border: 1px solid var(--accent);
  border-radius: 8px; padding: 12px 16px; pointer-events: none; z-index: 1000;
  min-width: 220px; backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
.hm-tooltip .tt-name { color: var(--accent); font-weight: 700; font-size: 14px; margin-bottom: 6px; }
.hm-tooltip .tt-pct { font-size: 28px; font-weight: 900; margin: 4px 0; }
.hm-tooltip .tt-row { display: flex; justify-content: space-between; font-size: 12px; padding: 2px 0; gap: 16px; }
.hm-tooltip .tt-row .k { color: var(--text-muted); }
.hm-tooltip .tt-row .v { color: var(--text-primary); font-weight: 600; }
.hm-tooltip .tt-status { font-size: 11px; margin-top: 6px; padding: 3px 8px; border-radius: 4px; display: inline-block; font-weight: 600; }

/* Welcome */
.welcome { text-align: center; padding: 60px 40px; }
.welcome h2 { font-size: 24px; color: var(--text-primary); margin-bottom: 12px; }
.welcome p { color: var(--text-muted); font-size: 14px; line-height: 1.8; }
.welcome .hierarchy-demo { margin-top: 24px; display: inline-block; text-align: left; font-size: 14px; color: var(--text-secondary); line-height: 2; }

/* Resize handle */
.resize-handle {
  width: 4px; cursor: col-resize; background: transparent; flex-shrink: 0;
  transition: background 0.2s;
}
.resize-handle:hover, .resize-handle.active { background: var(--accent); }

/* Loading */
.loading-spinner {
  text-align: center; padding: 40px; color: var(--text-muted);
}

/* Highlight matches */
.match-highlight { background: rgba(56,189,248,0.25); border-radius: 2px; padding: 0 1px; }

@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .tree-panel { width: 100% !important; max-width: 100%; height: 50vh; }
  .resize-handle { display: none; }
}
</style>
</head>
<body>

<div class="header">
  <h1>저장 위치 구조 조회</h1>
  <span class="badge b1">Storage Location Structure</span>
  <span class="badge b2">거점 > 플랜트 > 저장위치 > 영역 > 구역 > 지번</span>
  <a href="/" style="margin-left:auto;">← DB Viewer</a>
</div>

<div class="layout">
  <!-- Tree panel -->
  <div class="tree-panel" id="treePanel">
    <div class="tree-toolbar">
      <h3>구조 탐색</h3>
      <input type="text" class="search-box" id="searchInput"
             placeholder="검색 (거점, 영역, 구역, 지번...)" oninput="onSearch(this.value)">
      <div class="tree-actions">
        <button onclick="expandAll()">전체 펼치기</button>
        <button onclick="collapseAll()">전체 접기</button>
        <button onclick="expandLevel(1)">거점만</button>
        <button onclick="expandLevel(2)">플랜트까지</button>
      </div>
    </div>
    <div class="tree-container" id="treeContainer">
      <div class="loading-spinner">데이터 로딩 중...</div>
    </div>
  </div>

  <!-- Resize handle -->
  <div class="resize-handle" id="resizeHandle"></div>

  <!-- Detail panel -->
  <div class="detail-panel">
    <div class="summary-bar" id="summaryBar">
      <div class="summary-cards" id="summaryCards"></div>
    </div>
    <div class="breadcrumb" id="breadcrumb">
      <span class="current">전체 구조</span>
    </div>
    <div class="view-tabs" id="viewTabs" style="display:none;">
      <button class="view-tab active" data-view="heatmap" onclick="switchView('heatmap')">🟩 적재율 히트맵</button>
      <button class="view-tab" data-view="table" onclick="switchView('table')">📋 테이블 보기</button>
    </div>
    <!-- Heatmap view -->
    <div class="heatmap-container" id="heatmapContainer" style="display:none;">
      <div class="heatmap-header">
        <span class="hm-title" id="hmTitle">적재율 현황</span>
        <span class="hm-stat">현재고: <b id="hmQty">-</b> PLT</span>
        <span class="hm-stat">CAPA: <b id="hmCapa">-</b> PLT</span>
        <span class="hm-stat">적재율: <b id="hmUsage">-</b></span>
        <span class="hm-stat">항목: <b id="hmCount">-</b></span>
        <div class="hm-sort">
          <label>정렬:</label>
          <select id="hmSortBy" onchange="resortHeatmap()">
            <option value="usage_desc">적재율 높은순</option>
            <option value="usage_asc">적재율 낮은순</option>
            <option value="label_asc">이름순</option>
            <option value="qty_desc">재고량 높은순</option>
          </select>
        </div>
      </div>
      <div class="heatmap-grid-wrap">
        <div class="heatmap-grid" id="heatmapGrid"></div>
      </div>
      <div class="hm-legend">
        <span class="leg-title">적재율:</span>
        <div>
          <div class="leg-bar"></div>
          <div class="leg-labels"><span>0%</span><span>60%</span><span>100%</span><span>120%+</span></div>
        </div>
        <div class="leg-items">
          <span><span class="dot" style="background:#22c55e"></span>여유(~40%)</span>
          <span><span class="dot" style="background:#a3e635"></span>양호(~60%)</span>
          <span><span class="dot" style="background:#facc15"></span>주의(~80%)</span>
          <span><span class="dot" style="background:#fb923c"></span>포화임박(~100%)</span>
          <span><span class="dot" style="background:#ef4444"></span>초과(100%+)</span>
        </div>
      </div>
    </div>
    <!-- Table / Welcome view -->
    <div class="detail-content" id="detailContent">
      <div class="welcome" id="welcomeView">
        <h2>저장 위치 구조 조회 + CAPA 대비 현재고</h2>
        <p>왼쪽 트리에서 항목을 클릭하면 하위 저장위치별 <b style="color:var(--yellow)">CAPA 대비 현재고 수준</b>을 색상으로 구별하여 볼 수 있습니다.</p>
        <div style="margin:12px 0;padding:10px 14px;background:var(--bg-tertiary);border-radius:8px;font-size:13px;line-height:1.7;">
          <b style="color:var(--accent)">계산 기준:</b><br>
          &nbsp;&nbsp;📦 <b>현재고(PLT)</b> = LOCAKY별 SUM(STKKA.QTSIWH) / 20<br>
          &nbsp;&nbsp;📏 <b>CAPA(PLT)</b> = LOCAKY별 LOCMA.MAXCPC 합계<br>
          &nbsp;&nbsp;📊 <b>적재율</b> = 현재고 / CAPA * 100%<br>
          <div style="margin-top:6px;">
            <span style="color:#22c55e">■ 0~40% 여유</span>&nbsp;
            <span style="color:#a3e635">■ 40~60% 양호</span>&nbsp;
            <span style="color:#facc15">■ 60~80% 주의</span>&nbsp;
            <span style="color:#fb923c">■ 80~100% 포화임박</span>&nbsp;
            <span style="color:#f87171">■ 100%+ 초과</span>
          </div>
        </div>
        <div class="hierarchy-demo">
          📦 <b style="color:var(--yellow)">거점 (WAREKY)</b> - 물류 센터<br>
          &nbsp;&nbsp;🏭 <b style="color:var(--green)">플랜트 (PLNTKY)</b> - 생산/물류 단위<br>
          &nbsp;&nbsp;&nbsp;&nbsp;📍 <b style="color:var(--purple)">저장위치 (STLKY)</b> - 저장 공간 구분<br>
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🔲 <b style="color:var(--orange)">영역 (AREAKY)</b> - 물리적 영역<br>
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏷️ <b style="color:var(--accent)">구역 (ZONEKY)</b> - 세부 구역<br>
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;📋 <b style="color:var(--text-secondary)">지번 (LOCAKY)</b> - 최종 적치 위치
        </div>
        <p style="margin-top:20px;color:var(--accent);">트리에서 항목 클릭 → 적재율 색상 히트맵 표시, 사각형 호버 → 상세정보, 사각형 클릭 → 하위이동</p>
      </div>
    </div>
  </div>
</div>

<!-- Tooltip (fixed position, outside grid) -->
<div class="hm-tooltip" id="hmTooltip">
  <div class="tt-name" id="ttName"></div>
  <div class="tt-pct" id="ttPct"></div>
  <div class="tt-row"><span class="k">현재고</span><span class="v" id="ttQty"></span></div>
  <div class="tt-row"><span class="k">CAPA</span><span class="v" id="ttCapa"></span></div>
  <div class="tt-row"><span class="k">재고건수</span><span class="v" id="ttCnt"></span></div>
  <div class="tt-row"><span class="k">지번수</span><span class="v" id="ttLocs"></span></div>
  <div class="tt-status" id="ttStatus"></div>
</div>

<script>
// ========================
// State
// ========================
let treeData = [];
let selectedNodeId = null;
let searchTerm = '';
let currentView = 'heatmap';
let lastHeatmapItems = [];
let lastHeatmapTotalQty = 0;
let lastHeatmapLevel = '';

const ICONS = {
  warehouse: '📦', plant: '🏭', storage: '📍',
  area: '🔲', zone: '🏷️', location: '📋'
};
const TYPE_LABELS = {
  warehouse: '거점', plant: '플랜트', storage: '저장위치',
  area: '영역', zone: '구역', location: '지번'
};
const CHILD_LEVEL = {
  warehouse: 'plant', plant: 'storage', storage: 'area', area: 'zone', zone: 'location'
};

// ========================
// Color functions
// ========================
function usageColor(u) {
  if (u <= 0) return '#334155';
  if (u <= 40) return '#22c55e';
  if (u <= 60) return '#84cc16';
  if (u <= 70) return '#a3e635';
  if (u <= 80) return '#facc15';
  if (u <= 90) return '#f59e0b';
  if (u <= 100) return '#fb923c';
  if (u <= 120) return '#f87171';
  return '#dc2626';
}
function usageTextColor(u) {
  if (u <= 0) return '#64748b';
  if (u <= 70) return '#0f172a';
  return '#fff';
}
function usageStatus(u) {
  if (u <= 0) return { text:'재고없음', bg:'#334155', color:'#94a3b8' };
  if (u <= 40) return { text:'여유', bg:'rgba(34,197,94,0.2)', color:'#4ade80' };
  if (u <= 60) return { text:'양호', bg:'rgba(163,230,53,0.2)', color:'#a3e635' };
  if (u <= 80) return { text:'주의', bg:'rgba(250,204,21,0.2)', color:'#facc15' };
  if (u <= 100) return { text:'포화 임박', bg:'rgba(251,146,60,0.2)', color:'#fb923c' };
  return { text:'CAPA 초과', bg:'rgba(248,113,113,0.2)', color:'#f87171' };
}
function formatNumber(n) {
  if (n == null) return '-';
  if (n >= 1e8) return (n / 1e8).toFixed(1) + '억';
  if (n >= 1e4) return (n / 1e4).toFixed(1) + '만';
  if (n >= 1000) return n.toLocaleString();
  return String(Math.round(n * 100) / 100);
}

// ========================
// Data Loading
// ========================
async function loadTree() {
  try {
    const resp = await fetch('/api/hierarchy/tree');
    const data = await resp.json();
    treeData = data.tree;
    renderTree();
    loadSummary();
  } catch(e) {
    document.getElementById('treeContainer').innerHTML =
      `<div style="padding:20px;color:var(--red);">로딩 실패: ${e.message}</div>`;
  }
}

async function loadSummary() {
  try {
    const resp = await fetch('/api/hierarchy/summary');
    const data = await resp.json();
    renderSummary(data);
  } catch(e) { console.error(e); }
}

// ========================
// Tree Rendering
// ========================
function renderTree() {
  const container = document.getElementById('treeContainer');
  container.innerHTML = '';
  treeData.forEach(node => {
    container.appendChild(buildTreeNode(node, 0));
  });
}

function buildTreeNode(node, depth) {
  const div = document.createElement('div');
  div.className = 'tree-node';
  div.dataset.id = node.id;
  div.dataset.type = node.type;

  const hasChildren = (node.children && node.children.length > 0) ||
                      (node.type === 'zone' && node.locations && node.locations.length > 0);

  const row = document.createElement('div');
  row.className = `tree-row type-${node.type}`;
  row.style.paddingLeft = (depth * 18 + 8) + 'px';

  const toggle = document.createElement('span');
  toggle.className = 'tree-toggle' + (hasChildren ? '' : ' leaf');
  toggle.innerHTML = '▶';

  const icon = document.createElement('span');
  icon.className = 'tree-icon';
  icon.textContent = ICONS[node.type] || '📄';

  const label = document.createElement('span');
  label.className = 'tree-label';
  label.textContent = node.label;

  const count = document.createElement('span');
  count.className = 'tree-count';
  if (node.type === 'zone') {
    count.textContent = node.count + '지번';
  } else if (node.count !== undefined) {
    count.textContent = node.count.toLocaleString();
  }

  row.appendChild(toggle);
  row.appendChild(icon);
  row.appendChild(label);
  if (node.count > 0) row.appendChild(count);
  div.appendChild(row);

  if (hasChildren) {
    const childDiv = document.createElement('div');
    childDiv.className = 'tree-children';

    if (node.children) {
      node.children.forEach(child => {
        childDiv.appendChild(buildTreeNode(child, depth + 1));
      });
    }
    if (node.type === 'zone' && node.locations) {
      node.locations.forEach(loc => {
        const locNode = document.createElement('div');
        locNode.className = 'tree-node';
        const locRow = document.createElement('div');
        locRow.className = 'tree-row type-location';
        locRow.style.paddingLeft = ((depth + 1) * 18 + 8) + 'px';
        const lt = document.createElement('span');
        lt.className = 'tree-toggle leaf';
        lt.innerHTML = '▶';
        const li = document.createElement('span');
        li.className = 'tree-icon';
        li.textContent = '📋';
        const ll = document.createElement('span');
        ll.className = 'tree-label';
        ll.textContent = loc;
        locRow.appendChild(lt);
        locRow.appendChild(li);
        locRow.appendChild(ll);
        locNode.appendChild(locRow);
        childDiv.appendChild(locNode);
      });
      if (node.truncated) {
        const more = document.createElement('div');
        more.style.cssText = `padding: 4px 8px 4px ${((depth+1)*18+30)}px; font-size:11px; color:var(--text-muted); font-style:italic;`;
        more.textContent = `... +${node.count - node.locations.length}개 더`;
        childDiv.appendChild(more);
      }
    }
    div.appendChild(childDiv);
  }

  row.addEventListener('click', (e) => {
    e.stopPropagation();
    const children = div.querySelector('.tree-children');
    if (children) {
      children.classList.toggle('open');
      toggle.classList.toggle('open');
    }
    document.querySelectorAll('.tree-row.selected').forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');
    selectedNodeId = node.id;
    showNodeDetail(node);
  });

  return div;
}

// ========================
// Summary
// ========================
function renderSummary(data) {
  const cards = document.getElementById('summaryCards');
  cards.innerHTML = `
    <div class="s-card"><div class="s-val">${data.total_wareky}</div><div class="s-lbl">거점</div></div>
    <div class="s-card"><div class="s-val">${data.distinct_plants}</div><div class="s-lbl">플랜트</div></div>
    <div class="s-card"><div class="s-val">${data.distinct_stlky}</div><div class="s-lbl">저장위치</div></div>
    <div class="s-card"><div class="s-val">${data.distinct_areaky}</div><div class="s-lbl">영역</div></div>
    <div class="s-card"><div class="s-val">${data.distinct_zoneky}</div><div class="s-lbl">구역</div></div>
    <div class="s-card"><div class="s-val">${data.total_locations.toLocaleString()}</div><div class="s-lbl">지번 (LOCMA)</div></div>
    <div class="s-card"><div class="s-val">${data.total_stock.toLocaleString()}</div><div class="s-lbl">재고 (STKKA)</div></div>
  `;
}

// ========================
// View switching
// ========================
function switchView(view) {
  currentView = view;
  document.querySelectorAll('.view-tab').forEach(t => t.classList.toggle('active', t.dataset.view === view));
  document.getElementById('heatmapContainer').style.display = view === 'heatmap' ? 'flex' : 'none';
  document.getElementById('detailContent').style.display = view === 'table' ? 'block' : 'none';
}

// ========================
// Detail View
// ========================
function showNodeDetail(node) {
  updateBreadcrumb(node);
  document.getElementById('viewTabs').style.display = 'flex';

  const content = document.getElementById('detailContent');
  if (node.type === 'zone') {
    showZoneDetail(node, content);
  } else {
    showGroupDetail(node, content);
  }

  loadHeatmapForNode(node);
  switchView(currentView);
}

function showGroupDetail(node, content) {
  const typeLabel = TYPE_LABELS[node.type];
  let html = `<div class="detail-title">${ICONS[node.type]} ${typeLabel}: ${node.label}</div>`;
  html += `<div class="detail-subtitle">하위 항목 ${node.children ? node.children.length : 0}개 | 총 지번 ${node.count.toLocaleString()}개</div>`;

  if (node.children && node.children.length > 0) {
    const childType = node.children[0].type;
    const childLabel = TYPE_LABELS[childType];

    html += `<table class="data-table"><thead><tr>`;
    html += `<th>#</th><th>${childLabel}</th><th>하위 수</th><th>지번수</th><th>팔레트재고</th><th>Capa</th><th>적재율</th><th>비율</th>`;
    html += `</tr></thead><tbody>`;

    node.children.forEach((child, i) => {
      const pct = node.count > 0 ? ((child.count / node.count) * 100).toFixed(1) : 0;
      const barW = Math.max(2, Math.min(200, (child.count / node.count) * 200));
      html += `<tr onclick="navigateToNode('${child.id}')" style="cursor:pointer">`;
      html += `<td style="color:var(--text-muted)">${i+1}</td>`;
      html += `<td class="clickable">${ICONS[childType]} ${child.label}</td>`;
      html += `<td>${child.children ? child.children.length : (child.locations ? child.locations.length : '-')}</td>`;
      html += `<td><b>${child.count.toLocaleString()}</b></td>`;
      html += `<td class="stock-qty" data-label="${child.label}">-</td>`;
      html += `<td class="stock-capa" data-label="${child.label}">-</td>`;
      html += `<td class="stock-usage" data-label="${child.label}">-</td>`;
      html += `<td><div style="display:flex;align-items:center;gap:8px;"><div style="width:${barW}px;height:6px;background:var(--accent);border-radius:3px;"></div><span style="font-size:11px;color:var(--text-muted)">${pct}%</span></div></td>`;
      html += `</tr>`;
    });
    html += `</tbody></table>`;
  }

  content.innerHTML = html;
}

function showZoneDetail(node, content) {
  let html = `<div class="detail-title">${ICONS.zone} 구역: ${node.label}</div>`;
  html += `<div class="detail-subtitle">지번 ${node.count.toLocaleString()}개</div>`;

  if (node.locations && node.locations.length > 0) {
    html += `<div class="loc-grid">`;
    node.locations.forEach(loc => {
      html += `<div class="loc-chip">${loc}</div>`;
    });
    html += `</div>`;
    if (node.truncated) {
      html += `<div style="margin-top:12px;color:var(--text-muted);font-size:12px;font-style:italic;">처음 200개만 표시됨. 전체 ${node.count}개 지번.</div>`;
    }
  }
  content.innerHTML = html;
}

// ========================
// Heatmap Builder
// ========================
function buildHeatmap(items, totalQty, levelName) {
  lastHeatmapItems = items;
  lastHeatmapTotalQty = totalQty;
  lastHeatmapLevel = levelName;

  const grid = document.getElementById('heatmapGrid');
  grid.innerHTML = '';

  if (!items || items.length === 0) {
    grid.innerHTML = '<div style="padding:40px;color:var(--text-muted);text-align:center;width:100%;">데이터 없음</div>';
    return;
  }

  // Sort
  const sortBy = document.getElementById('hmSortBy').value;
  const sorted = [...items];
  if (sortBy === 'usage_desc') sorted.sort((a,b) => (b.usage||0) - (a.usage||0));
  else if (sortBy === 'usage_asc') sorted.sort((a,b) => (a.usage||0) - (b.usage||0));
  else if (sortBy === 'label_asc') sorted.sort((a,b) => (a.label||'').localeCompare(b.label||''));
  else if (sortBy === 'qty_desc') sorted.sort((a,b) => (b.qty||0) - (a.qty||0));

  // Calculate cell size based on count
  const count = sorted.length;
  let cellW, cellH, fontSize, pctSize;
  if (count <= 8) { cellW=180; cellH=110; fontSize=14; pctSize=24; }
  else if (count <= 20) { cellW=145; cellH=90; fontSize=13; pctSize=21; }
  else if (count <= 50) { cellW=120; cellH=76; fontSize=12; pctSize=18; }
  else if (count <= 100) { cellW=100; cellH=64; fontSize=11; pctSize=16; }
  else if (count <= 200) { cellW=80; cellH=52; fontSize=10; pctSize=14; }
  else { cellW=62; cellH=42; fontSize=9; pctSize=12; }

  sorted.forEach(item => {
    const u = item.usage || 0;
    const bg = usageColor(u);
    const fg = usageTextColor(u);

    const cell = document.createElement('div');
    cell.className = 'hm-cell';
    cell.style.width = cellW + 'px';
    cell.style.height = cellH + 'px';
    cell.style.background = bg;
    cell.style.color = fg;

    const lbl = document.createElement('div');
    lbl.className = 'hm-lbl';
    lbl.style.fontSize = fontSize + 'px';
    lbl.textContent = item.label;

    const pct = document.createElement('div');
    pct.className = 'hm-pct';
    pct.style.fontSize = pctSize + 'px';
    pct.textContent = u > 0 ? Math.round(u) + '%' : '-';

    cell.appendChild(lbl);
    cell.appendChild(pct);

    // Extra info for larger cells
    if (cellH >= 76) {
      const sub = document.createElement('div');
      sub.className = 'hm-sub';
      sub.style.fontSize = (fontSize - 2) + 'px';
      sub.textContent = formatNumber(item.qty) + ' / ' + formatNumber(item.maxcpc) + ' PLT';
      cell.appendChild(sub);
    }

    // Click to navigate
    if (item.nodeId) {
      cell.addEventListener('click', () => navigateToNode(item.nodeId));
    }

    // Tooltip events
    cell.addEventListener('mouseenter', e => showTooltip(e, item));
    cell.addEventListener('mousemove', e => moveTooltip(e));
    cell.addEventListener('mouseleave', hideTooltip);

    grid.appendChild(cell);
  });

  // Update header stats
  const totalCapa = items.reduce((s, i) => s + (i.maxcpc || 0), 0);
  const totalUsage = totalCapa > 0 ? (totalQty * 100 / totalCapa).toFixed(1) : '0';
  document.getElementById('hmTitle').textContent = `${TYPE_LABELS[levelName] || levelName}별 적재율 현황`;
  document.getElementById('hmQty').textContent = formatNumber(totalQty);
  document.getElementById('hmCapa').textContent = formatNumber(totalCapa);
  const usageEl = document.getElementById('hmUsage');
  usageEl.textContent = totalUsage + '%';
  usageEl.style.color = totalUsage > 100 ? 'var(--red)' : totalUsage > 80 ? 'var(--orange)' : 'var(--green)';
  document.getElementById('hmCount').textContent = items.length + '개';
}

function resortHeatmap() {
  if (lastHeatmapItems.length > 0) {
    buildHeatmap(lastHeatmapItems, lastHeatmapTotalQty, lastHeatmapLevel);
  }
}

// ========================
// Tooltip
// ========================
function showTooltip(e, item) {
  const tt = document.getElementById('hmTooltip');
  const u = item.usage || 0;
  const st = usageStatus(u);
  document.getElementById('ttName').textContent = item.label;
  const pctEl = document.getElementById('ttPct');
  pctEl.textContent = u > 0 ? u.toFixed(1) + '%' : 'N/A';
  pctEl.style.color = usageColor(u === 0 ? 0.1 : u);
  document.getElementById('ttQty').textContent = formatNumber(item.qty) + ' PLT';
  document.getElementById('ttCapa').textContent = formatNumber(item.maxcpc) + ' PLT';
  document.getElementById('ttCnt').textContent = (item.cnt || '-').toLocaleString();
  document.getElementById('ttLocs').textContent = (item.locs || '-').toLocaleString();
  const stEl = document.getElementById('ttStatus');
  stEl.textContent = st.text;
  stEl.style.background = st.bg;
  stEl.style.color = st.color;
  tt.style.display = 'block';
  moveTooltip(e);
}
function moveTooltip(e) {
  const tt = document.getElementById('hmTooltip');
  let x = e.clientX + 16, y = e.clientY - 10;
  const bw = window.innerWidth, bh = window.innerHeight;
  if (x + 240 > bw) x = e.clientX - 240;
  if (y + 200 > bh) y = bh - 210;
  if (y < 0) y = 10;
  tt.style.left = x + 'px'; tt.style.top = y + 'px';
}
function hideTooltip() {
  document.getElementById('hmTooltip').style.display = 'none';
}

// ========================
// Heatmap Data Loading
// ========================
async function loadHeatmapForNode(node) {
  const id = node.id;
  const parts = parseNodeId(id);

  let params = {};
  let childLevel = '';

  if (node.type === 'warehouse') {
    params = { level: 'plant', wareky: parts.wareky };
    childLevel = 'plant';
  } else if (node.type === 'plant') {
    params = { level: 'storage', wareky: parts.wareky, plntky: parts.plntky };
    childLevel = 'storage';
  } else if (node.type === 'storage') {
    params = { level: 'area', wareky: parts.wareky, plntky: parts.plntky, stlky: parts.stlky };
    childLevel = 'area';
  } else if (node.type === 'area') {
    params = { level: 'zone', wareky: parts.wareky, areaky: parts.areaky };
    childLevel = 'zone';
  } else if (node.type === 'zone') {
    params = { level: 'location', wareky: parts.wareky, areaky: parts.areaky, zoneky: parts.zoneky };
    childLevel = 'location';
  }

  const qs = new URLSearchParams(params).toString();
  try {
    const resp = await fetch(`/api/hierarchy/stock?${qs}`);
    const data = await resp.json();

    // Map nodeIds for click navigation
    if (node.children) {
      data.items.forEach(item => {
        const child = node.children.find(c => c.label === item.label || c.label.startsWith(item.label + ' '));
        if (child) item.nodeId = child.id;
      });
    }

    document.getElementById('heatmapContainer').style.display = currentView === 'heatmap' ? 'flex' : 'none';
    buildHeatmap(data.items, data.total_qty, childLevel);

    // Update table view stock quantities, capa, and usage
    data.items.forEach(item => {
      const cells = document.querySelectorAll(`.stock-qty[data-label="${item.label}"]`);
      cells.forEach(cell => {
        cell.textContent = formatNumber(item.qty);
        cell.style.color = 'var(--yellow)';
        cell.style.fontWeight = '600';
      });
      const capaCells = document.querySelectorAll(`.stock-capa[data-label="${item.label}"]`);
      capaCells.forEach(cell => {
        cell.textContent = formatNumber(item.maxcpc || 0);
        cell.style.color = 'var(--green)';
      });
      const usageCells = document.querySelectorAll(`.stock-usage[data-label="${item.label}"]`);
      usageCells.forEach(cell => {
        const u = item.usage || 0;
        cell.textContent = u.toFixed(1) + '%';
        cell.style.fontWeight = '600';
        cell.style.color = u > 100 ? 'var(--red)' : u > 80 ? 'var(--orange)' : 'var(--green)';
      });
    });

  } catch(e) {
    console.error('Failed to load stock data:', e);
  }
}

function parseNodeId(id) {
  const result = {};
  const parts = id.split('_');
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    const prefix = p.charAt(0);
    const value = p.substring(1);
    switch(prefix) {
      case 'W': result.wareky = value; break;
      case 'P': result.plntky = value; break;
      case 'S': result.stlky = value; break;
      case 'A': result.areaky = value; break;
      case 'Z': result.zoneky = value; break;
    }
  }
  return result;
}

// ========================
// Breadcrumb
// ========================
function updateBreadcrumb(node) {
  const bc = document.getElementById('breadcrumb');
  const parts = node.id.split('_');
  let html = `<span onclick="showWelcome()">전체</span>`;

  let currentId = '';
  for (const part of parts) {
    if (currentId) currentId += '_';
    currentId += part;
    const foundNode = findNodeById(treeData, currentId);
    if (foundNode) {
      const isLast = currentId === node.id;
      if (isLast) {
        html += `<span class="sep">›</span><span class="current">${ICONS[foundNode.type]} ${foundNode.label}</span>`;
      } else {
        html += `<span class="sep">›</span><span onclick="navigateToNode('${currentId}')">${ICONS[foundNode.type]} ${foundNode.label}</span>`;
      }
    }
  }
  bc.innerHTML = html;
}

function findNodeById(nodes, id) {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.children) {
      const found = findNodeById(node.children, id);
      if (found) return found;
    }
  }
  return null;
}

function navigateToNode(id) {
  expandPathTo(id);
  const node = findNodeById(treeData, id);
  if (node) {
    document.querySelectorAll('.tree-row.selected').forEach(r => r.classList.remove('selected'));
    const treeNode = document.querySelector(`.tree-node[data-id="${id}"] > .tree-row`);
    if (treeNode) {
      treeNode.classList.add('selected');
      treeNode.scrollIntoView({behavior: 'smooth', block: 'center'});
    }
    selectedNodeId = id;
    showNodeDetail(node);
  }
}

function expandPathTo(id) {
  const parts = id.split('_');
  let currentId = '';
  for (let i = 0; i < parts.length; i++) {
    if (currentId) currentId += '_';
    currentId += parts[i];
    const treeNode = document.querySelector(`.tree-node[data-id="${currentId}"]`);
    if (treeNode) {
      const children = treeNode.querySelector(':scope > .tree-children');
      const toggle = treeNode.querySelector(':scope > .tree-row .tree-toggle');
      if (children && !children.classList.contains('open')) {
        children.classList.add('open');
        if (toggle) toggle.classList.add('open');
      }
    }
  }
}

function showWelcome() {
  document.querySelectorAll('.tree-row.selected').forEach(r => r.classList.remove('selected'));
  document.getElementById('breadcrumb').innerHTML = '<span class="current">전체 구조</span>';
  document.getElementById('viewTabs').style.display = 'none';
  document.getElementById('heatmapContainer').style.display = 'none';
  document.getElementById('detailContent').style.display = 'block';
  document.getElementById('detailContent').innerHTML = `
    <div class="welcome">
      <h2>저장 위치 구조 조회</h2>
      <p>왼쪽 트리에서 항목을 클릭하면 하위 저장위치별 적재율을 색상으로 구별하여 볼 수 있습니다.</p>
      <div class="hierarchy-demo">
        📦 <b style="color:var(--yellow)">거점 (WAREKY)</b> - 물류 센터<br>
        &nbsp;&nbsp;🏭 <b style="color:var(--green)">플랜트 (PLNTKY)</b> - 생산/물류 단위<br>
        &nbsp;&nbsp;&nbsp;&nbsp;📍 <b style="color:var(--purple)">저장위치 (STLKY)</b> - 저장 공간 구분<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🔲 <b style="color:var(--orange)">영역 (AREAKY)</b> - 물리적 영역<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🏷️ <b style="color:var(--accent)">구역 (ZONEKY)</b> - 세부 구역<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;📋 <b style="color:var(--text-secondary)">지번 (LOCAKY)</b> - 최종 적치 위치
      </div>
      <p style="margin-top:20px;color:var(--accent);">트리에서 항목 클릭 → 적재율 색상 히트맵 표시, 사각형 호버 → 상세정보, 사각형 클릭 → 하위이동</p>
    </div>`;
}

// ========================
// Search
// ========================
let searchTimeout;
function onSearch(term) {
  clearTimeout(searchTimeout);
  searchTerm = term.trim().toUpperCase();
  searchTimeout = setTimeout(() => {
    if (!searchTerm) {
      renderTree();
      return;
    }
    const container = document.getElementById('treeContainer');
    container.innerHTML = '';
    treeData.forEach(node => {
      const filtered = filterNode(node, searchTerm);
      if (filtered) {
        container.appendChild(buildFilteredTreeNode(filtered, 0, searchTerm));
      }
    });
  }, 250);
}

function filterNode(node, term) {
  const labelMatch = node.label.toUpperCase().includes(term);
  let matchedChildren = [];

  if (node.children) {
    node.children.forEach(child => {
      const filtered = filterNode(child, term);
      if (filtered) matchedChildren.push(filtered);
    });
  }

  let matchedLocations = [];
  if (node.type === 'zone' && node.locations) {
    matchedLocations = node.locations.filter(l => l.toUpperCase().includes(term));
  }

  if (labelMatch || matchedChildren.length > 0 || matchedLocations.length > 0) {
    return {
      ...node,
      children: matchedChildren.length > 0 ? matchedChildren : node.children,
      _matchedLocations: matchedLocations,
      _labelMatch: labelMatch
    };
  }
  return null;
}

function buildFilteredTreeNode(node, depth, term) {
  const div = document.createElement('div');
  div.className = 'tree-node';
  div.dataset.id = node.id;
  div.dataset.type = node.type;

  const hasChildren = (node.children && node.children.length > 0) ||
                      (node.type === 'zone' && node.locations && node.locations.length > 0);

  const row = document.createElement('div');
  row.className = `tree-row type-${node.type}`;
  row.style.paddingLeft = (depth * 18 + 8) + 'px';

  const toggle = document.createElement('span');
  toggle.className = 'tree-toggle open';
  toggle.innerHTML = '▶';

  const icon = document.createElement('span');
  icon.className = 'tree-icon';
  icon.textContent = ICONS[node.type] || '📄';

  const label = document.createElement('span');
  label.className = 'tree-label';
  if (node._labelMatch && term) {
    label.innerHTML = highlightText(node.label, term);
  } else {
    label.textContent = node.label;
  }

  const count = document.createElement('span');
  count.className = 'tree-count';
  count.textContent = node.type === 'zone' ? node.count + '지번' : node.count.toLocaleString();

  row.appendChild(toggle);
  row.appendChild(icon);
  row.appendChild(label);
  if (node.count > 0) row.appendChild(count);
  div.appendChild(row);

  if (hasChildren) {
    const childDiv = document.createElement('div');
    childDiv.className = 'tree-children open';

    if (node.children) {
      node.children.forEach(child => {
        const fChild = filterNode(child, term) || child;
        childDiv.appendChild(buildFilteredTreeNode(fChild, depth + 1, term));
      });
    }
    if (node.type === 'zone' && node._matchedLocations && node._matchedLocations.length > 0) {
      node._matchedLocations.forEach(loc => {
        const locNode = document.createElement('div');
        locNode.className = 'tree-node';
        const locRow = document.createElement('div');
        locRow.className = 'tree-row type-location';
        locRow.style.paddingLeft = ((depth + 1) * 18 + 8) + 'px';
        const lt = document.createElement('span');
        lt.className = 'tree-toggle leaf';
        lt.innerHTML = '▶';
        const li = document.createElement('span');
        li.className = 'tree-icon';
        li.textContent = '📋';
        const ll = document.createElement('span');
        ll.className = 'tree-label';
        ll.innerHTML = highlightText(loc, term);
        locRow.appendChild(lt); locRow.appendChild(li); locRow.appendChild(ll);
        locNode.appendChild(locRow);
        childDiv.appendChild(locNode);
      });
    }
    div.appendChild(childDiv);
  }

  row.addEventListener('click', (e) => {
    e.stopPropagation();
    const children = div.querySelector('.tree-children');
    if (children) {
      children.classList.toggle('open');
      toggle.classList.toggle('open');
    }
    document.querySelectorAll('.tree-row.selected').forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');
    selectedNodeId = node.id;
    showNodeDetail(node);
  });

  return div;
}

function highlightText(text, term) {
  const idx = text.toUpperCase().indexOf(term);
  if (idx === -1) return text;
  return text.substring(0, idx) +
    '<span class="match-highlight">' + text.substring(idx, idx + term.length) + '</span>' +
    text.substring(idx + term.length);
}

// ========================
// Expand / Collapse
// ========================
function expandAll() {
  document.querySelectorAll('.tree-children').forEach(c => c.classList.add('open'));
  document.querySelectorAll('.tree-toggle').forEach(t => { if (!t.classList.contains('leaf')) t.classList.add('open'); });
}

function collapseAll() {
  document.querySelectorAll('.tree-children').forEach(c => c.classList.remove('open'));
  document.querySelectorAll('.tree-toggle').forEach(t => t.classList.remove('open'));
}

function expandLevel(level) {
  collapseAll();
  const typeOrder = ['warehouse', 'plant', 'storage', 'area', 'zone'];
  document.querySelectorAll('.tree-node').forEach(n => {
    const type = n.dataset.type;
    const typeIdx = typeOrder.indexOf(type);
    if (typeIdx >= 0 && typeIdx < level) {
      const children = n.querySelector(':scope > .tree-children');
      const toggle = n.querySelector(':scope > .tree-row .tree-toggle');
      if (children) children.classList.add('open');
      if (toggle) toggle.classList.add('open');
    }
  });
}

// ========================
// Resize Handle
// ========================
(function() {
  const handle = document.getElementById('resizeHandle');
  const panel = document.getElementById('treePanel');
  let startX, startW;

  handle.addEventListener('mousedown', (e) => {
    startX = e.clientX;
    startW = panel.offsetWidth;
    handle.classList.add('active');
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', onStop);
    e.preventDefault();
  });

  function onDrag(e) {
    const w = startW + (e.clientX - startX);
    panel.style.width = Math.max(280, Math.min(800, w)) + 'px';
  }

  function onStop() {
    handle.classList.remove('active');
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', onStop);
  }
})();

// ========================
// Init
// ========================
loadTree();
</script>
</body>
</html>
"""


if __name__ == '__main__':
    print(f"DB path: {DB_PATH}")
    print(f"Starting DB Viewer on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
