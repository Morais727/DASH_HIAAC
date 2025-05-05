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
  ListItemText,
  TextField,
  IconButton
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import background from "../assets/hiaac.png";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import { getApiUrl } from "../utils/apiConfig";

export default function ConfigurarClientes() {
  const [files, setFiles] = useState({});
  const [ipList, setIpList] = useState([""]);
  const [uploadStatus, setUploadStatus] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();

  const handleIPChange = (index, value) => {
    const newIps = [...ipList];
    newIps[index] = value;
    setIpList(newIps);
  };

  const addIPField = () => {
    setIpList([...ipList, ""]);
  };

  const removeIPField = (index) => {
    const newIps = ipList.filter((_, i) => i !== index);
    setIpList(newIps);
  };

  const handleSubmit = () => {
    setDialogOpen(true);
  };

  const confirmAndUpload = async () => {
    try {
      // Envia IPs ao backend
      await fetch(getApiUrl("/save-ips"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ips: ipList }),
      });

      setUploadStatus("IP(s) enviados com sucesso!");
      setDialogOpen(false);
      navigate("/metricas");

    } catch (error) {
      console.error(error);
      setUploadStatus("Falha ao enviar os IPs.");
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
        <Button
          variant="contained"
          color="success"
          component={Link}
          to="/"
          sx={{ mb: 2 }}
        >
          Voltar
        </Button>

        <Typography variant="h4" mb={3}>
          Configurando IP da Raspberry Pi
        </Typography>

        {/* Campos de IPs Dinâmicos */}
        <Box mt={2} width="100%" maxWidth="600px">
          {ipList.map((ip, index) => (
            <Box key={index} display="flex" alignItems="center" mb={2}>
              <TextField
                fullWidth
                label={`IP ${index + 1}`}
                value={ip}
                onChange={(e) => handleIPChange(index, e.target.value)}
              />
              {ipList.length > 1 && (
                <IconButton onClick={() => removeIPField(index)} sx={{ ml: 1 }}>
                  <DeleteIcon color="error" />
                </IconButton>
              )}
            </Box>
          ))}

          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={addIPField}
            sx={{ mt: 1 }}
          >
            Adicionar outro IP
          </Button>
        </Box>

        <Button
          variant="contained"
          color="primary"
          sx={{ mt: 4 }}
          onClick={handleSubmit}
        >
          Salvar Configurações
        </Button>

        <Typography variant="body1" mt={2}>
          {uploadStatus}
        </Typography>
      </Box>

      {/* Diálogo de confirmação */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>IPs informados</DialogTitle>
        <DialogContent>
          <List dense>
            {ipList.map((ip, index) => (
              <ListItem key={index}>
                <ListItemText primary={`IP ${index + 1}: ${ip || "❌ Não informado"}`} />
              </ListItem>
            ))}
          </List>
          <Typography mt={2}>
            Os IPs acima serão usados na configuração do experimento.
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

