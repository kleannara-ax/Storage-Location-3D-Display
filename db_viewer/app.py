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

# 플랜트 코드 → 이름 매핑
PLANT_NAMES = {
    'P100': '제지',
    'P200': '화장지',
    'P300': '패드',
    'P400': '물류',
    'P500': '음성',
}

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
body { font-family: 'Segoe UI', -apple-system, sans-serif; background: #080d1a; color: #edf0f7; }
.header { background: linear-gradient(135deg, #0a1128 0%, #121d3a 50%, #162550 100%); padding: 16px 24px; border-bottom: 1px solid rgba(110,168,254,0.1); display: flex; align-items: center; gap: 16px; box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03); }
.header h1 { font-size: 18px; background: linear-gradient(135deg, #6ea8fe, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; letter-spacing: 0.5px; }
.header .badge { background: rgba(110,168,254,0.12); color: #6ea8fe; font-size: 11px; padding: 4px 12px; border-radius: 6px; border: 1px solid rgba(110,168,254,0.2); backdrop-filter: blur(8px); }
.container { display: flex; height: calc(100vh - 56px); background: linear-gradient(180deg, #080d1a, #060a14); }

/* Sidebar */
.sidebar { width: 280px; background: linear-gradient(180deg, #0e1529, #0b1020); border-right: 1px solid rgba(110,168,254,0.1); overflow-y: auto; flex-shrink: 0; }
.sidebar h3 { padding: 16px 16px 8px; font-size: 11px; text-transform: uppercase; color: #5a6d8e; letter-spacing: 1.5px; font-weight: 700; }
.table-item { padding: 10px 16px; cursor: pointer; border-left: 3px solid transparent; transition: all 0.2s; display: flex; justify-content: space-between; align-items: center; }
.table-item:hover { background: rgba(110,168,254,0.06); }
.table-item.active { background: linear-gradient(90deg, rgba(110,168,254,0.15), rgba(110,168,254,0.05)); border-left-color: #6ea8fe; }
.table-item .name { font-size: 14px; font-weight: 500; }
.table-item .info { font-size: 11px; color: #5a6d8e; }
.table-item .count { font-size: 11px; background: rgba(110,168,254,0.06); padding: 3px 10px; border-radius: 10px; color: #a0b0d0; border: 1px solid rgba(110,168,254,0.1); }

/* Main */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.toolbar { padding: 12px 20px; background: linear-gradient(135deg, rgba(14,21,41,0.95), rgba(10,17,40,0.9)); border-bottom: 1px solid rgba(110,168,254,0.1); display: flex; gap: 12px; align-items: center; flex-wrap: wrap; backdrop-filter: blur(8px); }
.sql-input { flex: 1; min-width: 300px; background: rgba(8,13,26,0.6); border: 1px solid rgba(110,168,254,0.12); color: #edf0f7; padding: 9px 14px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
.sql-input:focus { border-color: #6ea8fe; box-shadow: 0 0 0 3px rgba(110,168,254,0.12); }
.btn { padding: 8px 20px; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; border: none; transition: all 0.2s; }
.btn-primary { background: linear-gradient(135deg, #6ea8fe, #4a8af0); color: white; box-shadow: 0 2px 12px rgba(110,168,254,0.25); }
.btn-primary:hover { background: linear-gradient(135deg, #5b9cf7, #3d7de3); box-shadow: 0 4px 16px rgba(110,168,254,0.35); }
.btn-secondary { background: rgba(110,168,254,0.06); color: #a0b0d0; border: 1px solid rgba(110,168,254,0.1); }
.btn-secondary:hover { background: rgba(110,168,254,0.15); color: #edf0f7; border-color: rgba(110,168,254,0.25); }

/* Results */
.results { flex: 1; overflow: auto; padding: 0; }
.result-info { padding: 8px 20px; background: rgba(14,21,41,0.8); font-size: 12px; color: #5a6d8e; border-bottom: 1px solid rgba(110,168,254,0.1); display: flex; justify-content: space-between; backdrop-filter: blur(8px); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { position: sticky; top: 0; background: #141d35; color: #a0b0d0; font-weight: 600; text-align: left; padding: 10px 12px; border-bottom: 2px solid rgba(110,168,254,0.12); white-space: nowrap; font-size: 12px; text-transform: uppercase; z-index:1; }
td { padding: 8px 12px; border-bottom: 1px solid rgba(110,168,254,0.05); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
tr:hover td { background: rgba(110,168,254,0.06); }
tr:nth-child(even) td { background: rgba(14,21,41,0.4); }
tr:nth-child(even):hover td { background: rgba(110,168,254,0.06); }
td.null { color: #5a6d8e; font-style: italic; }

/* Schema view */
.schema-table { margin: 20px; }
.schema-table h3 { background: linear-gradient(90deg, #6ea8fe, #b197fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; font-size: 16px; font-weight: 700; }
.col-row { display: grid; grid-template-columns: 30px 180px 120px 80px 1fr; gap: 8px; padding: 6px 12px; font-size: 13px; border-bottom: 1px solid rgba(110,168,254,0.05); }
.col-row.header-row { color: #5a6d8e; font-weight: 600; text-transform: uppercase; font-size: 11px; border-bottom: 2px solid rgba(110,168,254,0.12); }
.col-pk { color: #fcd34d; font-weight: bold; }
.col-type { color: #b197fc; }

/* Pagination */
.pagination { padding: 10px 20px; background: rgba(14,21,41,0.8); border-top: 1px solid rgba(110,168,254,0.1); display: flex; gap: 8px; align-items: center; justify-content: center; backdrop-filter: blur(8px); }
.pagination button { background: rgba(110,168,254,0.06); color: #a0b0d0; border: 1px solid rgba(110,168,254,0.1); padding: 6px 14px; border-radius: 8px; cursor: pointer; font-size: 12px; transition: all 0.2s; }
.pagination button:hover { background: rgba(110,168,254,0.15); border-color: rgba(110,168,254,0.25); }
.pagination button.active { background: linear-gradient(135deg, #6ea8fe, #4a8af0); color: white; border-color: #6ea8fe; box-shadow: 0 2px 10px rgba(110,168,254,0.25); }
.pagination button:disabled { opacity: 0.3; cursor: default; }

/* Quick stats */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; padding: 20px; }
.stat-card { background: rgba(110,168,254,0.04); border: 1px solid rgba(110,168,254,0.1); border-radius: 12px; padding: 18px 22px; transition: all 0.2s; }
.stat-card:hover { background: rgba(110,168,254,0.08); border-color: rgba(110,168,254,0.2); box-shadow: 0 4px 20px rgba(110,168,254,0.08); }
.stat-card h4 { color: #5a6d8e; font-size: 12px; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px; }
.stat-card .value { font-size: 28px; font-weight: 700; background: linear-gradient(135deg, #6ea8fe, #93c5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-card .sub { font-size: 12px; color: #5a6d8e; margin-top: 4px; }

.error-msg { background: rgba(252,165,165,0.08); color: #fca5a5; border: 1px solid rgba(252,165,165,0.15); padding: 12px 20px; margin: 10px 20px; border-radius: 10px; font-size: 13px; }
.loading { text-align: center; padding: 40px; color: #5a6d8e; }
</style>
</head>
<body>
<div class="header">
  <h1>Storage-Location-3D-Display</h1>
  <span class="badge">DB Viewer</span>
  <span class="badge" style="background:rgba(160,176,208,0.08);color:#a0b0d0;border:1px solid rgba(160,176,208,0.1);">SQLite (Mirrored from Oracle)</span>
  <div style="margin-left:auto;display:flex;gap:8px;">
    <a href="/structure" style="color:#a0b0d0;text-decoration:none;font-size:13px;padding:6px 16px;background:rgba(110,168,254,0.08);border:1px solid rgba(110,168,254,0.12);border-radius:8px;transition:all 0.2s;">📦 구조 조회</a>
    <a href="/aging" style="color:#a0b0d0;text-decoration:none;font-size:13px;padding:6px 16px;background:rgba(110,168,254,0.08);border:1px solid rgba(110,168,254,0.12);border-radius:8px;transition:all 0.2s;">📊 출고 연령 분석</a>
  </div>
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
    html += `<div class="col-row"><span>${i+1}</span><span>${col.name} ${pkMark}</span><span class="col-type">${col.type}</span><span>${col.notnull ? 'NOT NULL' : 'NULL OK'}</span><span style="color:#94a3b8">${col.comment||''}</span></div>`;
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
    html += `<td style="color:#94a3b8">${data.page * pageSize + idx + 1}</td>`;
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
    html += `<span style="color:#94a3b8;font-size:12px;">${data.page+1} / ${totalPages}</span>`;
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
              'LMOUSR':'수정자','INDBZL':'비지니스로직','INDARC':'아카이브구분자','UPDCHK':'수정체크','KEEPTS':'SMS'},
    'TASDI': {'TASKKY':'작업지시번호','TASKIT':'작업지시순번','TASKTY':'작업 타입','RSNCOD':'사유코드','STATIT':'아이템상태',
              'QTTAOR':'작업수량','QTCOMP':'완료수량','OWNRKY':'화주','SKUKEY':'품목코드','LOTNUM':'물류롯트넘버',
              'ACTCDT':'실제완료날짜','ACTCTI':'실제완료시간','QTYUOM':'Quantity','TKFLKY':'작업흐름 키','STEPNO':'단계 번호',
              'LSTTFL':'최종 스텝','LOCASR':'FROM 지번','SECTSR':'섹션ID','PAIDSR':'BOM 코드','TRNUSR':'P/T ID',
              'STRUTY':'팔렛타입','SMEAKY':'단위구성','SUOMKY':'단위','QTSPUM':'UPM','SDUOKY':'기본단위',
              'QTSDUM':'기본UPM','LOCATG':'TO 지번','SECTTG':'To 섹션ID','PAIDTG':'BOM 코드','TRNUTG':'To P/T ID',
              'TTRUTY':'To 팔렛타입','TMEAKY':'To 단위구성','TUOMKY':'To 단위','QTTPUM':'To UPM','TDUOKY':'To 기본단위',
              'QTTDUM':'To 기본UPM','LOCAAC':'실지번','SECTAC':'실섹션ID','PAIDAC':'BOM 코드','TRNUAC':'실P/T ID',
              'ATRUTY':'실팔렛타입','AMEAKY':'실단위구성','AUOMKY':'실단위','QTAPUM':'실UPM','ADUOKY':'실기본단위',
              'QTADUM':'실기본UPM','REFDKY':'참조문서','REFDIT':'참조문서It.','REFCAT':'참조문서유형','REFDAT':'참조일자',
              'PURCKY':'구매오더','PURCIT':'구매 It.','ASNDKY':'ASN 문서번호','ASNDIT':'ASN Item','RECVKY':'입고문서번호',
              'RECVIT':'입고문서아이템','SHPOKY':'출하문서번호','SHPOIT':'출하문서순번','GRPOKY':'그룹오더','GRPOIT':'그룹오더아이템',
              'SADJKY':'조정문서번호','SADJIT':'조정아이템번호','SDIFKY':'Diff.No.','SDIFIT':'Diff.It.','PHYIKY':'실사번호',
              'PHYIIT':'재고실사순번','DROPID':'Drop ID','DESC01':'품목명','DESC02':'규격','ASKU01':'ERP 품번코드',
              'ASKU02':'브랜드','ASKU03':'제조상','ASKU04':'유통기한일','ASKU05':'Image등록유무','EANCOD':'바코드',
              'GTINCD':'바코드','SKUG01':'품목유형','SKUG02':'즉시불출여부','SKUG03':'품목유형3','SKUG04':'상품구분',
              'SKUG05':'상품군','GRSWGT':'총중량','NETWGT':'KIT순중량','WGTUNT':'중량단위','LENGTH':'길이',
              'WIDTHW':'가로','HEIGHT':'높이','CUBICM':'CBM','CAPACT':'CAPA','WORKID':'작업자ID',
              'WORKNM':'작업자명','HHTTID':'PDA_ID','AREAKY':'영역','LOTA01':'저장위치','LOTA02':'플랜트',
              'LOTA03':'포장타입','LOTA04':'호기','LOTA05':'LOTA05','LOTA06':'재고상태','LOTA07':'MTO판매번호',
              'LOTA08':'국가코드','LOTA09':'MTO판매처코드','LOTA10':'보류사유명','LOTA11':'제조일자','LOTA12':'입고일자',
              'LOTA13':'유효기간','LOTA14':'개별바코드','LOTA15':'LOT 번호','LOTA16':'평량','LOTA17':'컨테이너유형',
              'LOTA18':'LOTA18','LOTA19':'LOTA19','LOTA20':'LOTA20','AWMSNO':'SEQ(MP)','AWMSTS':'자동창고 I/F',
              'SMANDT':'Client','SEBELN':'오더번호','SEBELP':'오더순번','SZMBLNO':'B/L NO','SZMIPNO':'B/L Item NO',
              'STRAID':'SCM주문번호','SVBELN':'출고오더번호','SPOSNR':'출고오더순번','STKNUM':'선적번호','STPNUM':'예약 It',
              'SWERKS':'출발지','SLGORT':'영업 부문','SDATBG':'출하계획일시','STDLNR':'작업장','SSORNU':'반품출하문서번호',
              'SSORIT':'반품출하 문서아이템','SMBLNR':'Mat.Doc.','SZEILE':'Mat.Doc.','SMJAHR':'M/D 년도','SXBLNR':'인터페이스번호',
              'SAPSTS':'ERP Mvt','DOORKY':'출하대','PTLT01':'To 공급처','PTLT02':'To 부서코드','PTLT03':'To 개별바코드',
              'PTLT04':'To Mall PO No.','PTLT05':'To Mall PO Item No.','PTLT06':'To 재고상태','PTLT07':'To Shipment Order No.',
              'PTLT08':'To 교환반납 문서','PTLT09':'To WMS PO No.','PTLT10':'To 통화','PTLT11':'To 제조일자','PTLT12':'To 입고일자',
              'PTLT13':'To 유효기간','PTLT14':'To 개별바코드','PTLT15':'To Lot번호','PTLT16':'To 매입단가','PTLT17':'To 매출단가',
              'PTLT18':'To 미사용','PTLT19':'To 미사용','PTLT20':'To 미사용','PASTKY':'적치전략키','ALSTKY':'할당전략키',
              'SBKTXT':'Text','TASRSN':'상세사유','CREDAT':'생성일','CRETIM':'생성시간','CREUSR':'생성자',
              'LMODAT':'수정일','LMOTIM':'수정시간','LMOUSR':'수정자','INDBZL':'비지니스로직 구','INDARC':'아카이브 구분자','UPDCHK':'수정 체크'}
}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tables')
def api_tables():
    conn = get_db()
    tables = []
    for name in ['ZONMA', 'LOCMA', 'STKKA', 'TASDI']:
        count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        tables.append({'name': name, 'count': count, 'columns': len(cols)})
    conn.close()
    return jsonify({'tables': tables})

@app.route('/api/schema/<table_name>')
def api_schema(table_name):
    if table_name not in ['ZONMA', 'LOCMA', 'STKKA', 'TASDI']:
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
    for name in ['ZONMA', 'LOCMA', 'STKKA', 'TASDI']:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        label_map = {'ZONMA': 'ZONMA (Zone Master)', 'LOCMA': 'LOCMA (Location Master)', 'STKKA': 'STKKA (Stock)', 'TASDI': 'TASDI (출고데이터)'}
        stats.append({'label': label_map.get(name, name), 'value': f'{cnt:,}', 'sub': f'{len(cols)} columns'})
    
    # Total records
    total = sum(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ['ZONMA','LOCMA','STKKA','TASDI'])
    stats.append({'label': 'Total Records', 'value': f'{total:,}', 'sub': '4 tables'})
    
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

    # Load master names (use str() for consistent key matching across integer/text types)
    ware_names = {}
    try:
        for r in cur.execute("SELECT WAREKY, NAME01 FROM WAHMA").fetchall():
            ware_names[str(r['WAREKY']).strip()] = (r['NAME01'] or '').strip()
    except: pass

    stl_names = {}
    try:
        for r in cur.execute("SELECT WAREKY, PLNTKY, STLKY, STLNM FROM STLMA").fetchall():
            stl_names[(str(r['WAREKY']).strip(), str(r['PLNTKY']).strip(), str(r['STLKY']).strip())] = (r['STLNM'] or '').strip()
    except: pass

    area_names = {}
    try:
        for r in cur.execute("SELECT WAREKY, AREAKY, SHORTX FROM AREMA").fetchall():
            area_names[(str(r['WAREKY']).strip(), str(r['AREAKY']).strip())] = (r['SHORTX'] or '').strip()
    except: pass

    # ZONMA: WAREKY > PLNTKY > STLKY > AREAKY > ZONEKY mapping
    cur.execute("SELECT DISTINCT WAREKY, PLNTKY, STLKY, AREAKY, ZONEKY, SHORTX FROM ZONMA")
    zone_map = {}
    zone_names = {}
    for row in cur.fetchall():
        wareky, plntky, stlky, areaky, zoneky, shortx = row['WAREKY'], row['PLNTKY'], row['STLKY'], row['AREAKY'], row['ZONEKY'], row['SHORTX']
        plntky = (str(plntky) if plntky else '').strip() or None
        stlky = (str(stlky) if stlky else '').strip() or None
        zone_map[(wareky, areaky, zoneky)] = (plntky, stlky)
        zone_names[(str(wareky).strip(), str(zoneky).strip())] = shortx

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
    for wareky in sorted(tree.keys(), key=str):
        wk = str(wareky)
        wn = ware_names.get(wk, '')
        ware_label = f"{wk} ({wn})" if wn else wk
        ware_node = {'id': f'W{wk}', 'label': ware_label, 'type': 'warehouse', 'children': [], 'count': 0}
        for plntky in sorted(tree[wareky].keys(), key=str):
            pk = str(plntky)
            pn = PLANT_NAMES.get(pk, '')
            plnt_label = f"{pk} ({pn})" if pn else pk
            plnt_node = {'id': f'W{wk}_P{pk}', 'label': plnt_label, 'type': 'plant', 'children': [], 'count': 0}
            for stlky in sorted(tree[wareky][plntky].keys(), key=str):
                sk = str(stlky)
                sn = stl_names.get((wk, pk, sk), '')
                stl_label = f"{sk} ({sn})" if sn else sk
                stl_node = {'id': f'W{wk}_P{pk}_S{sk}', 'label': stl_label, 'type': 'storage', 'children': [], 'count': 0}
                for areaky in sorted(tree[wareky][plntky][stlky].keys(), key=str):
                    ak = str(areaky)
                    an = area_names.get((wk, ak), '')
                    area_label = f"{ak} ({an})" if an else ak
                    area_node = {'id': f'W{wk}_P{pk}_S{sk}_A{ak}', 'label': area_label, 'type': 'area', 'children': [], 'count': 0}
                    for zoneky in sorted(tree[wareky][plntky][stlky][areaky].keys(), key=str):
                        locs = sorted(tree[wareky][plntky][stlky][areaky][zoneky])
                        loc_count = len(locs)
                        zk = str(zoneky)
                        zone_label = zk
                        name = zone_names.get((wk, zk), '')
                        if name and name.strip():
                            zone_label = f"{zk} ({name.strip()})"
                        zone_node = {
                            'id': f'W{wk}_P{pk}_S{sk}_A{ak}_Z{zk}',
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
    Parameters: level (warehouse|plant|storage|area|zone), wareky, plntky, stlky, areaky, zoneky, aging_months
    """
    from datetime import datetime, timedelta
    level = request.args.get('level', 'warehouse')
    wareky = request.args.get('wareky')
    plntky = request.args.get('plntky')
    stlky = request.args.get('stlky')
    areaky = request.args.get('areaky')
    zoneky = request.args.get('zoneky')
    aging_months = request.args.get('aging_months', '0')  # 0=전체, 1~6=N개월 이상

    # Calculate aging cutoff date (YYYYMMDD format)
    try:
        am = int(aging_months)
    except:
        am = 0
    aging_cutoff = None
    if am > 0:
        cutoff_date = datetime.now() - timedelta(days=am * 30)
        aging_cutoff = cutoff_date.strftime('%Y%m%d')

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

    # Lookup names from master tables
    if result:
        name_map = {}
        try:
            if level == 'warehouse':
                nrows = cur.execute("SELECT WAREKY, NAME01 FROM WAHMA").fetchall()
                name_map = {str(r['WAREKY']).strip(): (r['NAME01'] or '').strip() for r in nrows}
            elif level == 'plant':
                name_map = dict(PLANT_NAMES)
            elif level == 'storage':
                nrows = cur.execute("SELECT STLKY, STLNM FROM STLMA WHERE WAREKY=? AND PLNTKY=?", (wareky, plntky or '')).fetchall()
                name_map = {str(r['STLKY']).strip(): (r['STLNM'] or '').strip() for r in nrows}
            elif level == 'area':
                nrows = cur.execute("SELECT AREAKY, SHORTX FROM AREMA WHERE WAREKY=?", (wareky,)).fetchall()
                name_map = {str(r['AREAKY']).strip(): (r['SHORTX'] or '').strip() for r in nrows}
            elif level == 'zone':
                nrows = cur.execute("SELECT ZONEKY, SHORTX FROM ZONMA WHERE WAREKY=? AND AREAKY=?", (wareky, areaky or '')).fetchall()
                name_map = {str(r['ZONEKY']).strip(): (r['SHORTX'] or '').strip() for r in nrows}
            elif level == 'location':
                labels = [item['label'] for item in result]
                if labels:
                    ph = ",".join(["?" for _ in labels])
                    nrows = cur.execute(f"SELECT LOCAKY, SHORTX FROM LOCMA WHERE WAREKY=? AND LOCAKY IN ({ph})", [wareky] + labels).fetchall()
                    name_map = {str(r['LOCAKY']).strip(): (r['SHORTX'] or '').strip() for r in nrows}
        except Exception as e:
            print(f"[name_map] Error for level={level}: {e}")
        for item in result:
            item['name'] = name_map.get(item['label'], '')

    # Calculate aging ratio for each result item
    if aging_cutoff and result:
        # Build aging query based on level
        for item in result:
            aging_where = ["s.QTSIWH > 0", "s.LOTA11 != ''", f"s.LOTA11 <= '{aging_cutoff}'"]
            aging_params = []

            if level == 'warehouse':
                aging_where.append("s.WAREKY=?")
                aging_params.append(item['label'])
            elif level == 'plant':
                aging_where.append("s.WAREKY=?")
                aging_params.append(wareky)
                lbl_orig = '' if item['label'] == '(미지정)' else item['label']
                if item['label'] == '(미지정)':
                    aging_where.append("TRIM(s.LOTA02)=''")
                else:
                    aging_where.append("s.LOTA02=?")
                    aging_params.append(lbl_orig)
            elif level == 'storage':
                aging_where.append("s.WAREKY=?")
                aging_params.append(wareky)
                if plntky and plntky != '(미지정)':
                    aging_where.append("s.LOTA02=?")
                    aging_params.append(plntky)
                lbl_orig = '' if item['label'] == '(미지정)' else item['label']
                if item['label'] == '(미지정)':
                    aging_where.append("TRIM(s.LOTA01)=''")
                else:
                    aging_where.append("s.LOTA01=?")
                    aging_params.append(lbl_orig)
            elif level == 'area':
                aging_where.append("s.WAREKY=?")
                aging_params.append(wareky)
                if plntky and plntky != '(미지정)':
                    aging_where.append("s.LOTA02=?")
                    aging_params.append(plntky)
                if stlky and stlky != '(미지정)':
                    aging_where.append("s.LOTA01=?")
                    aging_params.append(stlky)
                aging_where.append("s.AREAKY=?")
                aging_params.append(item['label'])
            elif level == 'zone':
                aging_where.append("s.WAREKY=?")
                aging_params.append(wareky)
                aging_where.append("s.AREAKY=?")
                aging_params.append(areaky)
                aging_where.append("s.ZONEKY=?")
                aging_params.append(item['label'])
            elif level == 'location':
                aging_where.append("s.WAREKY=?")
                aging_params.append(wareky)
                aging_where.append("s.ZONEKY=?")
                aging_params.append(zoneky)
                if areaky:
                    aging_where.append("s.AREAKY=?")
                    aging_params.append(areaky)
                aging_where.append("s.LOCAKY=?")
                aging_params.append(item['label'])

            where_clause = " AND ".join(aging_where)
            aging_row = cur.execute(f"""
                SELECT CAST(ROUND(SUM(s.QTSIWH) / 20.0) AS INTEGER) as aging_qty
                FROM STKKA s WHERE {where_clause}
            """, aging_params).fetchone()
            aging_qty = aging_row['aging_qty'] if aging_row and aging_row['aging_qty'] else 0
            item['aging_qty'] = aging_qty
            item['aging_ratio'] = round(aging_qty * 100.0 / item['qty'], 1) if item['qty'] > 0 else 0
    else:
        # No aging filter - still compute default aging ratio (all stock = 0% aging by definition if no cutoff)
        for item in result:
            item['aging_qty'] = 0
            item['aging_ratio'] = 0

    conn.close()

    # Calculate max for scaling
    max_qty = max((r['qty'] for r in result), default=0)
    total_qty = sum(r['qty'] for r in result)
    total_aging_qty = sum(r.get('aging_qty', 0) for r in result)
    total_aging_ratio = round(total_aging_qty * 100.0 / total_qty, 1) if total_qty > 0 else 0
    return jsonify({
        'items': result, 'max_qty': max_qty, 'total_qty': total_qty, 'level': level,
        'aging_months': am, 'aging_cutoff': aging_cutoff or '',
        'total_aging_qty': total_aging_qty, 'total_aging_ratio': total_aging_ratio
    })








@app.route('/structure')
def structure_page():
    return render_template_string(STRUCTURE_HTML)


# ================================================
# 출고 제품 연령 분석 (Outbound Product Aging Analysis)
# ================================================
@app.route('/aging')
def aging_page():
    return render_template_string(AGING_HTML)


@app.route('/api/aging/summary')
def api_aging_summary():
    """출고 제품 연령 분석 요약 데이터"""
    from_month = request.args.get('from', '')  # YYYYMM
    to_month = request.args.get('to', '')      # YYYYMM
    plant = request.args.get('plant', '')       # LOTA02 e.g. P100
    warehouse = request.args.get('warehouse', '')  # AREAKY e.g. 280

    conn = get_db()

    # Build WHERE clause based on ACTCDT (실제완료날짜)
    conditions = ["ACTCDT IS NOT NULL AND ACTCDT != '' AND LOTA11 IS NOT NULL AND LOTA11 != ''"]
    params = []
    if from_month:
        conditions.append("SUBSTR(ACTCDT,1,6) >= ?")
        params.append(from_month)
    if to_month:
        conditions.append("SUBSTR(ACTCDT,1,6) <= ?")
        params.append(to_month)
    if plant:
        conditions.append("LOTA02 = ?")
        params.append(plant)
    if warehouse:
        conditions.append("AREAKY = ?")
        params.append(warehouse)

    where = " AND ".join(conditions)

    # ---- 1) Monthly outbound quantity by UOM ----
    sql_monthly_qty = f"""
        SELECT SUBSTR(ACTCDT,1,6) as month,
               SUOMKY as uom,
               SUM(CAST(QTCOMP AS REAL)) as total_qty,
               COUNT(*) as cnt
        FROM TASDI
        WHERE {where}
        GROUP BY SUBSTR(ACTCDT,1,6), SUOMKY
        ORDER BY month, uom
    """
    rows_qty = conn.execute(sql_monthly_qty, params).fetchall()
    monthly_qty = {}
    for r in rows_qty:
        m = r['month']
        if m not in monthly_qty:
            monthly_qty[m] = {}
        monthly_qty[m][r['uom']] = {'qty': r['total_qty'], 'cnt': r['cnt']}

    # ---- 2) Inventory days (ACTCDT - LOTA11) distribution by month ----
    sql_aging = f"""
        SELECT SUBSTR(ACTCDT,1,6) as month,
               ACTCDT, LOTA11,
               CAST(QTCOMP AS REAL) as qty,
               SUOMKY as uom,
               SMEAKY as sku,
               DESC01 as desc1,
               LOTA02 as plant_code,
               AREAKY as area
        FROM TASDI
        WHERE {where}
        ORDER BY ACTCDT
    """
    rows_aging = conn.execute(sql_aging, params).fetchall()

    from datetime import datetime
    monthly_aging = {}
    # Aging buckets: 0-7, 8-14, 15-30, 31-60, 61-90, 91-180, 181-365, 365+
    bucket_keys = ['0-7', '8-14', '15-30', '31-60', '61-90', '91-180', '181-365', '365+']

    for r in rows_aging:
        m = r['month']
        try:
            d_act = datetime.strptime(r['ACTCDT'], '%Y%m%d')
            d_mfg = datetime.strptime(r['LOTA11'], '%Y%m%d')
            days = (d_act - d_mfg).days
            if days < 0:
                days = 0
        except:
            continue

        if m not in monthly_aging:
            monthly_aging[m] = {b: {'qty': 0, 'cnt': 0} for b in bucket_keys}
            monthly_aging[m]['total_days'] = 0
            monthly_aging[m]['total_cnt'] = 0
            monthly_aging[m]['details'] = []

        monthly_aging[m]['total_days'] += days
        monthly_aging[m]['total_cnt'] += 1

        # Determine bucket
        if days <= 7:
            b = '0-7'
        elif days <= 14:
            b = '8-14'
        elif days <= 30:
            b = '15-30'
        elif days <= 60:
            b = '31-60'
        elif days <= 90:
            b = '61-90'
        elif days <= 180:
            b = '91-180'
        elif days <= 365:
            b = '181-365'
        else:
            b = '365+'

        monthly_aging[m][b]['qty'] += r['qty'] or 0
        monthly_aging[m][b]['cnt'] += 1

    # Compute averages
    for m in monthly_aging:
        tc = monthly_aging[m]['total_cnt']
        monthly_aging[m]['avg_days'] = round(monthly_aging[m]['total_days'] / tc, 1) if tc > 0 else 0
        del monthly_aging[m]['details']

    # ---- 3) Available filters ----
    plants_raw = conn.execute("SELECT DISTINCT LOTA02 FROM TASDI WHERE LOTA02 IS NOT NULL AND LOTA02 != '' ORDER BY LOTA02").fetchall()
    plants = [{'code': r['LOTA02'], 'name': PLANT_NAMES.get(r['LOTA02'], r['LOTA02'])} for r in plants_raw]

    warehouses_sql = "SELECT DISTINCT AREAKY FROM TASDI WHERE AREAKY IS NOT NULL AND AREAKY != ''"
    wh_params = []
    if plant:
        warehouses_sql += " AND LOTA02 = ?"
        wh_params.append(plant)
    warehouses_sql += " ORDER BY AREAKY"
    wh_raw = conn.execute(warehouses_sql, wh_params).fetchall()
    warehouses = [r['AREAKY'] for r in wh_raw]

    # Date range
    date_range = conn.execute("SELECT MIN(SUBSTR(ACTCDT,1,6)), MAX(SUBSTR(ACTCDT,1,6)) FROM TASDI WHERE ACTCDT IS NOT NULL AND ACTCDT != ''").fetchone()

    conn.close()

    return jsonify({
        'monthly_qty': monthly_qty,
        'monthly_aging': monthly_aging,
        'plants': plants,
        'warehouses': warehouses,
        'date_range': {'min': date_range[0], 'max': date_range[1]},
        'bucket_keys': bucket_keys
    })


@app.route('/api/aging/detail')
def api_aging_detail():
    """출고 제품 연령 상세 데이터 (개별 건)"""
    from_month = request.args.get('from', '')
    to_month = request.args.get('to', '')
    plant = request.args.get('plant', '')
    warehouse = request.args.get('warehouse', '')
    page = int(request.args.get('page', 0))
    page_size = min(int(request.args.get('page_size', 50)), 200)

    conn = get_db()
    conditions = ["ACTCDT IS NOT NULL AND ACTCDT != '' AND LOTA11 IS NOT NULL AND LOTA11 != ''"]
    params = []
    if from_month:
        conditions.append("SUBSTR(ACTCDT,1,6) >= ?")
        params.append(from_month)
    if to_month:
        conditions.append("SUBSTR(ACTCDT,1,6) <= ?")
        params.append(to_month)
    if plant:
        conditions.append("LOTA02 = ?")
        params.append(plant)
    if warehouse:
        conditions.append("AREAKY = ?")
        params.append(warehouse)

    where = " AND ".join(conditions)

    count = conn.execute(f"SELECT COUNT(*) FROM TASDI WHERE {where}", params).fetchone()[0]

    sql = f"""
        SELECT TASKKY, ACTCDT, LOTA11, LOTA02, AREAKY, LOCASR,
               SMEAKY, DESC01, SUOMKY, CAST(QTCOMP AS REAL) as qty,
               SKUKEY, LOTNUM
        FROM TASDI
        WHERE {where}
        ORDER BY ACTCDT DESC, SMEAKY
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(sql, params + [page_size, page * page_size]).fetchall()

    from datetime import datetime
    result = []
    for r in rows:
        try:
            d_act = datetime.strptime(r['ACTCDT'], '%Y%m%d')
            d_mfg = datetime.strptime(r['LOTA11'], '%Y%m%d')
            days = max(0, (d_act - d_mfg).days)
        except:
            days = None
        result.append({
            'task_key': r['TASKKY'],
            'act_date': r['ACTCDT'],
            'mfg_date': r['LOTA11'],
            'plant': r['LOTA02'],
            'plant_name': PLANT_NAMES.get(r['LOTA02'], r['LOTA02']),
            'warehouse': r['AREAKY'],
            'location': r['LOCASR'],
            'sku': r['SMEAKY'],
            'desc': r['DESC01'],
            'uom': r['SUOMKY'],
            'qty': r['qty'],
            'days': days,
            'lot': r['LOTNUM']
        })

    conn.close()
    return jsonify({'rows': result, 'total': count, 'page': page, 'page_size': page_size})


STRUCTURE_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>저장 위치 구조 조회 | 적재율 히트맵</title>
<style>
:root {
  --bg-primary: #080d1a;
  --bg-secondary: #0e1529;
  --bg-tertiary: #141d35;
  --border: rgba(120,160,255,0.1);
  --text-primary: #edf0f7;
  --text-secondary: #a0b0d0;
  --text-muted: #5a6d8e;
  --accent: #6ea8fe;
  --accent-dark: #4a8af0;
  --green: #34d399;
  --yellow: #fcd34d;
  --purple: #b197fc;
  --pink: #f472b6;
  --orange: #fdba74;
  --red: #fca5a5;
  --glass: rgba(14,21,41,0.7);
  --glass-border: rgba(120,160,255,0.12);
  --glow: rgba(110,168,254,0.06);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', -apple-system, 'Malgun Gothic', sans-serif; background: var(--bg-primary); color: var(--text-primary); }
::selection { background: rgba(110,168,254,0.35); }

/* Header */
.header {
  background: linear-gradient(135deg, #0a1128 0%, #121d3a 50%, #162550 100%);
  padding: 14px 24px;
  border-bottom: 1px solid rgba(110,168,254,0.1);
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
}
.header h1 { font-size: 18px; background: linear-gradient(135deg, #6ea8fe, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; letter-spacing: 0.5px; }
.header .badge { font-size: 11px; padding: 4px 12px; border-radius: 6px; backdrop-filter: blur(8px); }
.header .b1 { background: rgba(110,168,254,0.12); color: var(--accent); border: 1px solid rgba(110,168,254,0.2); }
.header .b2 { background: rgba(160,176,208,0.08); color: var(--text-secondary); border: 1px solid rgba(160,176,208,0.1); }
.header a { color: var(--text-secondary); text-decoration: none; font-size: 13px; margin-left: auto; padding: 6px 16px; border-radius: 8px; background: rgba(110,168,254,0.08); border: 1px solid rgba(110,168,254,0.12); transition: all 0.2s; }
.header a:hover { color: var(--accent); background: rgba(110,168,254,0.18); border-color: rgba(110,168,254,0.3); }

/* Layout */
.layout { display: flex; height: calc(100vh - 52px); position: relative; background: linear-gradient(180deg, var(--bg-primary) 0%, #060a14 100%); }

/* Left panel - tree */
.tree-panel {
  width: 420px; min-width: 320px; max-width: 600px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, #0b1020 100%);
  border-right: 1px solid var(--glass-border);
  display: flex; flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ease, min-width 0.3s ease, opacity 0.3s ease;
}
.tree-panel.collapsed {
  width: 0px !important; min-width: 0 !important;
  opacity: 0; pointer-events: none;
  border-right: none;
}
.resize-handle.collapsed { display: none; }
.tree-toolbar {
  padding: 14px 18px;
  border-bottom: 1px solid var(--glass-border);
  background: linear-gradient(135deg, rgba(20,29,53,0.9), rgba(14,21,41,0.95));
  backdrop-filter: blur(12px);
  display: flex; flex-direction: column; gap: 8px;
}
.tree-toolbar h3 { font-size: 13px; background: linear-gradient(90deg, var(--accent), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.search-box {
  width: 100%; padding: 9px 14px;
  background: rgba(8,13,26,0.6); border: 1px solid var(--border);
  color: var(--text-primary); border-radius: 8px; font-size: 13px; outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-box:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(110,168,254,0.1); }
.search-box::placeholder { color: var(--text-muted); }
.tree-actions { display: flex; gap: 6px; }
.tree-actions button {
  flex: 1; padding: 7px 10px; font-size: 11px;
  background: rgba(110,168,254,0.06); color: var(--text-secondary);
  border: 1px solid rgba(110,168,254,0.1); border-radius: 8px; cursor: pointer;
  transition: all 0.2s; font-weight: 500;
}
.tree-actions button:hover { background: rgba(110,168,254,0.15); color: var(--accent); border-color: rgba(110,168,254,0.25); box-shadow: 0 2px 12px rgba(110,168,254,0.1); }
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
.tree-row:hover { background: rgba(110,168,254,0.06); }
.tree-row.selected { background: linear-gradient(90deg, rgba(110,168,254,0.15), rgba(110,168,254,0.05)); border-left-color: var(--accent); box-shadow: inset 0 0 20px rgba(110,168,254,0.05); }
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
  border-bottom: 1px solid var(--glass-border);
  background: linear-gradient(135deg, rgba(20,29,53,0.95), rgba(14,21,41,0.9));
  backdrop-filter: blur(12px);
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}
.s-card {
  background: rgba(110,168,254,0.05); border: 1px solid rgba(110,168,254,0.1);
  border-radius: 12px; padding: 12px 14px; text-align: center;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}
.s-card:hover { background: rgba(110,168,254,0.1); border-color: rgba(110,168,254,0.2); box-shadow: 0 4px 20px rgba(110,168,254,0.08); }
.s-card .s-val { font-size: 22px; font-weight: 700; background: linear-gradient(135deg, var(--accent), #93c5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.s-card .s-lbl { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* Breadcrumb */
.breadcrumb {
  padding: 12px 28px;
  background: rgba(14,21,41,0.8);
  border-bottom: 1px solid var(--glass-border);
  font-size: 16px; color: var(--text-muted);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  backdrop-filter: blur(8px);
}
.breadcrumb .bc-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 16px; border-radius: 10px; cursor: pointer;
  background: rgba(110,168,254,0.06); color: var(--text-secondary);
  border: 1px solid rgba(110,168,254,0.1); font-size: 15px; font-weight: 500;
  transition: all 0.25s; white-space: nowrap;
}
.breadcrumb .bc-btn:hover { background: rgba(110,168,254,0.15); color: var(--accent); border-color: rgba(110,168,254,0.3); box-shadow: 0 2px 12px rgba(110,168,254,0.1); }
.breadcrumb .bc-btn.current {
  background: linear-gradient(135deg, rgba(110,168,254,0.2), rgba(167,139,250,0.12)); color: var(--accent);
  border-color: rgba(110,168,254,0.35); font-weight: 600;
  box-shadow: 0 2px 16px rgba(110,168,254,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}
.breadcrumb .sep { color: var(--text-muted); font-size: 18px; margin: 0 2px; user-select: none; }

/* Aging filter bar - persistent separate row */
.aging-filter-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 28px;
  background: linear-gradient(135deg, rgba(14,21,41,0.95), rgba(10,17,40,0.9));
  border-bottom: 1px solid var(--glass-border);
  font-size: 16px; flex-shrink: 0; flex-wrap: wrap;
  backdrop-filter: blur(8px);
}
.aging-filter-bar .aging-info {
  margin-left: 12px; font-size: 14px; color: var(--text-muted); font-style: italic;
}
.aging-label {
  color: var(--accent) !important; font-weight: 700; font-size: 16px !important;
  cursor: default !important; margin-right: 6px;
}
.aging-radio {
  cursor: pointer; display: inline-flex; align-items: center;
  padding: 6px 14px; border-radius: 10px;
  background: rgba(110,168,254,0.04); border: 1px solid rgba(110,168,254,0.08);
  transition: all 0.25s;
}
.aging-radio:hover { background: rgba(110,168,254,0.12); border-color: rgba(110,168,254,0.25); box-shadow: 0 2px 10px rgba(110,168,254,0.08); }
.aging-radio input[type="radio"] { display: none; }
.aging-radio span {
  font-size: 15px !important; color: var(--text-secondary) !important;
  cursor: pointer !important; white-space: nowrap; font-weight: 500;
}
.aging-radio input[type="radio"]:checked + span {
  color: #6ea8fe !important; font-weight: 700;
}
.aging-radio:has(input:checked) {
  background: linear-gradient(135deg, rgba(110,168,254,0.18), rgba(167,139,250,0.1)); border-color: rgba(110,168,254,0.4);
  box-shadow: 0 2px 16px rgba(110,168,254,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
}

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
  padding: 7px 12px; border-bottom: 1px solid rgba(99,140,255,0.06);
}
.data-table tr:hover td { background: rgba(99,140,255,0.06); }
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
  display: flex; border-bottom: 1px solid var(--glass-border);
  background: rgba(14,21,41,0.8); backdrop-filter: blur(8px);
}
.view-tab {
  padding: 10px 22px; font-size: 13px; cursor: pointer;
  color: var(--text-muted); border-bottom: 2px solid transparent;
  transition: all 0.25s; background: none; border-top: none; border-left: none; border-right: none; font-weight: 500;
}
.view-tab:hover { color: var(--text-primary); background: rgba(110,168,254,0.06); }
.view-tab.active { color: var(--accent); border-bottom-color: var(--accent); background: rgba(110,168,254,0.04); }

/* Heatmap container */
.heatmap-container {
  position: relative; flex: 1; overflow: auto; background: linear-gradient(180deg, var(--bg-primary), #060a14);
  display: flex; flex-direction: column;
}
.heatmap-header {
  display: flex; align-items: center; gap: 16px; padding: 12px 20px;
  border-bottom: 1px solid var(--glass-border); background: linear-gradient(135deg, rgba(20,29,53,0.95), rgba(14,21,41,0.9)); backdrop-filter: blur(8px); flex-shrink: 0; flex-wrap: wrap;
}
.heatmap-header .hm-title { font-size: 14px; font-weight: 700; background: linear-gradient(90deg, var(--accent), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.heatmap-header .hm-stat { font-size: 12px; color: var(--text-muted); }
.heatmap-header .hm-stat b { color: var(--text-primary); font-weight: 700; }
.heatmap-header .hm-sort { display: flex; align-items: center; gap: 6px; margin-left: auto; }
.heatmap-header .hm-sort label { font-size: 11px; color: var(--text-muted); }
.heatmap-header .hm-sort select {
  background: rgba(8,13,26,0.6); border: 1px solid var(--border); color: var(--text-primary);
  padding: 5px 10px; border-radius: 6px; font-size: 11px; outline: none;
}

.heatmap-grid-wrap { flex: 1; overflow: auto; padding: 16px; }
.heatmap-grid { display: flex; flex-wrap: wrap; gap: 5px; align-content: flex-start; }

.hm-cell {
  border-radius: 12px; cursor: pointer; position: relative;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(255,255,255,0.06);
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06);
}
.hm-cell:hover { transform: scale(1.08); z-index: 2; box-shadow: 0 8px 32px rgba(110,168,254,0.25), 0 0 0 1px var(--accent); border-color: var(--accent); }
.hm-cell .hm-lbl {
  font-weight: 700;
  text-align: center; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; width: 100%; padding: 0 4px;
}
.hm-cell .hm-pct { font-weight: 800; }
.hm-cell .hm-sub { opacity: 0.9; }
.hm-cell .hm-aging {
  font-weight: 900;
  text-align: center; width: 100%; padding: 6px 8px;
  background: linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.85) 100%);
  border-radius: 0 0 11px 11px;
  margin-top: auto; flex-shrink: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  letter-spacing: 1px;
}

/* Heatmap legend */
.hm-legend {
  display: flex; align-items: center; gap: 12px; padding: 10px 20px;
  border-top: 1px solid var(--glass-border); flex-shrink: 0;
  background: linear-gradient(135deg, rgba(20,29,53,0.95), rgba(14,21,41,0.9)); backdrop-filter: blur(8px); flex-wrap: wrap;
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
  position: fixed; display: none; background: rgba(8,13,26,0.92); border: 1px solid rgba(110,168,254,0.3);
  border-radius: 14px; padding: 16px 20px; pointer-events: none; z-index: 1000;
  min-width: 250px; backdrop-filter: blur(20px) saturate(1.2); box-shadow: 0 16px 48px rgba(0,0,0,0.6), 0 0 30px rgba(110,168,254,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
}
.hm-tooltip .tt-name { color: var(--accent); font-weight: 700; font-size: 14px; margin-bottom: 6px; }
.hm-tooltip .tt-pct { font-size: 28px; font-weight: 900; margin: 4px 0; }
.hm-tooltip .tt-row { display: flex; justify-content: space-between; font-size: 12px; padding: 2px 0; gap: 16px; }
.hm-tooltip .tt-row .k { color: var(--text-muted); }
.hm-tooltip .tt-row .v { color: var(--text-primary); font-weight: 600; }
.hm-tooltip .tt-status { font-size: 11px; margin-top: 6px; padding: 3px 8px; border-radius: 4px; display: inline-block; font-weight: 600; }

/* Welcome */
.welcome { text-align: center; padding: 60px 40px; }
.welcome h2 { font-size: 24px; background: linear-gradient(135deg, var(--text-primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; font-weight: 700; }
.welcome p { color: var(--text-muted); font-size: 14px; line-height: 1.8; }
.welcome .hierarchy-demo { margin-top: 24px; display: inline-block; text-align: left; font-size: 14px; color: var(--text-secondary); line-height: 2; }

/* Resize handle */
.resize-handle {
  width: 4px; cursor: col-resize; background: transparent; flex-shrink: 0;
  transition: background 0.2s;
  border-left: 1px solid var(--glass-border);
}
.resize-handle:hover, .resize-handle.active { background: linear-gradient(180deg, var(--accent), var(--purple)); }

/* Tree panel toggle */
.tree-toggle-btn {
  position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  z-index: 20; width: 26px; height: 64px;
  background: linear-gradient(180deg, rgba(20,29,53,0.95), rgba(14,21,41,0.9)); border: 1px solid rgba(110,168,254,0.15);
  border-left: none; border-radius: 0 10px 10px 0;
  color: var(--text-secondary); font-size: 14px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.25s ease;
  box-shadow: 3px 0 16px rgba(0,0,0,0.3); backdrop-filter: blur(12px);
}
.tree-toggle-btn:hover { background: linear-gradient(180deg, var(--accent), var(--accent-dark)); color: #fff; box-shadow: 3px 0 20px rgba(110,168,254,0.3); border-color: var(--accent); }
.tree-toggle-btn .arrow { transition: transform 0.3s ease; display: inline-block; }
.tree-toggle-btn.collapsed .arrow { transform: rotate(180deg); }



/* Loading */
.loading-spinner {
  text-align: center; padding: 40px; color: var(--text-muted);
}

/* Highlight matches */
.match-highlight { background: rgba(110,168,254,0.2); border-radius: 3px; padding: 0 2px; }

@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .tree-panel { width: 100% !important; max-width: 100%; height: 50vh; }
  .resize-handle { display: none; }
  .tree-toggle-btn { display: none; }
}
</style>
</head>
<body>

<div class="header">
  <h1>저장 위치 구조 조회</h1>
  <span class="badge b1">Storage Location Structure</span>
  <span class="badge b2">거점 > 플랜트 > 저장위치 > 영역 > 구역 > 지번</span>
  <div style="margin-left:auto;display:flex;gap:8px;">
    <a href="/">← DB Viewer</a>
    <a href="/aging">📊 출고 연령 분석</a>
  </div>
</div>

<div class="layout">
  <!-- Tree panel toggle button -->
  <button class="tree-toggle-btn collapsed" id="treePanelToggle" onclick="toggleTreePanel()" title="트리 패널 보이기">
    <span class="arrow">◀</span>
  </button>

  <!-- Tree panel -->
  <div class="tree-panel collapsed" id="treePanel" style="width:0px;">
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
  <div class="resize-handle collapsed" id="resizeHandle"></div>

  <!-- Detail panel -->
  <div class="detail-panel">
    <div class="summary-bar" id="summaryBar">
      <div class="summary-cards" id="summaryCards"></div>
    </div>
    <div class="breadcrumb" id="breadcrumb">
      <span class="current">전체 구조</span>
    </div>
    <div class="aging-filter-bar" id="agingFilterBar">
      <span class="aging-label">📅 장기재고:</span>
      <label class="aging-radio" onclick="onAgingClick('0')"><input type="radio" name="agingMonths" value="0" checked><span>전체</span></label>
      <label class="aging-radio" onclick="onAgingClick('1')"><input type="radio" name="agingMonths" value="1"><span>1개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('2')"><input type="radio" name="agingMonths" value="2"><span>2개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('3')"><input type="radio" name="agingMonths" value="3"><span>3개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('4')"><input type="radio" name="agingMonths" value="4"><span>4개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('5')"><input type="radio" name="agingMonths" value="5"><span>5개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('6')"><input type="radio" name="agingMonths" value="6"><span>6개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('7')"><input type="radio" name="agingMonths" value="7"><span>7개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('8')"><input type="radio" name="agingMonths" value="8"><span>8개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('9')"><input type="radio" name="agingMonths" value="9"><span>9개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('10')"><input type="radio" name="agingMonths" value="10"><span>10개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('11')"><input type="radio" name="agingMonths" value="11"><span>11개월+</span></label>
      <label class="aging-radio" onclick="onAgingClick('12')"><input type="radio" name="agingMonths" value="12"><span>12개월+</span></label>
      <span class="aging-info" id="agingInfo"></span>
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
        <span class="hm-stat" id="hmAgingStat" style="display:none;">장기재고: <b id="hmAgingRatio" style="color:var(--yellow);">-</b></span>
        <div class="hm-sort">
          <label>정렬:</label>
          <select id="hmSortBy" onchange="resortHeatmap()">
            <option value="label_asc" selected>이름순</option>
            <option value="usage_desc">적재율 높은순</option>
            <option value="usage_asc">적재율 낮은순</option>
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
  <div class="tt-row" id="ttAgingRow" style="display:none;"><span class="k">장기재고</span><span class="v" id="ttAging"></span></div>
  <div class="tt-row" id="ttAgingRatioRow" style="display:none;"><span class="k">장기재고 비율</span><span class="v" id="ttAgingRatio" style="color:var(--yellow);"></span></div>
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
let lastSelectedNode = null;

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
  if (u <= 0) return '#cbd5e1';
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
  if (u <= 0) return '#94a3b8';
  if (u <= 70) return '#1e293b';
  return '#fff';
}
function usageStatus(u) {
  if (u <= 0) return { text:'재고없음', bg:'#f1f5f9', color:'#94a3b8' };
  if (u <= 40) return { text:'여유', bg:'rgba(22,163,74,0.1)', color:'#16a34a' };
  if (u <= 60) return { text:'양호', bg:'rgba(101,163,13,0.1)', color:'#65a30d' };
  if (u <= 80) return { text:'주의', bg:'rgba(217,119,6,0.1)', color:'#d97706' };
  if (u <= 100) return { text:'포화 임박', bg:'rgba(234,88,12,0.1)', color:'#ea580c' };
  return { text:'CAPA 초과', bg:'rgba(220,38,38,0.1)', color:'#dc2626' };
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

    // 기본값: 1100 거점 자동 선택
    const defaultNode = findNodeById(treeData, 'W1100');
    if (defaultNode) {
      navigateToNode('W1100');
    }
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
function getAgingMonths() {
  const checked = document.querySelector('input[name="agingMonths"]:checked');
  return checked ? checked.value : '0';
}

function onAgingClick(val) {
  // Select the radio button
  const radio = document.querySelector(`input[name="agingMonths"][value="${val}"]`);
  if (radio) radio.checked = true;

  // Always execute query with current node
  if (lastSelectedNode) {
    if (lastSelectedNode.type === 'root') {
      loadWarehouseHeatmap();
    } else {
      loadHeatmapForNode(lastSelectedNode);
    }
  }
}

function showNodeDetail(node) {
  lastSelectedNode = node;
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

function extractCode(label) {
  // Extract code from label like "1100 (청주공장창고)" -> "1100"
  const m = label.match(/^([^ ]+)/);
  return m ? m[1] : label;
}

function showGroupDetail(node, content) {
  const typeLabel = TYPE_LABELS[node.type];
  let html = `<div class="detail-title">${ICONS[node.type]} ${typeLabel}: ${node.label}</div>`;
  html += `<div class="detail-subtitle">하위 항목 ${node.children ? node.children.length : 0}개 | 총 지번 ${node.count.toLocaleString()}개</div>`;

  if (node.children && node.children.length > 0) {
    const childType = node.children[0].type;
    const childLabel = TYPE_LABELS[childType];

    html += `<table class="data-table"><thead><tr>`;
    html += `<th>#</th><th>${childLabel}</th><th>명칭</th><th>하위 수</th><th>지번수</th><th>팔레트재고</th><th>Capa</th><th>적재율</th><th>장기재고 비율</th><th>분포</th>`;
    html += `</tr></thead><tbody>`;

    node.children.forEach((child, i) => {
      const code = extractCode(child.label);
      const pct = node.count > 0 ? ((child.count / node.count) * 100).toFixed(1) : 0;
      const barW = Math.max(2, Math.min(200, (child.count / node.count) * 200));
      html += `<tr onclick="navigateToNode('${child.id}')" style="cursor:pointer">`;
      html += `<td style="color:var(--text-muted)">${i+1}</td>`;
      html += `<td class="clickable">${ICONS[childType]} ${child.label}</td>`;
      html += `<td class="stock-name" data-code="${code}" style="color:var(--text-muted);font-size:11px;">-</td>`;
      html += `<td>${child.children ? child.children.length : (child.locations ? child.locations.length : '-')}</td>`;
      html += `<td><b>${child.count.toLocaleString()}</b></td>`;
      html += `<td class="stock-qty" data-code="${code}">-</td>`;
      html += `<td class="stock-capa" data-code="${code}">-</td>`;
      html += `<td class="stock-usage" data-code="${code}">-</td>`;
      html += `<td class="stock-aging" data-code="${code}">-</td>`;
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
  const hasAging = getAgingMonths() !== '0';
  let cellW, cellH, fontSize, pctSize;
  if (count <= 8) { cellW=180; cellH=110; fontSize=14; pctSize=24; }
  else if (count <= 20) { cellW=145; cellH=90; fontSize=13; pctSize=21; }
  else if (count <= 50) { cellW=120; cellH=76; fontSize=12; pctSize=18; }
  else if (count <= 100) { cellW=100; cellH=64; fontSize=11; pctSize=16; }
  else if (count <= 200) { cellW=80; cellH=52; fontSize=10; pctSize=14; }
  else { cellW=62; cellH=42; fontSize=9; pctSize=12; }
  // 장기재고 표시 시 셀 높이 확대
  if (hasAging) { cellH += 28; }

  sorted.forEach(item => {
    const u = item.usage || 0;
    const bg = usageColor(u);
    const fg = usageTextColor(u);

    const cell = document.createElement('div');
    cell.className = 'hm-cell';
    cell.style.width = cellW + 'px';
    cell.style.minHeight = cellH + 'px';
    cell.style.background = bg;
    cell.style.color = fg;

    const lbl = document.createElement('div');
    lbl.className = 'hm-lbl';
    lbl.style.fontSize = fontSize + 'px';
    lbl.textContent = item.label;

    // Show name below label if available
    let nameEl = null;
    if (item.name) {
      nameEl = document.createElement('div');
      nameEl.className = 'hm-name';
      const nameFs = Math.max(11, fontSize);
      nameEl.style.fontSize = nameFs + 'px';
      nameEl.style.fontWeight = '600';
      nameEl.style.opacity = '1';

      nameEl.style.overflow = 'hidden';
      nameEl.style.textOverflow = 'ellipsis';
      nameEl.style.whiteSpace = 'nowrap';
      nameEl.style.maxWidth = (cellW - 8) + 'px';
      nameEl.textContent = item.name;
    }

    const pct = document.createElement('div');
    pct.className = 'hm-pct';
    pct.style.fontSize = pctSize + 'px';
    pct.textContent = u > 0 ? Math.round(u) + '%' : '-';

    cell.appendChild(lbl);
    if (nameEl) cell.appendChild(nameEl);
    cell.appendChild(pct);

    // Extra info for larger cells
    if (cellH >= 76) {
      const sub = document.createElement('div');
      sub.className = 'hm-sub';
      sub.style.fontSize = (fontSize - 2) + 'px';
      sub.textContent = formatNumber(item.qty) + ' / ' + formatNumber(item.maxcpc) + ' PLT';
      cell.appendChild(sub);
    }

    // Aging ratio at bottom of cell
    const agingVal = item.aging_ratio || 0;
    const agingMonthsSel = getAgingMonths();
    if (agingMonthsSel !== '0' && agingVal > 0) {
      const agingDiv = document.createElement('div');
      agingDiv.className = 'hm-aging';
      const agingFs = Math.max(13, fontSize + 1);
      agingDiv.style.fontSize = agingFs + 'px';
      agingDiv.style.color = agingVal >= 50 ? '#fde68a' : agingVal >= 30 ? '#fed7aa' : '#e0e7ff';
      agingDiv.textContent = '장기 ' + agingVal.toFixed(1) + '%';
      cell.appendChild(agingDiv);
    } else if (agingMonthsSel !== '0') {
      const agingDiv = document.createElement('div');
      agingDiv.className = 'hm-aging';
      const agingFs = Math.max(13, fontSize + 1);
      agingDiv.style.fontSize = agingFs + 'px';
      agingDiv.style.color = 'rgba(224,231,255,0.8)';
      agingDiv.textContent = '장기 0%';
      cell.appendChild(agingDiv);
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

  // Update aging stat in header
  const agingStatEl = document.getElementById('hmAgingStat');
  const amSel = getAgingMonths();
  if (amSel !== '0') {
    const totalAgingQty = items.reduce((s, i) => s + (i.aging_qty || 0), 0);
    const totalAgingRatio = totalQty > 0 ? (totalAgingQty * 100 / totalQty).toFixed(1) : '0';
    agingStatEl.style.display = '';
    const arEl = document.getElementById('hmAgingRatio');
    arEl.textContent = totalAgingRatio + '%';
    arEl.style.color = totalAgingRatio >= 50 ? 'var(--yellow)' : totalAgingRatio >= 30 ? 'var(--orange)' : 'var(--green)';
  } else {
    agingStatEl.style.display = 'none';
  }
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
  document.getElementById('ttName').textContent = item.name ? item.label + ' (' + item.name + ')' : item.label;
  const pctEl = document.getElementById('ttPct');
  pctEl.textContent = u > 0 ? u.toFixed(1) + '%' : 'N/A';
  pctEl.style.color = usageColor(u === 0 ? 0.1 : u);
  document.getElementById('ttQty').textContent = formatNumber(item.qty) + ' PLT';
  document.getElementById('ttCapa').textContent = formatNumber(item.maxcpc) + ' PLT';
  document.getElementById('ttCnt').textContent = (item.cnt || '-').toLocaleString();
  document.getElementById('ttLocs').textContent = (item.locs || '-').toLocaleString();
  // Aging info in tooltip
  const am = getAgingMonths();
  const agingRow = document.getElementById('ttAgingRow');
  const agingRatioRow = document.getElementById('ttAgingRatioRow');
  if (am !== '0') {
    agingRow.style.display = 'flex';
    agingRatioRow.style.display = 'flex';
    document.getElementById('ttAging').textContent = formatNumber(item.aging_qty || 0) + ' PLT';
    const arVal = item.aging_ratio || 0;
    const arEl = document.getElementById('ttAgingRatio');
    arEl.textContent = arVal.toFixed(1) + '%';
    arEl.style.color = arVal >= 50 ? 'var(--yellow)' : arVal >= 30 ? 'var(--orange)' : 'var(--green)';
  } else {
    agingRow.style.display = 'none';
    agingRatioRow.style.display = 'none';
  }
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

  params.aging_months = getAgingMonths();
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
    updateAgingInfo(data);

    // Update table view: names, stock quantities, capa, and usage
    data.items.forEach(item => {
      const code = item.label;
      // Update name in table
      const nameCells = document.querySelectorAll(`.stock-name[data-code="${code}"]`);
      nameCells.forEach(cell => {
        cell.textContent = item.name || '-';
        cell.style.color = item.name ? 'var(--text-secondary)' : 'var(--text-muted)';
        cell.style.fontSize = '12px';
      });
      const cells = document.querySelectorAll(`.stock-qty[data-code="${code}"]`);
      cells.forEach(cell => {
        cell.textContent = formatNumber(item.qty);
        cell.style.color = 'var(--yellow)';
        cell.style.fontWeight = '600';
      });
      const capaCells = document.querySelectorAll(`.stock-capa[data-code="${code}"]`);
      capaCells.forEach(cell => {
        cell.textContent = formatNumber(item.maxcpc || 0);
        cell.style.color = 'var(--green)';
      });
      const usageCells = document.querySelectorAll(`.stock-usage[data-code="${code}"]`);
      usageCells.forEach(cell => {
        const u = item.usage || 0;
        cell.textContent = u.toFixed(1) + '%';
        cell.style.fontWeight = '600';
        cell.style.color = u > 100 ? 'var(--red)' : u > 80 ? 'var(--orange)' : 'var(--green)';
      });
      // Update aging ratio in table
      const agingCells = document.querySelectorAll(`.stock-aging[data-code="${code}"]`);
      agingCells.forEach(cell => {
        const am = getAgingMonths();
        if (am !== '0') {
          const ar = item.aging_ratio || 0;
          cell.textContent = ar.toFixed(1) + '%';
          cell.style.fontWeight = '600';
          cell.style.color = ar >= 50 ? 'var(--yellow)' : ar >= 30 ? 'var(--orange)' : ar > 0 ? 'var(--text-secondary)' : 'var(--text-muted)';
        } else {
          cell.textContent = '-';
          cell.style.color = 'var(--text-muted)';
        }
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
  let html = `<span class="bc-btn" onclick="showWelcome()">🏠 전체</span>`;

  let currentId = '';
  for (const part of parts) {
    if (currentId) currentId += '_';
    currentId += part;
    const foundNode = findNodeById(treeData, currentId);
    if (foundNode) {
      const isLast = currentId === node.id;
      if (isLast) {
        html += `<span class="sep">›</span><span class="bc-btn current">${ICONS[foundNode.type]} ${foundNode.label}</span>`;
      } else {
        html += `<span class="sep">›</span><span class="bc-btn" onclick="navigateToNode('${currentId}')">${ICONS[foundNode.type]} ${foundNode.label}</span>`;
      }
    }
  }
  bc.innerHTML = html;
}

function updateAgingInfo(data) {
  const info = document.getElementById('agingInfo');
  const am = getAgingMonths();
  if (am !== '0' && data && data.total_aging_ratio !== undefined) {
    info.textContent = '(제조일자 기준 ' + am + '개월 이상 장기재고 비율: ' + data.total_aging_ratio + '%)';
    info.style.color = data.total_aging_ratio >= 50 ? 'var(--yellow)' : 'var(--orange)';
  } else {
    info.textContent = '';
  }
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
  document.getElementById('breadcrumb').innerHTML = '<span class="bc-btn current">🏠 전체</span>';

  // Build virtual root node with all warehouses as children
  const rootNode = {
    id: 'ROOT', type: 'root', label: '전체',
    children: treeData,
    count: treeData.reduce((s, w) => s + w.count, 0)
  };
  lastSelectedNode = rootNode;

  // Show table view
  document.getElementById('viewTabs').style.display = 'flex';
  const content = document.getElementById('detailContent');
  const totalCount = rootNode.count;
  let html = `<div class="detail-title">🏠 전체 거점 재고 현황</div>`;
  html += `<div class="detail-subtitle">거점 ${treeData.length}개 | 총 지번 ${totalCount.toLocaleString()}개</div>`;
  html += `<table class="data-table"><thead><tr>`;
  html += `<th>#</th><th>거점</th><th>명칭</th><th>플랜트수</th><th>지번수</th><th>팔레트재고</th><th>Capa</th><th>적재율</th><th>장기재고 비율</th><th>분포</th>`;
  html += `</tr></thead><tbody>`;
  treeData.forEach((w, i) => {
    const code = extractCode(w.label);
    const pct = totalCount > 0 ? ((w.count / totalCount) * 100).toFixed(1) : 0;
    const barW = Math.max(2, Math.min(200, (w.count / totalCount) * 200));
    html += `<tr onclick="navigateToNode('${w.id}')" style="cursor:pointer">`;
    html += `<td style="color:var(--text-muted)">${i+1}</td>`;
    html += `<td class="clickable">📦 ${w.label}</td>`;
    html += `<td class="stock-name" data-code="${code}" style="color:var(--text-muted);font-size:12px;">-</td>`;
    html += `<td>${w.children ? w.children.length : '-'}</td>`;
    html += `<td><b>${w.count.toLocaleString()}</b></td>`;
    html += `<td class="stock-qty" data-code="${code}">-</td>`;
    html += `<td class="stock-capa" data-code="${code}">-</td>`;
    html += `<td class="stock-usage" data-code="${code}">-</td>`;
    html += `<td class="stock-aging" data-code="${code}">-</td>`;
    html += `<td><div style="display:flex;align-items:center;gap:8px;"><div style="width:${barW}px;height:6px;background:var(--accent);border-radius:3px;"></div><span style="font-size:11px;color:var(--text-muted)">${pct}%</span></div></td>`;
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  content.innerHTML = html;

  // Load warehouse-level heatmap
  loadWarehouseHeatmap();
  switchView(currentView);
}

async function loadWarehouseHeatmap() {
  const params = { level: 'warehouse', aging_months: getAgingMonths() };
  const qs = new URLSearchParams(params).toString();
  try {
    const resp = await fetch(`/api/hierarchy/stock?${qs}`);
    const data = await resp.json();

    // Map nodeIds for click navigation
    data.items.forEach(item => {
      const w = treeData.find(c => c.label === item.label || c.label.startsWith(item.label + ' '));
      if (w) item.nodeId = w.id;
    });

    document.getElementById('heatmapContainer').style.display = currentView === 'heatmap' ? 'flex' : 'none';
    buildHeatmap(data.items, data.total_qty, 'warehouse');
    updateAgingInfo(data);

    // Update table cells
    data.items.forEach(item => {
      const code = item.label;
      const nameCells = document.querySelectorAll(`.stock-name[data-code="${code}"]`);
      nameCells.forEach(cell => { cell.textContent = item.name || '-'; cell.style.color = item.name ? 'var(--text-secondary)' : 'var(--text-muted)'; });
      document.querySelectorAll(`.stock-qty[data-code="${code}"]`).forEach(cell => { cell.textContent = formatNumber(item.qty); cell.style.color = 'var(--yellow)'; cell.style.fontWeight = '600'; });
      document.querySelectorAll(`.stock-capa[data-code="${code}"]`).forEach(cell => { cell.textContent = formatNumber(item.maxcpc || 0); cell.style.color = 'var(--green)'; });
      document.querySelectorAll(`.stock-usage[data-code="${code}"]`).forEach(cell => { const u = item.usage || 0; cell.textContent = u.toFixed(1) + '%'; cell.style.fontWeight = '600'; cell.style.color = u > 100 ? 'var(--red)' : u > 80 ? 'var(--orange)' : 'var(--green)'; });
      document.querySelectorAll(`.stock-aging[data-code="${code}"]`).forEach(cell => {
        const am = getAgingMonths();
        if (am !== '0') { const ar = item.aging_ratio || 0; cell.textContent = ar.toFixed(1) + '%'; cell.style.fontWeight = '600'; cell.style.color = ar >= 50 ? 'var(--yellow)' : ar >= 30 ? 'var(--orange)' : ar > 0 ? 'var(--text-secondary)' : 'var(--text-muted)'; }
        else { cell.textContent = '-'; cell.style.color = 'var(--text-muted)'; }
      });
    });
  } catch(e) { console.error('Failed to load warehouse stock:', e); }
}

function showWelcomeOld() {
  /* kept for reference - original welcome screen */
  document.querySelectorAll('.tree-row.selected').forEach(r => r.classList.remove('selected'));
  document.getElementById('breadcrumb').innerHTML = '<span class="bc-btn current">🏠 전체 구조</span>';
  document.getElementById('agingInfo').textContent = '';
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
    const newW = Math.max(280, Math.min(800, w));
    panel.style.width = newW + 'px';
    const btn = document.getElementById('treePanelToggle');
    if (btn) btn.style.left = newW + 'px';
  }

  function onStop() {
    handle.classList.remove('active');
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', onStop);
  }
})();

// ========================
// Tree Panel Toggle
// ========================
let treePanelVisible = false;
function toggleTreePanel() {
  const panel = document.getElementById('treePanel');
  const handle = document.getElementById('resizeHandle');
  const btn = document.getElementById('treePanelToggle');
  treePanelVisible = !treePanelVisible;
  if (treePanelVisible) {
    panel.classList.remove('collapsed');
    panel.style.width = (panel._savedWidth || 420) + 'px';
    handle.classList.remove('collapsed');
    btn.classList.remove('collapsed');
    btn.title = '트리 패널 숨기기';
  } else {
    panel._savedWidth = panel.offsetWidth;
    panel.classList.add('collapsed');
    handle.classList.add('collapsed');
    btn.classList.add('collapsed');
    btn.title = '트리 패널 보이기';
  }
  // Update toggle button position
  setTimeout(() => {
    if (treePanelVisible) {
      btn.style.left = panel.offsetWidth + 'px';
    } else {
      btn.style.left = '0px';
    }
  }, 310);
}
// Position the toggle button on load
window.addEventListener('load', () => {
  const btn = document.getElementById('treePanelToggle');
  btn.style.left = '0px';
});

// ========================
// Init
// ========================
loadTree();
</script>
</body>
</html>
"""


AGING_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>출고 제품 연령 분석 | Outbound Aging Analysis</title>
<style>
:root {
  --bg-primary: #080d1a;
  --bg-secondary: #0e1529;
  --bg-tertiary: #141d35;
  --border: rgba(120,160,255,0.1);
  --text-primary: #edf0f7;
  --text-secondary: #a0b0d0;
  --text-muted: #5a6d8e;
  --accent: #6ea8fe;
  --accent-dark: #4a8af0;
  --green: #34d399;
  --yellow: #fcd34d;
  --purple: #b197fc;
  --pink: #f472b6;
  --orange: #fdba74;
  --red: #fca5a5;
  --glass: rgba(14,21,41,0.7);
  --glass-border: rgba(120,160,255,0.08);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', -apple-system, sans-serif; background: var(--bg-primary); color: var(--text-primary); }

/* Header */
.header {
  background: linear-gradient(135deg, #0a1128 0%, #121d3a 50%, #162550 100%);
  padding: 16px 24px;
  border-bottom: 1px solid rgba(110,168,254,0.1);
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03);
}
.header h1 { font-size: 18px; background: linear-gradient(135deg, #6ea8fe, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; letter-spacing: 0.5px; }
.header .badge { font-size: 11px; padding: 4px 12px; border-radius: 6px; backdrop-filter: blur(8px); }
.header .b1 { background: rgba(110,168,254,0.12); color: var(--accent); border: 1px solid rgba(110,168,254,0.2); }
.header .b2 { background: rgba(160,176,208,0.08); color: var(--text-secondary); border: 1px solid rgba(160,176,208,0.1); }
.header a { color: var(--text-secondary); text-decoration: none; font-size: 13px; padding: 6px 16px; border-radius: 8px; background: rgba(110,168,254,0.08); border: 1px solid rgba(110,168,254,0.12); transition: all 0.2s; }
.header a:hover { color: var(--accent); background: rgba(110,168,254,0.18); border-color: rgba(110,168,254,0.3); }

/* Main layout */
.main-content { padding: 20px 24px; max-width: 1600px; margin: 0 auto; }

/* Filter bar */
.filter-bar {
  display: flex; align-items: flex-end; gap: 16px; flex-wrap: wrap;
  padding: 20px; margin-bottom: 20px;
  background: linear-gradient(135deg, rgba(14,21,41,0.9), rgba(20,29,53,0.85));
  border: 1px solid var(--glass-border); border-radius: 14px;
  backdrop-filter: blur(12px);
}
.filter-group { display: flex; flex-direction: column; gap: 6px; }
.filter-group label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.filter-group select, .filter-group input[type="month"] {
  padding: 8px 14px; border-radius: 8px;
  background: rgba(8,13,26,0.7); border: 1px solid var(--glass-border);
  color: var(--text-primary); font-size: 13px;
  transition: all 0.2s; cursor: pointer;
  min-width: 140px;
}
.filter-group select:focus, .filter-group input[type="month"]:focus {
  outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(110,168,254,0.15);
}
.filter-group input[type="month"]::-webkit-calendar-picker-indicator { filter: invert(0.7); cursor: pointer; }
.filter-bar .btn-search {
  padding: 8px 24px; border: none; border-radius: 8px;
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: #fff; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.25s; box-shadow: 0 4px 16px rgba(110,168,254,0.3);
}
.filter-bar .btn-search:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(110,168,254,0.4); }

/* Summary cards */
.summary-cards {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px; margin-bottom: 24px;
}
.summary-card {
  padding: 18px 20px; border-radius: 14px;
  background: linear-gradient(135deg, rgba(14,21,41,0.9), rgba(20,29,53,0.85));
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px);
  transition: all 0.25s;
}
.summary-card:hover { border-color: rgba(110,168,254,0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.summary-card .sc-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 600; }
.summary-card .sc-value { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.summary-card .sc-sub { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.summary-card.accent .sc-value { background: linear-gradient(135deg, var(--accent), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.summary-card.green .sc-value { color: var(--green); }
.summary-card.orange .sc-value { color: var(--orange); }
.summary-card.pink .sc-value { color: var(--pink); }

/* Section titles */
.section-title {
  font-size: 16px; font-weight: 700; margin-bottom: 16px; padding-bottom: 8px;
  border-bottom: 1px solid var(--glass-border);
  background: linear-gradient(90deg, var(--accent), var(--purple));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* Chart container */
.chart-section {
  background: linear-gradient(135deg, rgba(14,21,41,0.9), rgba(20,29,53,0.85));
  border: 1px solid var(--glass-border); border-radius: 14px;
  backdrop-filter: blur(12px); padding: 20px; margin-bottom: 24px;
}

/* Bar chart (CSS-only) */
.bar-chart { display: flex; align-items: flex-end; gap: 4px; height: 220px; padding: 0 10px; }
.bar-group { display: flex; flex-direction: column; align-items: center; flex: 1; gap: 4px; }
.bar-stack { display: flex; flex-direction: column; justify-content: flex-end; width: 100%; height: 200px; border-radius: 6px 6px 0 0; overflow: hidden; position: relative; }
.bar-segment { width: 100%; transition: height 0.6s ease; min-height: 1px; cursor: pointer; position: relative; }
.bar-segment:hover { filter: brightness(1.3); }
.bar-label { font-size: 11px; color: var(--text-muted); text-align: center; white-space: nowrap; }
.bar-value { font-size: 11px; color: var(--text-secondary); text-align: center; font-weight: 600; }

/* Aging distribution chart */
.aging-chart { width: 100%; }
.aging-month-row {
  display: flex; align-items: center; gap: 12px; margin-bottom: 10px; padding: 8px 12px;
  background: rgba(8,13,26,0.4); border-radius: 10px; border: 1px solid rgba(120,160,255,0.05);
  transition: all 0.2s;
}
.aging-month-row:hover { background: rgba(110,168,254,0.06); border-color: rgba(110,168,254,0.12); }
.aging-month-label { width: 80px; font-size: 13px; font-weight: 600; color: var(--text-secondary); flex-shrink: 0; }
.aging-bar-container { flex: 1; height: 32px; display: flex; border-radius: 6px; overflow: hidden; background: rgba(8,13,26,0.5); }
.aging-bar-seg {
  height: 100%; display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.9);
  transition: width 0.6s ease; cursor: pointer; position: relative;
  min-width: 0;
}
.aging-bar-seg:hover { filter: brightness(1.2); z-index: 1; }
.aging-bar-seg span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 4px; }
.aging-avg { width: 90px; text-align: right; font-size: 13px; font-weight: 700; color: var(--text-primary); flex-shrink: 0; }
.aging-count { width: 70px; text-align: right; font-size: 12px; color: var(--text-muted); flex-shrink: 0; }

/* Aging bucket colors */
.bucket-0-7   { background: #22c55e; }
.bucket-8-14  { background: #4ade80; }
.bucket-15-30 { background: #a3e635; }
.bucket-31-60 { background: #facc15; }
.bucket-61-90 { background: #fb923c; }
.bucket-91-180 { background: #f87171; }
.bucket-181-365 { background: #dc2626; }
.bucket-365p  { background: #991b1b; }

/* Legend */
.aging-legend {
  display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; padding-top: 12px;
  border-top: 1px solid var(--glass-border);
}
.aging-legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); }
.aging-legend-dot { width: 14px; height: 14px; border-radius: 4px; flex-shrink: 0; }

/* Qty table */
.qty-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.qty-table th {
  background: var(--bg-secondary); color: var(--text-secondary); font-weight: 600;
  text-align: left; padding: 10px 14px; border-bottom: 2px solid var(--border);
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
  position: sticky; top: 0; z-index: 2;
}
.qty-table td { padding: 10px 14px; border-bottom: 1px solid var(--glass-border); }
.qty-table tr:hover td { background: rgba(110,168,254,0.04); }
.qty-table .num { text-align: right; font-variant-numeric: tabular-nums; font-weight: 500; }

/* Detail table */
.detail-table-wrap { max-height: 500px; overflow-y: auto; border-radius: 10px; border: 1px solid var(--glass-border); }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.detail-table th {
  background: var(--bg-secondary); color: var(--text-secondary); font-weight: 600;
  text-align: left; padding: 8px 12px; border-bottom: 2px solid var(--border);
  font-size: 11px; text-transform: uppercase; position: sticky; top: 0; z-index: 2;
}
.detail-table td { padding: 7px 12px; border-bottom: 1px solid var(--glass-border); }
.detail-table tr:hover td { background: rgba(110,168,254,0.04); }

/* Days badge */
.days-badge {
  display: inline-block; padding: 2px 10px; border-radius: 10px;
  font-size: 11px; font-weight: 700;
}
.days-badge.fresh { background: rgba(34,197,94,0.15); color: #34d399; }
.days-badge.normal { background: rgba(250,204,21,0.15); color: #fcd34d; }
.days-badge.aged { background: rgba(248,113,113,0.15); color: #fca5a5; }
.days-badge.old { background: rgba(153,27,27,0.2); color: #fca5a5; }

/* Pagination */
.pagination { display: flex; align-items: center; gap: 10px; padding: 12px 0; justify-content: center; }
.pagination button {
  padding: 6px 16px; border: 1px solid var(--glass-border); border-radius: 6px;
  background: rgba(14,21,41,0.7); color: var(--text-secondary); cursor: pointer;
  font-size: 12px; transition: all 0.2s;
}
.pagination button:hover:not(:disabled) { background: rgba(110,168,254,0.12); color: var(--accent); border-color: rgba(110,168,254,0.3); }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.pagination .page-info { font-size: 12px; color: var(--text-muted); }

/* Tabs */
.view-tabs { display: flex; gap: 4px; margin-bottom: 20px; }
.view-tab {
  padding: 8px 20px; border: 1px solid var(--glass-border); border-radius: 8px;
  background: transparent; color: var(--text-muted); cursor: pointer;
  font-size: 13px; font-weight: 500; transition: all 0.2s;
}
.view-tab:hover { color: var(--text-secondary); background: rgba(110,168,254,0.06); }
.view-tab.active {
  background: linear-gradient(135deg, rgba(110,168,254,0.2), rgba(167,139,250,0.12));
  color: var(--accent); border-color: rgba(110,168,254,0.35); font-weight: 600;
}

/* Loading */
.loading { text-align: center; padding: 60px; color: var(--text-muted); font-size: 14px; }
.loading::after { content: ''; display: inline-block; width: 20px; height: 20px; border: 2px solid var(--glass-border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-left: 10px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 768px) {
  .filter-bar { flex-direction: column; align-items: stretch; }
  .summary-cards { grid-template-columns: repeat(2, 1fr); }
  .aging-month-label { width: 60px; font-size: 11px; }
  .aging-avg { width: 60px; font-size: 11px; }
  .aging-count { width: 50px; font-size: 10px; }
}
</style>
</head>
<body>

<div class="header">
  <h1>출고 제품 연령 분석</h1>
  <span class="badge b1">Outbound Aging Analysis</span>
  <span class="badge b2">재고일수 = 실제완료일 − 제조일자</span>
  <div style="margin-left:auto;display:flex;gap:8px;">
    <a href="/">← DB Viewer</a>
    <a href="/structure">📦 구조 조회</a>
  </div>
</div>

<div class="main-content">
  <!-- Filters -->
  <div class="filter-bar">
    <div class="filter-group">
      <label>조회 시작월</label>
      <input type="month" id="filterFrom">
    </div>
    <div class="filter-group">
      <label>조회 종료월</label>
      <input type="month" id="filterTo">
    </div>
    <div class="filter-group">
      <label>플랜트</label>
      <select id="filterPlant"><option value="">전체</option></select>
    </div>
    <div class="filter-group">
      <label>창고 (영역)</label>
      <select id="filterWarehouse"><option value="">전체</option></select>
    </div>
    <button class="btn-search" onclick="doSearch()">🔍 조회</button>
  </div>

  <!-- Summary cards -->
  <div class="summary-cards" id="summaryCards">
    <div class="summary-card accent"><div class="sc-label">총 출고 건수</div><div class="sc-value" id="scTotal">-</div><div class="sc-sub" id="scTotalSub">조회 후 표시</div></div>
    <div class="summary-card green"><div class="sc-label">평균 재고일수</div><div class="sc-value" id="scAvgDays">-</div><div class="sc-sub" id="scAvgSub">전체 기간</div></div>
    <div class="summary-card orange"><div class="sc-label">총 출고 수량</div><div class="sc-value" id="scQty">-</div><div class="sc-sub" id="scQtySub">단위별 합계</div></div>
    <div class="summary-card pink"><div class="sc-label">장기재고 비율 (90일+)</div><div class="sc-value" id="scLong">-</div><div class="sc-sub" id="scLongSub">90일 초과 비율</div></div>
  </div>

  <!-- Tabs -->
  <div class="view-tabs">
    <button class="view-tab active" onclick="switchTab('aging')">📊 재고일수 분포</button>
    <button class="view-tab" onclick="switchTab('qty')">📦 월별 출고 수량</button>
    <button class="view-tab" onclick="switchTab('detail')">📋 상세 데이터</button>
  </div>

  <!-- Tab: Aging distribution -->
  <div class="tab-content" id="tabAging">
    <div class="chart-section">
      <div class="section-title">월별 재고일수 분포 (재고일수 = 실제완료일 − 제조일자)</div>
      <div id="agingChart" class="aging-chart"><div class="loading">데이터 로딩 중</div></div>
      <div class="aging-legend" id="agingLegend"></div>
    </div>
  </div>

  <!-- Tab: Monthly qty -->
  <div class="tab-content" id="tabQty" style="display:none;">
    <div class="chart-section">
      <div class="section-title">월별 출고 수량 (단위별)</div>
      <div id="qtyContent"><div class="loading">데이터 로딩 중</div></div>
    </div>
  </div>

  <!-- Tab: Detail data -->
  <div class="tab-content" id="tabDetail" style="display:none;">
    <div class="chart-section">
      <div class="section-title">출고 상세 데이터</div>
      <div id="detailContent"><div class="loading">데이터 로딩 중</div></div>
      <div class="pagination" id="detailPagination"></div>
    </div>
  </div>
</div>

<script>
// State
let summaryData = null;
let detailPage = 0;
const bucketLabels = {
  '0-7': '0~7일', '8-14': '8~14일', '15-30': '15~30일', '31-60': '31~60일',
  '61-90': '61~90일', '91-180': '91~180일', '181-365': '181~365일', '365+': '365일+'
};
const bucketClasses = {
  '0-7': 'bucket-0-7', '8-14': 'bucket-8-14', '15-30': 'bucket-15-30',
  '31-60': 'bucket-31-60', '61-90': 'bucket-61-90', '91-180': 'bucket-91-180',
  '181-365': 'bucket-181-365', '365+': 'bucket-365p'
};
const bucketColors = {
  '0-7': '#22c55e', '8-14': '#4ade80', '15-30': '#a3e635', '31-60': '#facc15',
  '61-90': '#fb923c', '91-180': '#f87171', '181-365': '#dc2626', '365+': '#991b1b'
};

function formatMonth(ym) {
  if (!ym || ym.length < 6) return ym;
  return ym.substring(0,4) + '.' + ym.substring(4,6);
}
function fmt(n) {
  if (n == null) return '-';
  return Number(n).toLocaleString('ko-KR', {maximumFractionDigits: 1});
}
function fmtDate(d) {
  if (!d || d.length < 8) return d;
  return d.substring(0,4) + '-' + d.substring(4,6) + '-' + d.substring(6,8);
}

// Init: set default month values
function initFilters() {
  const now = new Date();
  const ym = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0');
  // Data range is 202506~202508
  document.getElementById('filterFrom').value = '2025-06';
  document.getElementById('filterTo').value = '2025-08';
  // Load initial data
  doSearch();
}

// Fetch summary data
async function doSearch() {
  const fromVal = document.getElementById('filterFrom').value; // YYYY-MM
  const toVal = document.getElementById('filterTo').value;
  const plant = document.getElementById('filterPlant').value;
  const wh = document.getElementById('filterWarehouse').value;

  const fromYM = fromVal ? fromVal.replace('-','') : '';
  const toYM = toVal ? toVal.replace('-','') : '';

  const params = new URLSearchParams();
  if (fromYM) params.set('from', fromYM);
  if (toYM) params.set('to', toYM);
  if (plant) params.set('plant', plant);
  if (wh) params.set('warehouse', wh);

  // Show loading
  document.getElementById('agingChart').innerHTML = '<div class="loading">데이터 로딩 중</div>';
  document.getElementById('qtyContent').innerHTML = '<div class="loading">데이터 로딩 중</div>';

  try {
    const res = await fetch('/api/aging/summary?' + params.toString());
    summaryData = await res.json();
    renderFilters(summaryData);
    renderSummaryCards(summaryData);
    renderAgingChart(summaryData);
    renderQtyTable(summaryData);
    // Reset detail page
    detailPage = 0;
    loadDetail();
  } catch(e) {
    console.error(e);
    document.getElementById('agingChart').innerHTML = '<div class="loading">오류 발생: ' + e.message + '</div>';
  }
}

function renderFilters(data) {
  const plantSel = document.getElementById('filterPlant');
  const whSel = document.getElementById('filterWarehouse');
  const curPlant = plantSel.value;
  const curWh = whSel.value;

  // Plants
  let html = '<option value="">전체</option>';
  (data.plants || []).forEach(p => {
    html += '<option value="' + p.code + '"' + (p.code === curPlant ? ' selected' : '') + '>' + p.code + ' (' + p.name + ')</option>';
  });
  plantSel.innerHTML = html;

  // Warehouses
  html = '<option value="">전체</option>';
  (data.warehouses || []).forEach(w => {
    html += '<option value="' + w + '"' + (w === curWh ? ' selected' : '') + '>' + w + '</option>';
  });
  whSel.innerHTML = html;
}

function renderSummaryCards(data) {
  const aging = data.monthly_aging || {};
  const qty = data.monthly_qty || {};

  // Total records & avg days
  let totalCnt = 0, totalDays = 0, totalDayCnt = 0;
  let longCnt = 0; // 90+ days
  Object.values(aging).forEach(m => {
    totalCnt += m.total_cnt || 0;
    totalDays += (m.avg_days || 0) * (m.total_cnt || 0);
    totalDayCnt += m.total_cnt || 0;
    ['91-180','181-365','365+'].forEach(b => { longCnt += (m[b] && m[b].cnt) || 0; });
  });
  const avgDays = totalDayCnt > 0 ? (totalDays / totalDayCnt).toFixed(1) : 0;

  document.getElementById('scTotal').textContent = fmt(totalCnt);
  document.getElementById('scTotalSub').textContent = Object.keys(aging).length + '개월 데이터';

  document.getElementById('scAvgDays').textContent = avgDays + '일';
  document.getElementById('scAvgSub').textContent = '전체 출고 건 기준';

  // Total qty by UOM
  let totalQtyMap = {};
  Object.values(qty).forEach(mq => {
    Object.entries(mq).forEach(([uom, v]) => {
      if (!totalQtyMap[uom]) totalQtyMap[uom] = 0;
      totalQtyMap[uom] += v.qty || 0;
    });
  });
  const qtyParts = Object.entries(totalQtyMap).map(([u, q]) => fmt(q) + ' ' + u);
  document.getElementById('scQty').textContent = qtyParts.length > 0 ? qtyParts[0] : '-';
  document.getElementById('scQtySub').textContent = qtyParts.length > 1 ? qtyParts.slice(1).join(', ') : '총 출고수량';

  // Long-term ratio
  const longRatio = totalCnt > 0 ? (longCnt / totalCnt * 100).toFixed(1) : 0;
  document.getElementById('scLong').textContent = longRatio + '%';
  document.getElementById('scLongSub').textContent = fmt(longCnt) + '건 / ' + fmt(totalCnt) + '건';
}

function renderAgingChart(data) {
  const aging = data.monthly_aging || {};
  const buckets = data.bucket_keys || Object.keys(bucketLabels);
  const container = document.getElementById('agingChart');
  const legend = document.getElementById('agingLegend');

  const months = Object.keys(aging).sort();
  if (months.length === 0) {
    container.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:40px;">조회 결과가 없습니다.</div>';
    return;
  }

  let html = '';
  months.forEach(m => {
    const mData = aging[m];
    const totalCnt = mData.total_cnt || 0;
    const avgDays = mData.avg_days || 0;

    html += '<div class="aging-month-row">';
    html += '<div class="aging-month-label">' + formatMonth(m) + '</div>';
    html += '<div class="aging-bar-container">';

    buckets.forEach(b => {
      const bData = mData[b] || {cnt: 0, qty: 0};
      const pct = totalCnt > 0 ? (bData.cnt / totalCnt * 100) : 0;
      if (pct > 0) {
        const cls = bucketClasses[b] || '';
        const label = pct >= 8 ? bData.cnt + '건 (' + pct.toFixed(0) + '%)' : (pct >= 4 ? pct.toFixed(0) + '%' : '');
        html += '<div class="aging-bar-seg ' + cls + '" style="width:' + pct.toFixed(2) + '%" title="' + bucketLabels[b] + ': ' + bData.cnt + '건 (' + pct.toFixed(1) + '%), 수량: ' + fmt(bData.qty) + '">';
        html += '<span>' + label + '</span>';
        html += '</div>';
      }
    });

    html += '</div>';
    html += '<div class="aging-avg">평균 ' + avgDays + '일</div>';
    html += '<div class="aging-count">' + fmt(totalCnt) + '건</div>';
    html += '</div>';
  });

  container.innerHTML = html;

  // Legend
  let legHtml = '';
  buckets.forEach(b => {
    legHtml += '<div class="aging-legend-item"><div class="aging-legend-dot" style="background:' + bucketColors[b] + '"></div>' + bucketLabels[b] + '</div>';
  });
  legend.innerHTML = legHtml;
}

function renderQtyTable(data) {
  const qty = data.monthly_qty || {};
  const container = document.getElementById('qtyContent');
  const months = Object.keys(qty).sort();

  if (months.length === 0) {
    container.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:40px;">조회 결과가 없습니다.</div>';
    return;
  }

  // Collect all UOMs
  const uomSet = new Set();
  months.forEach(m => Object.keys(qty[m]).forEach(u => uomSet.add(u)));
  const uoms = Array.from(uomSet).sort();

  let html = '<table class="qty-table"><thead><tr><th>월</th>';
  uoms.forEach(u => {
    html += '<th class="num">수량 (' + u + ')</th><th class="num">건수 (' + u + ')</th>';
  });
  html += '<th class="num">총 건수</th></tr></thead><tbody>';

  let grandTotal = {};
  uoms.forEach(u => { grandTotal[u] = {qty: 0, cnt: 0}; });
  let grandCnt = 0;

  months.forEach(m => {
    html += '<tr><td style="font-weight:600;">' + formatMonth(m) + '</td>';
    let mTotal = 0;
    uoms.forEach(u => {
      const d = qty[m][u] || {qty: 0, cnt: 0};
      html += '<td class="num">' + fmt(d.qty) + '</td>';
      html += '<td class="num">' + fmt(d.cnt) + '</td>';
      grandTotal[u].qty += d.qty;
      grandTotal[u].cnt += d.cnt;
      mTotal += d.cnt;
    });
    grandCnt += mTotal;
    html += '<td class="num" style="font-weight:700;">' + fmt(mTotal) + '</td>';
    html += '</tr>';
  });

  // Grand total row
  html += '<tr style="background:rgba(110,168,254,0.08);font-weight:700;"><td>합계</td>';
  uoms.forEach(u => {
    html += '<td class="num">' + fmt(grandTotal[u].qty) + '</td>';
    html += '<td class="num">' + fmt(grandTotal[u].cnt) + '</td>';
  });
  html += '<td class="num">' + fmt(grandCnt) + '</td>';
  html += '</tr></tbody></table>';

  container.innerHTML = html;
}

// Detail
async function loadDetail() {
  const fromVal = document.getElementById('filterFrom').value;
  const toVal = document.getElementById('filterTo').value;
  const plant = document.getElementById('filterPlant').value;
  const wh = document.getElementById('filterWarehouse').value;

  const params = new URLSearchParams();
  if (fromVal) params.set('from', fromVal.replace('-',''));
  if (toVal) params.set('to', toVal.replace('-',''));
  if (plant) params.set('plant', plant);
  if (wh) params.set('warehouse', wh);
  params.set('page', detailPage);
  params.set('page_size', 50);

  const container = document.getElementById('detailContent');
  container.innerHTML = '<div class="loading">데이터 로딩 중</div>';

  try {
    const res = await fetch('/api/aging/detail?' + params.toString());
    const data = await res.json();
    renderDetail(data);
  } catch(e) {
    container.innerHTML = '<div style="color:var(--red);padding:20px;">오류: ' + e.message + '</div>';
  }
}

function daysBadgeClass(days) {
  if (days == null) return '';
  if (days <= 14) return 'fresh';
  if (days <= 60) return 'normal';
  if (days <= 180) return 'aged';
  return 'old';
}

function renderDetail(data) {
  const container = document.getElementById('detailContent');
  const rows = data.rows || [];
  const total = data.total || 0;

  if (rows.length === 0) {
    container.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:40px;">조회 결과가 없습니다.</div>';
    document.getElementById('detailPagination').innerHTML = '';
    return;
  }

  let html = '<div class="detail-table-wrap"><table class="detail-table">';
  html += '<thead><tr>';
  html += '<th>실제완료일</th><th>제조일자</th><th>재고일수</th><th>플랜트</th><th>창고</th>';
  html += '<th>SKU</th><th>품명</th><th>수량</th><th>단위</th>';
  html += '</tr></thead><tbody>';

  rows.forEach(r => {
    const bc = daysBadgeClass(r.days);
    html += '<tr>';
    html += '<td>' + fmtDate(r.act_date) + '</td>';
    html += '<td>' + fmtDate(r.mfg_date) + '</td>';
    html += '<td><span class="days-badge ' + bc + '">' + (r.days != null ? r.days + '일' : '-') + '</span></td>';
    html += '<td>' + (r.plant || '') + ' <span style="color:var(--text-muted);font-size:11px;">' + (r.plant_name || '') + '</span></td>';
    html += '<td>' + (r.warehouse || '') + '</td>';
    html += '<td style="font-size:11px;">' + (r.sku || '') + '</td>';
    html += '<td>' + (r.desc || '') + '</td>';
    html += '<td class="num">' + fmt(r.qty) + '</td>';
    html += '<td>' + (r.uom || '') + '</td>';
    html += '</tr>';
  });

  html += '</tbody></table></div>';
  container.innerHTML = html;

  // Pagination
  const pageSize = data.page_size || 50;
  const totalPages = Math.ceil(total / pageSize);
  const curPage = data.page || 0;
  let pgHtml = '';
  pgHtml += '<button ' + (curPage <= 0 ? 'disabled' : '') + ' onclick="detailPage=0;loadDetail();">◀◀</button>';
  pgHtml += '<button ' + (curPage <= 0 ? 'disabled' : '') + ' onclick="detailPage--;loadDetail();">◀</button>';
  pgHtml += '<span class="page-info">' + (curPage+1) + ' / ' + totalPages + ' (' + fmt(total) + '건)</span>';
  pgHtml += '<button ' + (curPage >= totalPages-1 ? 'disabled' : '') + ' onclick="detailPage++;loadDetail();">▶</button>';
  pgHtml += '<button ' + (curPage >= totalPages-1 ? 'disabled' : '') + ' onclick="detailPage=' + (totalPages-1) + ';loadDetail();">▶▶</button>';
  document.getElementById('detailPagination').innerHTML = pgHtml;
}

// Tab switching
function switchTab(tab) {
  document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.view-tab').forEach(el => el.classList.remove('active'));

  if (tab === 'aging') {
    document.getElementById('tabAging').style.display = 'block';
    document.querySelectorAll('.view-tab')[0].classList.add('active');
  } else if (tab === 'qty') {
    document.getElementById('tabQty').style.display = 'block';
    document.querySelectorAll('.view-tab')[1].classList.add('active');
  } else if (tab === 'detail') {
    document.getElementById('tabDetail').style.display = 'block';
    document.querySelectorAll('.view-tab')[2].classList.add('active');
    if (!document.getElementById('detailContent').querySelector('table')) {
      loadDetail();
    }
  }
}

// Plant filter change => refresh warehouses
document.getElementById('filterPlant').addEventListener('change', function() {
  // Re-fetch to update warehouse list
  doSearch();
});

// Init
initFilters();
</script>
</body>
</html>
"""


if __name__ == '__main__':
    print(f"DB path: {DB_PATH}")
    print(f"Starting DB Viewer on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
