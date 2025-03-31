import React, { useEffect, useState, useMemo } from "react";
import { Card, CardContent, Typography } from "@mui/material";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

function MetricChart({ title, endpoint, label }) {
  const [data, setData] = useState([]);
  const [timestamps, setTimestamps] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const url = `http://100.127.13.111:5150${endpoint}`;
        const response = await fetch(url);
        const result = await response.json();

        // Agora usa a label como chave no JSON
        const value = result[label];
        const timestamp = new Date().toLocaleTimeString();

        if (value !== undefined) {
          setData((prevData) => [...prevData.slice(-590), value]);
          setTimestamps((prevTimestamps) => [...prevTimestamps.slice(-590), timestamp]);
        }
      } catch (error) {
        console.error(`Erro ao buscar métricas de ${title}:`, error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000); // 1 segundo
    return () => clearInterval(interval);
  }, [endpoint, label]);

  const chartData = useMemo(() => ({
    labels: timestamps,
    datasets: [
      {
        label: label,
        data: data,
        borderColor: "blue",
        backgroundColor: "rgba(0,0,255,0.1)",
        fill: true,
        tension: 0.2,
      },
    ],
  }), [data, timestamps, label]);

  return (
    <Card sx={{ width: 400, height: 350 }}>
      <CardContent>
        <Typography variant="h6">{title}</Typography>
        <div style={{ height: "250px" }}>
          <Line
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              elements: { point: { radius: 2 } },
              scales: { x: { display: true }, y: { display: true, beginAtZero: true } },
              animation: { duration: 0 },
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
}

export default MetricChart;
