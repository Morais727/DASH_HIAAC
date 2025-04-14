import React, { useState } from "react";
import {
  Box,
  Button,
  Typography,
  Input,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import background from "../assets/hiaac.png"; // 

export default function ConfigurarExperimento() {
  const [files, setFiles] = useState({
    client: null,
    server: null,
    dataset: null,
    envClient: null,
    envServer: null,
  });

  const [uploadStatus, setUploadStatus] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);

  const navigate = useNavigate();

  const handleFileChange = (e, type) => {
    setFiles({ ...files, [type]: e.target.files[0] });
  };

  const handleSubmit = () => {
    setDialogOpen(true);
  };

  const confirmAndUpload = async () => {
    const fileMappings = [
      { type: "client", filename: "client.py" },
      { type: "server", filename: "server.py" },
      { type: "dataset", filename: "dataset.csv" },
      { type: "envClient", filename: "env_client.env" },
      { type: "envServer", filename: "env_server.env" },
    ];

    const flags = {
      client: false,
      server: false,
      dataset: false,
      envClient: false,
      envServer: false,
    };

    const uploadPromises = fileMappings
      .filter(({ type }) => files[type])
      .map(async ({ type, filename }) => {
        const formData = new FormData();
        formData.append("file", files[type]);
        formData.append("filename", filename);

        const res = await fetch("http://100.127.13.111:5150/upload", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) throw new Error(`Erro ao enviar ${filename}`);
        flags[type] = true;
        return res.json();
      });

    try {
      await Promise.all(uploadPromises);
      setUploadStatus("✅ Arquivos enviados com sucesso!");
      localStorage.setItem("uploadedFlags", JSON.stringify(flags));

      // ✅ Salvar flags no backend após uploads bem-sucedidos
      await fetch("http://100.127.13.111:5150/save-flags", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(flags),
      });

      setDialogOpen(false);
      navigate("/metricas");
    } catch (error) {
      console.error(error);
      setUploadStatus("❌ Falha ao enviar um ou mais arquivos.");
      setDialogOpen(false);
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
        <Box textAlign="center" mt={5}>
          <Button
            variant="contained"
            color="success"
            component={Link}
            to="/padrao"
            sx={{ mt: 2, mb: 2 }}
          >
            🔙 Voltar
          </Button>

          <Typography variant="h4" mb={3}>
            🛠️ Configuração Avançada do Experimento
          </Typography>

          <Box
            display="grid"
            gridTemplateColumns="1fr 1fr"
            gap={4}
            mt={3}
            width="100%"
            justifyItems="center"
          >
            {[
              { label: "Client.py", type: "client", accept: ".py" },
              { label: "Server.py", type: "server", accept: ".py" },
              { label: "Dataset.csv", type: "dataset", accept: ".csv" },
              {
                label: "Variáveis de Ambiente do Cliente (.env ou .txt)",
                type: "envClient",
                accept: ".env,.txt"
              },
              {
                label: "Variáveis de Ambiente do Servidor (.env ou .txt)",
                type: "envServer",
                accept: ".env,.txt"
              },
            ].map(({ label, type, accept }) => (
              <Box
                key={type}
                p={2}
                border="1px solid #ccc"
                borderRadius="8px"
                bgcolor="#f5f5f5"
                width="100%"
                maxWidth="300px"
                textAlign="left"
              >
                <Typography variant="h6" color="black" mb={1}>
                  {label}
                </Typography>
                <Input
                  type="file"
                  accept={accept}
                  onChange={(e) => handleFileChange(e, type)}
                  sx={{ mb: 1 }}
                />
                {files[type] ? (
                  <Typography variant="body2" color="green">
                    ✅ {files[type].name} selecionado
                  </Typography>
                ) : (
                  <Typography variant="body2" color="gray">
                    Nenhum arquivo selecionado
                  </Typography>
                )}
              </Box>
            ))}
          </Box>

          <Button
            variant="contained"
            color="primary"
            sx={{ mt: 4 }}
            onClick={handleSubmit}
          >
            💾 Salvar Configurações
          </Button>

          <Typography variant="body1" mt={2}>
            {uploadStatus}
          </Typography>
        </Box>
      </Box>

      {/* Caixa de diálogo de confirmação */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>📦 Arquivos selecionados para envio</DialogTitle>
        <DialogContent>
          <List dense>
            {Object.entries(files).map(([key, file]) => (
              <ListItem key={key}>
                <ListItemText
                  primary={`${key.toUpperCase()}: ${file?.name || "❌ Não selecionado"}`}
                />
              </ListItem>
            ))}
          </List>
          <Typography mt={2}>
            Apenas os arquivos selecionados serão usados durante o treinamento.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} color="secondary">
            Cancelar
          </Button>
          <Button onClick={confirmAndUpload} variant="contained" color="primary">
            Confirmar Envio
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
