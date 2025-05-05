import React, { useState, useEffect } from "react";
import {
  Button,
  Typography,
  Box,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import MetricChart from "../components/MetricChart.jsx";
import CombinedMetricsChart from "../components/CombinedMetricsChart.jsx";
import { Link } from "react-router-dom";
import { exportAllMetrics } from "../utils/exportMetrics.js";
import FullScreenChartModal from "../components/FullScreenChartModal";
import SaveIcon from '@mui/icons-material/Save';
import background from "../assets/hiaac.png"; // 


function App() {
  const [status, setStatus] = useState("");
  const [activeClients, setActiveClients] = useState(null);
  const [activeExporters, setActiveExporters] = useState(null);
  const [accuracyData, setAccuracyData] = useState(null);
  const [lossData, setLossData] = useState(null);
  const [exportFormat, setExportFormat] = useState("csv");
  const [openChartModal, setOpenChartModal] = useState(false);
  const [selectedChartData, setSelectedChartData] = useState(null);
  const [selectedChartTitle, setSelectedChartTitle] = useState("");
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

  const openChart = (data, title) => {
    setSelectedChartData(data);
    setSelectedChartTitle(title);
    setOpenChartModal(true);
  };

  const sendCommand = async (command) => {
    try {
      const response = await fetch(`http://100.127.13.111:5150/${command}`, {
        method: "POST",
      });
      if (!response.ok)
        throw new Error(`Erro no servidor: ${response.statusText}`);
      const data = await response.json();
      setStatus(data.message);

      if (command === "start") {
        setAccuracyData(null);
        setLossData(null);
      }
    } catch (error) {
      console.error("Erro ao enviar comando:", error);
      setStatus("Erro ao conectar ao servidor");
    }
  };

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [clientsRes, exportersRes] = await Promise.all([
          fetch("http://100.127.13.111:5150/metrics/clients"),
          fetch("http://100.127.13.111:5150/metrics/exporters"),
        ]);

        const clientsData = await clientsRes.json();
        const exportersData = await exportersRes.json();

        setActiveClients(clientsData.clients);
        setActiveExporters(exportersData.exporters);
      } catch (error) {
        console.error("Erro ao buscar status:", error);
        setActiveClients("Erro");
        setActiveExporters("Erro");
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Box
      height="100vh"
      width="100vw"
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      position="relative"
      sx={{
        backgroundImage: `url(${background})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <Box
              display="flex"
              flexDirection="column"
              justifyContent="center"
              alignItems="center"
              bgcolor="#7c889c"
              padding={4}
              borderRadius={2}
              boxShadow={3}
              width="70vw"
            >
        <Box textAlign="center" mt={2}>
          <Button
            variant="contained"
            color="success"
            component={Link}
            to="/"
            sx={{ mt: 2, mb: -1 }}
            >
              Voltar ao menu
            </Button>

          <Box mt={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => sendCommand("start")}
              sx={{ ml: 2, mb: -1}}
            > 
              Iniciar
            </Button>

            <Button
              variant="contained"
              color="warning"
              onClick={() => sendCommand("stop")}
              sx={{ ml: 2, mb: -1 }}
            >
              Parar
            </Button>
          </Box>

            <Typography variant="h6" mt={2} mb={-3} color="white">
              Status: {status}
            </Typography>
          </Box>

          {/* Linha 1: Gráficos Sistêmicos */}
          <Box
            display="flex"
            justifyContent="center"
            flexWrap="wrap"
            gap={4}
            mt={4}
          >
            <MetricChart title="Rede RX (bytes/s)" endpoint="/metrics/network/rx" label="rx" />
            <MetricChart title="Rede TX (bytes/s)" endpoint="/metrics/network/tx" label="tx" />
            <MetricChart title="CPU (%)" endpoint="/metrics/cpu" label="cpu" />
            <MetricChart title="Memória (%)" endpoint="/metrics/memory" label="memory" />
          </Box>

          {/* Linha 2: Gráficos Treino/Teste + Cards */}
          <Box
            display="flex"
            justifyContent="center"
            alignItems="flex-start"
            flexWrap="wrap"
            gap={4}
            mt={4}
          >
            {/* Gráficos */}
            <Box display="flex" flexWrap="wrap" gap={4}>
              <CombinedMetricsChart
                title="Accuracy - Train vs Test"
                metricKeyPrefix="accuracy"
                colorTrain="green"
                colorTest="orange"
                onDataUpdate={setAccuracyData}
                onClick={() => {
                  if (accuracyData) {
                    const chartData = {
                      labels: accuracyData.train.timestamps,
                      datasets: [
                        {
                          label: "Train",
                          data: accuracyData.train.data,
                          borderColor: "green",
                          backgroundColor: "rgba(0,255,0,0.1)",
                          fill: true,
                          tension: 0.3,
                        },
                        {
                          label: "Test",
                          data: accuracyData.test.data,
                          borderColor: "orange",
                          backgroundColor: "rgba(255,165,0,0.1)",
                          fill: true,
                          tension: 0.3,
                        },
                      ],
                    };
                    openChart(chartData, "Accuracy - Train vs Test");
                  }
                }}
              />

              <CombinedMetricsChart
                title="Loss - Train vs Test"
                metricKeyPrefix="loss"
                colorTrain="green"
                colorTest="orange"
                onDataUpdate={setLossData}
                onClick={() => {
                  if (lossData) {
                    const chartData = {
                      labels: lossData.train.timestamps,
                      datasets: [
                        {
                          label: "Train",
                          data: lossData.train.data,
                          borderColor: "purple",
                          backgroundColor: "rgba(128,0,128,0.1)",
                          fill: true,
                          tension: 0.3,
                        },
                        {
                          label: "Test",
                          data: lossData.test.data,
                          borderColor: "red",
                          backgroundColor: "rgba(255,0,0,0.1)",
                          fill: true,
                          tension: 0.3,
                        },
                      ],
                    };
                    openChart(chartData, "Loss - Train vs Test");
                  }
                }}
              />
            </Box>

            {/* Coluna com os dois cards */}
            <Box display="flex" flexDirection="column" gap={2}>
              <Box
                p={3}
                borderRadius="12px"
                minWidth="100px"
                height="50px"
                bgcolor="#FFFFFF"
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                boxShadow={3}
              >
                <Typography variant="h6" color="black">
                  Clientes Ativos
                </Typography>
                <Typography variant="h3" color="black">
                  {activeClients !== null ? activeClients : "0"}
                </Typography>
              </Box>

              <Box
                p={3}
                borderRadius="12px"
                minWidth="100px"
                height="50px"
                bgcolor="#FFFFFF"
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                boxShadow={3}
              >
                <Typography variant="h6" color="black">
                  Clientes Treinando
                </Typography>
                <Typography variant="h3" color="black">
                  {activeExporters !== null ? activeExporters : "0"}
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Botão de Exportação Condicional */}
          {accuracyData && lossData && (
            <Button
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              sx={{
                mt: 4,
                px: 2,
                py: 1,
                minWidth: "130px",
                height: "36px",
                borderRadius: "6px",
                backgroundColor: "#1e1e1e",
                color: "white",
                textTransform: "none",
                boxShadow: "0 3px 8px rgba(0,0,0,0.3)",
                transition: "all 0.2s ease-in-out",
                '&:hover': {
                  backgroundColor: "#333333",
                  transform: "scale(1.03)"
                }
              }}
              onClick={() => setExportDialogOpen(true)}
            >
              Exportar Métricas
            </Button>
          )}
        </Box>
      
        {/* Modal de Gráfico Expandido */}
        <FullScreenChartModal
          open={openChartModal}
          onClose={() => setOpenChartModal(false)}
          chartData={selectedChartData}
          title={selectedChartTitle}
        />

      {/* Modal de Exportação */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)}>
        <DialogTitle>Escolher formato de exportação</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel id="dialog-format-label">Formato</InputLabel>
            <Select
              labelId="dialog-format-label"
              value={exportFormat}
              label="Formato"
              onChange={(e) => setExportFormat(e.target.value)}
            >
              <MenuItem value="csv">CSV</MenuItem>
              <MenuItem value="json">JSON</MenuItem>
              <MenuItem value="xlsx">XLSX</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)} color="secondary">
            Cancelar
          </Button>
          <Button
            onClick={() => {
              exportAllMetrics(
                {
                  "Accuracy - Train": accuracyData.train,
                  "Accuracy - Test": accuracyData.test,
                  "Loss - Train": lossData.train,
                  "Loss - Test": lossData.test,
                },
                exportFormat
              );
              setExportDialogOpen(false);
            }}
            variant="contained"
            color="primary"
          >
            Exportar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;
