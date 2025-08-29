import { useEffect, useMemo, useState } from "react";
import { fetchReport, exportReport } from "../services/api";
import { Link } from "react-router-dom";

type ReportKind = "hyperv"|"exchange"|"s3"|"summary";

function Table({ rows }: { rows: Array<Record<string, any>> }) {
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    if (!q) return rows;
    const s = q.toLowerCase();
    return rows.filter(r => Object.values(r).some(v => String(v ?? "").toLowerCase().includes(s)));
  }, [rows, q]);

  return (
    <div>
      <input placeholder="Поиск..." value={q} onChange={e => setQ(e.target.value)} style={{ margin: "8px 0", padding: 8, width: "100%" }} />
      <div style={{ overflow: "auto", border: "1px solid #ddd", borderRadius: 8 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {["Наименование компании","БИН","Наименование услуги","Количество"].map(h => (
                <th key={h} style={{ textAlign: "left", borderBottom: "1px solid #eee", padding: 8 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, i) => (
              <tr key={i}>
                <td style={{ padding: 8, borderBottom: "1px solid #fafafa" }}>{r["Наименование компании"]}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #fafafa" }}>{r["БИН"]}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #fafafa" }}>{r["Наименование услуги"]}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #fafafa" }}>{r["Количество"]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Reports() {
  const [tab, setTab] = useState<ReportKind>("summary");
  const [rows, setRows] = useState<Array<Record<string, any>>>([]);
  const [loading, setLoading] = useState(false);
  const kinds: ReportKind[] = ["hyperv","exchange","s3","summary"];

  useEffect(() => {
    setLoading(true);
    fetchReport(tab).then(setRows).finally(() => setLoading(false));
  }, [tab]);

  return (
    <div style={{ maxWidth: 1100, margin: "24px auto", padding: "0 16px", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <h2 style={{ margin: 0 }}>Отчеты</h2>
          <div style={{ fontSize: 12, opacity: 0.7 }}>Таблицы с поиском и экспортом в Excel</div>
        </div>
        <Link to="/">← На главную</Link>
      </header>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {kinds.map(k => (
          <button key={k} onClick={() => setTab(k)} style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #ddd", background: tab===k ? "#efefef" : "#fff" }}>
            {k.toUpperCase()}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <button onClick={() => exportReport(tab)} style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #2a6", background: "#eaffea" }}>
          Экспорт в Excel
        </button>
      </div>

      {loading ? <div>Загрузка...</div> : <Table rows={rows} />}
    </div>
  );
}
