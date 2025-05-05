import { useState } from "react";

function ConfigIpPrompt() {
  const [ip, setIp] = useState(localStorage.getItem("serverIp") || "");

  const handleSave = () => {
    if (ip.startsWith("http://") || ip.startsWith("https://")) {
      localStorage.setItem("serverIp", ip);
      window.location.reload();
    } else {
      alert("Informe um IP com http:// ou https://");
    }
  };

  if (localStorage.getItem("serverIp")) return null;

  return (
    <div style={{ padding: 20, backgroundColor: "#eee" }}>
      <h3>🔧 Configure o IP do servidor:</h3>
      <input
        value={ip}
        onChange={(e) => setIp(e.target.value)}
        placeholder="ex: http://192.168.1.100:5150"
        style={{ padding: 8, width: 300 }}
      />
      <button onClick={handleSave} style={{ marginLeft: 10 }}>
        Salvar
      </button>
    </div>
  );
}

export default ConfigIpPrompt;