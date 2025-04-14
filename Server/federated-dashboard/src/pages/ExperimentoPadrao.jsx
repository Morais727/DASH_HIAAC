import React, { useState } from "react";
import {
  Box,
  Button,
  MenuItem,
  Typography,
  Select,
  FormControl,
  InputLabel,
  TextField,
  Switch,
  FormControlLabel,
  Grid,
  Alert
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import background from "../assets/hiaac.png"; // 

export default function RodarExperimento() {
  const [modelo, setModelo] = useState("DNN");
  const [dataset, setDataset] = useState("MNIST");
  const [nonIID, setNonIID] = useState(false);
  const [dirichletAlpha, setDirichletAlpha] = useState(0.5);
  const [numClients, setNumClients] = useState(2);
  const [numRounds, setRounds] = useState(3);
  const [epochs, setEpochs] = useState(10);
  const [batchSize, setBatchSize] = useState(32);
  const [status, setStatus] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (
      epochs < 1 || epochs > 100 ||
      batchSize < 1 || batchSize > 1024 ||
      numClients < 1 || numClients > 100 ||
      numRounds < 1 || numRounds > 1000 ||
      (nonIID && (dirichletAlpha < 0.01 || dirichletAlpha > 1))
    ) {
      setStatus("❌ Valores inválidos: verifique os limites.");
      return;
    }

    const clientEnv = `
      MODEL_TYPE=${modelo}
      EPOCHS=${epochs}
      BATCH_SIZE=${batchSize}
      DATASET=${dataset}
      NON_IID=${nonIID}
      NUM_CLIENTS=${numClients}
      ${nonIID ? `DIRICHLET_ALPHA=${dirichletAlpha}` : ""}
    `;

    const serverEnv = `
      NUM_ROUNDS=${numRounds}
    `;

    const surplusClients = numClients > 3 ? numClients - 3 : 0;

    const flags = {
      surplus_clients: surplusClients
    };

    try {
      // Salva os arquivos .env
      const res = await fetch("http://100.127.13.111:5150/salvar-envs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          clientEnv: clientEnv.trim(),
          serverEnv: serverEnv.trim(),
        }),
      });

      const data = await res.json();
      setStatus(`✅ ${data.message}`);

      // Salva as flags (surplus_clients)
      await fetch("http://100.127.13.111:5150/save-flags", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(flags),
      });

      // Inicia os clientes
      await fetch("http://100.127.13.111:5150/start-simulados", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_clients: numClients }),
      });

      navigate("/metricas");
    } catch (err) {
      console.error(err);
      setStatus("❌ Erro ao enviar configurações ou iniciar clientes.");
    }
  };

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
        <Box textAlign="center" mt={3} mb={2}>
          <Button
            variant="contained"
            color="success"
            component={Link}
            to="/"
            sx={{ mb: 2 }}
          >
            🔙 Voltar ao menu
          </Button>

          <Typography variant="h4" mb={3} color="white">
            ⚙️ Configurar e Rodar Experimento
          </Typography>
        </Box>

        <Grid container spacing={2} justifyContent="center">
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel
                sx={{
                  color: "black",
                  fontWeight: "bold",
                  backgroundColor: "white",
                  px: 0.5,
                  borderRadius: 1,
                  zIndex: 1,
                  width: "fit-content",
                }}
              >
                Modelo
              </InputLabel>
              <Select
                value={modelo}
                onChange={(e) => setModelo(e.target.value)}
                sx={{ backgroundColor: "white" }}
              >
                <MenuItem value="CNN">CNN</MenuItem>
                <MenuItem value="DNN">DNN</MenuItem>
                <MenuItem value="LOGISTICREGRESSION">Logistic Regression</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel
                sx={{
                  color: "black",
                  fontWeight: "bold",
                  backgroundColor: "white",
                  px: 0.5,
                  borderRadius: 1,
                  zIndex: 1,
                  width: "fit-content",
                }}
              >
                Dataset
              </InputLabel>
              <Select
                value={dataset}
                onChange={(e) => setDataset(e.target.value)}
                sx={{ backgroundColor: "white" }}
              >
                <MenuItem value="MNIST">MNIST</MenuItem>
                <MenuItem value="CIFAR10">CIFAR-10</MenuItem>
                <MenuItem value="CIFAR100">CIFAR-100</MenuItem>
                <MenuItem value="UCIHAR">UCI-HAR</MenuItem>
                <MenuItem value="MotionSense">MotionSense</MenuItem>
                <MenuItem value="ExtraSensory">ExtraSensory</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <TextField
              label="Nº de Clientes"
              type="number"
              value={numClients}
              onChange={(e) => {
                const value = e.target.value;
                // remove o 0 à esquerda (ex: "01" vira "1")
                if (/^0\d/.test(value)) {
                  setNumClients(value.replace(/^0+/, ""));
                } else {
                  setNumClients(value);
                }
              }}
              onBlur={() => {
                if (numClients < 2) setNumClients(2);
                if (numClients > 13) setNumClients(13);
              }}
              fullWidth
              sx={{ backgroundColor: "white" }}
              inputProps={{ min: 2, max: 13 }}
              InputLabelProps={{
                sx: {
                  color: "black",
                  fontWeight: "bold",
                  backgroundColor: "white",
                  px: 0.5,
                  borderRadius: 1,
                  zIndex: 1,
                  width: "fit-content",
                },
              }}
            />
          </Grid>

          {numClients > 3 && (
            <Grid item xs={12}>
              <Alert severity="warning" sx={{ mt: 1 }}>
                ⚠️ Número de PIs disponíveis é 3. Os demais clientes serão executados localmente.
                <br />
                Certifique-se de que sua máquina possui capacidade para suportar a carga adicional.
              </Alert>
            </Grid>
          )}

          <Grid item xs={12} sm={6} md={4}>
            <TextField
              label="Epochs"
              type="number"
              value={epochs}
              onChange={(e) => {
                const value = e.target.value;
                // remove o 0 à esquerda (ex: "01" vira "1")
                if (/^0\d/.test(value)) {
                  setEpochs(value.replace(/^0+/, ""));
                } else {
                  setEpochs(value);
                }
              }}
              onBlur={() => {
                if (epochs < 1) setEpochs(1);
                if (epochs > 100) setEpochs(100);
              }}
              fullWidth
              sx={{ backgroundColor: "white" }}
              inputProps={{ min: 1, max: 100 }}
              InputLabelProps={{
                sx: {
                  color: "black",
                  fontWeight: "bold",
                  backgroundColor: "white",
                  px: 0.5,
                  borderRadius: 1,
                  zIndex: 1,
                  width: "fit-content",
                },
              }}
            />
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <TextField
              label="Batch Size"
              type="number"
              value={batchSize}
              onChange={(e) => {
                const value = e.target.value;
                // remove zeros à esquerda
                if (/^0\d+/.test(value)) {
                  setBatchSize(value.replace(/^0+/, ""));
                } else {
                  setBatchSize(value);
                }
              }}
              onBlur={() => {
                const parsed = parseInt(batchSize);
                if (isNaN(parsed) || parsed < 1) setBatchSize(1);
                else if (parsed > 1024) setBatchSize(1024);
                else setBatchSize(parsed); // garante que fique como número
              }}
              fullWidth
              sx={{ backgroundColor: "white" }}
              inputProps={{ min: 1, max: 1024 }}
              InputLabelProps={{
                shrink: true,
                sx: {
                  color: "black",
                  fontWeight: "bold",
                  backgroundColor: "white",
                  px: 0.5,
                  borderRadius: 1,
                  zIndex: 1,
                  width: "fit-content",
                },
              }}
            />
          </Grid>


          <Grid item xs={12} sm={6} md={4}>
            <TextField
              label="Nº de Rounds"
              type="number"
              value={numRounds}
              onChange={(e) => {
                const value = e.target.value;
                // remove o 0 à esquerda (ex: "01" vira "1")
                if (/^0\d/.test(value)) {
                  setRounds(value.replace(/^0+/, ""));
                } else {
                  setRounds(value);
                }
              }}
              onBlur={() => {
                if (numRounds < 1) setRounds(1);
                if (numRounds > 1000) setRounds(1000);
              }}
              fullWidth
              sx={{ backgroundColor: "white" }}
              inputProps={{ min: 1, max: 1000 }}
              InputLabelProps={{
                sx: {
                  color: "black",
                  fontWeight: "bold",
                  backgroundColor: "white",
                  px: 0.5,
                  borderRadius: 1,
                  zIndex: 1,
                  width: "fit-content",
                },
              }}
            />
          </Grid>

          {nonIID && (
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                label="Dirichlet α"
                type="number"
                value={dirichletAlpha}
                onChange={(e) => setDirichletAlpha(Number(e.target.value))}
                fullWidth
                sx={{ backgroundColor: "white" }}
                inputProps={{ min: 0.01, step: 0.01 }}
                onBlur={() => {
                  if (dirichletAlpha <= 0) setDirichletAlpha(0.01);
                  if (dirichletAlpha > 1) setDirichletAlpha(1);
                }}
                InputLabelProps={{
                  sx: {
                    color: "black",
                    fontWeight: "bold",
                    backgroundColor: "white",
                    px: 0.5,
                    borderRadius: 1,
                    zIndex: 1,
                    width: "fit-content",
                  },
                }}
              />
            </Grid>
          )}
        </Grid>

        <Box mt={3}>
          <FormControlLabel
            control={
              <Switch
                checked={nonIID}
                onChange={(e) => setNonIID(e.target.checked)}
                color="primary"
              />
            }
            label="Distribuição Não-IID"
            sx={{ color: "white", fontWeight: "bold" }}
          />
        </Box>

        <Box mt={3}>
          <Button
            variant="outlined"
            color="info"
            component={Link}
            to="/configurar"
            sx={{
              color: "#ffffff",
              borderColor: "#ffffff",
              '&:hover': {
                backgroundColor: "#ffffff22"
              }
            }}
          >
            📁 Enviar arquivos
          </Button>
        </Box>

        <Box mt={4}>
          <Button variant="contained" onClick={handleSubmit}>
            💾 Salvar Configurações
          </Button>
        </Box>

        <Typography variant="body1" mt={2} color="white">
          {status}
        </Typography>
      </Box>
    </Box>
  );
}
