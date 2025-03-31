// Server/federated-dashboard/src/utils/exportMetrics.js
import * as XLSX from "xlsx";

export function exportAllMetrics(metricsByType, format = "csv") {
  const rows = [];

  for (const [tipo, metric] of Object.entries(metricsByType)) {
    metric.timestamps.forEach((round, index) => {
      const valor = metric.data[index];
      if (valor !== undefined) {
        rows.push({ Round: round, Tipo: tipo, Valor: valor });
      }
    });
  }

  if (format === "csv") {
    const csv = convertToCSV(rows);
    downloadFile(csv, "metricas_federated_learning.csv", "text/csv;charset=utf-8;");
  } else if (format === "json") {
    const json = JSON.stringify(rows, null, 2);
    downloadFile(json, "metricas_federated_learning.json", "application/json");
  } else if (format === "xlsx") {
    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Métricas");
    const blob = workbookToBlob(workbook);
    downloadBlob(blob, "metricas_federated_learning.xlsx");
  }
}

function convertToCSV(rows) {
  const headers = Object.keys(rows[0]);
  const csv = [
    headers.join(","),
    ...rows.map((row) => headers.map((h) => row[h]).join(",")),
  ];
  return csv.join("\n");
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  downloadBlob(blob, filename);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function workbookToBlob(workbook) {
  const wbout = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
  return new Blob([wbout], { type: "application/octet-stream" });
}
