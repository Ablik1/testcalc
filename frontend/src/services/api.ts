/// <reference types="vite/client" />
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8023";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export async function uploadSingle(endpoint: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  return api.post(endpoint, form, { headers: { "Content-Type": "multipart/form-data" } });
}

export async function uploadMultiple(endpoint: string, files: File[]) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  return api.post(endpoint, form, { headers: { "Content-Type": "multipart/form-data" } });
}

export async function fetchReport(type: "hyperv"|"exchange"|"s3"|"summary") {
  const { data } = await api.get(`/api/reports/${type}`);
  return data as Array<Record<string, any>>;
}

export function exportReport(type: "hyperv"|"exchange"|"s3"|"summary") {
  return api.get(`/api/export/${type}`, { responseType: "blob" }).then(res => {
    const blob = new Blob([res.data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${type}.xlsx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  });
}
