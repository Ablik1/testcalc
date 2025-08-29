import { useState } from "react";
import { uploadSingle, uploadMultiple } from "../services/api";
import { Link } from "react-router-dom";

type UploadStatus = "idle" | "uploading" | "done" | "error";

function DropZone(props: { label: string; onFiles: (files: FileList) => Promise<void>; accept?: string; multiple?: boolean }) {
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [msg, setMsg] = useState<string>("");

  const onChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setStatus("uploading");
    try {
      await props.onFiles(e.target.files);
      setStatus("done");
      setMsg("Готово");
    } catch (e: any) {
      setStatus("error");
      setMsg(e?.response?.data?.detail || e.message || "Ошибка");
    }
  };

  return (
    <div style={{ border: "2px dashed #888", borderRadius: 12, padding: 16, minHeight: 120, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
      <div>
        <div style={{ fontWeight: 700 }}>{props.label}</div>
        <div style={{ fontSize: 12, opacity: 0.7 }}>Перетащите .xlsx или выберите файл</div>
        {status !== "idle" && <div style={{ marginTop: 8, fontSize: 12 }}>
          Статус: {status} {msg && <>— {msg}</>}
        </div>}
      </div>
      <input type="file" accept={props.accept || ".xlsx"} multiple={props.multiple} onChange={onChange} />
    </div>
  );
}

export default function App() {
  const onHyperV = async (files: FileList) => {
    await uploadSingle("/api/upload/hyperv", files[0]);
  };
  const onExchange = async (files: FileList) => {
    await uploadSingle("/api/upload/exchange", files[0]);
  };
  const onS3 = async (files: FileList) => {
    await uploadSingle("/api/upload/s3", files[0]);
  };
  const onMapping = async (files: FileList) => {
    await uploadMultiple("/api/upload/bin-mapping", Array.from(files));
  };

  return (
    <div style={{ maxWidth: 1000, margin: "24px auto", padding: "0 16px", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <h1 style={{ fontSize: 24, margin: 0 }}>Cloud24 Resource Calculator</h1>
        <Link to="/reports">Перейти к отчетам →</Link>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <DropZone label="Загрузить Hyper‑V (hyper-v.xlsx)" onFiles={onHyperV} />
        <DropZone label="Загрузить Exchange (mail.xlsx)" onFiles={onExchange} />
        <DropZone label="Загрузить S3 (s3.xlsx)" onFiles={onS3} />
        <DropZone label="Загрузить BIN‑mapping (несколько .xlsx)" onFiles={onMapping} multiple />
      </div>

      <footer style={{ marginTop: 24, fontSize: 12, opacity: 0.7 }}>
        Требуется: .xlsx (openxml). Данные кешируются на стороне API до перезагрузки контейнера.
      </footer>
    </div>
  );
}
