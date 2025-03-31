import React, { useEffect, useState, useMemo } from "react";
import { Line } from "react-chartjs-2";
import { Box, Typography, FormGroup, FormControlLabel, Checkbox, Button } from "@mui/material";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
} from "chart.js";

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Legend, Tooltip);

export default function CombinedMetricsChart({
  title,
  metricKeyPrefix,
  colorTrain,
  colorTest,
  onDataUpdate, 
  onClick,
}) {
  const [trainData, setTrainData] = useState([]);
  const [testData, setTestData] = useState([]);
  const [timestamps, setTimestamps] = useState([]);
  const [showTrain, setShowTrain] = useState(true);
  const [showTest, setShowTest] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("http://100.127.13.111:5150/metrics/prometheus/combined");
        const data = await res.json();

        const trainKey = `${metricKeyPrefix}_train`;
        const testKey = `${metricKeyPrefix}_test`;

        const train = averageMetricByRound(data, trainKey);
        const test = averageMetricByRound(data, testKey);

        setTrainData(train.averages);
        setTestData(test.averages);
        setTimestamps(train.rounds);

        // Envia dados ao componente pai
        if (onDataUpdate) {
          onDataUpdate({
            train: { data: train.averages, timestamps: train.rounds },
            test: { data: test.averages, timestamps: test.rounds },
          });
        }
      } catch (err) {
        console.error("Erro ao buscar métricas combinadas:", err);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10);
    return () => clearInterval(interval);
  }, [metricKeyPrefix]);

  // const handleDownload = () => {
  //   let csv = "Round,Tipo,Valor\n";

  //   timestamps.forEach((round, index) => {
  //     if (showTrain && trainData[index] !== undefined) {
  //       csv += `${round},Train,${trainData[index]}\n`;
  //     }
  //     if (showTest && testData[index] !== undefined) {
  //       csv += `${round},Test,${testData[index]}\n`;
  //     }
  //   });

  //   const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  //   const url = URL.createObjectURL(blob);

  //   const link = document.createElement("a");
  //   link.href = url;
  //   link.setAttribute("download", `${title.replace(/\s+/g, "_")}_metrics.csv`);
  //   document.body.appendChild(link);
  //   link.click();
  //   document.body.removeChild(link);
  // };

  const averageMetricByRound = (metrics, key) => {
    const grouped = {};

    metrics.forEach((item) => {
      const round = parseInt(item.round);
      if (!round || isNaN(round)) return;

      if (!grouped[round]) {
        grouped[round] = [];
      }

      const value = item[key];
      if (value !== undefined && value !== null) {
        grouped[round].push(value);
      }
    });

    const sortedRounds = Object.keys(grouped).sort((a, b) => parseInt(a) - parseInt(b));

    const rounds = [];
    const averages = [];

    sortedRounds.forEach((round) => {
      const values = grouped[round];
      const avg = values.reduce((acc, val) => acc + val, 0) / values.length;
      rounds.push(round);
      averages.push(avg);
    });

    return { rounds, averages };
  };

  const chartData = useMemo(() => {
    const datasets = [];

    if (showTrain) {
      datasets.push({
        label: "Train",
        data: trainData,
        borderColor: colorTrain,
        backgroundColor: "rgba(0,255,0,0.1)",
        fill: true,
        tension: 0.3,
      });
    }

    if (showTest) {
      datasets.push({
        label: "Test",
        data: testData,
        borderColor: colorTest,
        backgroundColor: "rgba(255,165,0,0.1)",
        fill: true,
        tension: 0.3,
      });
    }

    return {
      labels: timestamps,
      datasets,
    };
  }, [timestamps, trainData, testData, showTrain, showTest]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    elements: { point: { radius: 2 } },
    scales: {
      y: { beginAtZero: true },
      x: { display: true },
    },
    animation: { duration: 0 },
  };

  return (
    <Box
      p={3}
      borderRadius="12px"
      minWidth="400px"
      height="400px"
      bgcolor="#FFFFFF"
      display="flex"
      flexDirection="column"
      justifyContent="flex-start"
      alignItems="center"
      boxShadow={3}
    >
      <Typography variant="h6" color="black">{title}</Typography>

      <FormGroup row sx={{ mt: 1 }}>
        <FormControlLabel
          control={<Checkbox checked={showTrain} onChange={() => setShowTrain(!showTrain)} />}
          label="Train"
        />
        <FormControlLabel
          control={<Checkbox checked={showTest} onChange={() => setShowTest(!showTest)} />}
          label="Test"
        />
      </FormGroup>

      <div style={{ height: "250px", width: "100%" }}>
        <Line data={chartData} options={options} />
      </div>

      {/* <Button variant="outlined" onClick={handleDownload} sx={{ mt: 2 }}>
        Exportar CSV
      </Button> */}

      <Button
        variant="text"
        size="small"
        onClick={onClick}
        sx={{ alignSelf: "flex-end", mb: 1 }}
      >
        🔍 Expandir
      </Button>

    </Box>
  );
}
