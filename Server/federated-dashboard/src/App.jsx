import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import AcompanharMetricas from "./pages/AcompanharMetricas.jsx";
import ConfigurarExperimento from "./pages/ConfigurarExperimento.jsx";
import ExperimentoPadrao from "./pages/ExperimentoPadrao.jsx";
import ConfigurarClientes from "./pages/ConfiguraClientes.jsx";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/metricas" element={<AcompanharMetricas />} />
        <Route path="/configurar" element={<ConfigurarExperimento />} />
        <Route path="/padrao" element={<ExperimentoPadrao />} />
        <Route path="/configurar-pis" element={<ConfigurarClientes />} />
      </Routes>
    </Router>
  );
}
