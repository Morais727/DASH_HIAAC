export function getApiUrl(path = "") {
    const baseIp = localStorage.getItem("serverIp") || "http://100.127.13.111:5150";
    return `${baseIp}${path.startsWith("/") ? path : `/${path}`}`;
  }