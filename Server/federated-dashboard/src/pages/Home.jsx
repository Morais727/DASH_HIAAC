import { Box, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import logo from "../assets/logo_HIAAC.svg";


export default function Home() {
  return (
    <Box
      height="100vh"
      width="100vw"
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      bgcolor="#121212"
      position="relative" 
    >
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="10vh"
        bgcolor="#7c889c"
        padding={4}
        borderRadius={2}
        boxShadow={3}
        width="70vw"
        >
        <Typography variant="h4" gutterBottom color="white">
          Menu Principal
        </Typography>

        <Box mt={4} display="flex" justifyContent="center" flexWrap="wrap">
          <Button
            component={Link}
            to="/metricas"
            variant="contained"
            color="success"
            sx={{ m: 2 }}
          >
            📊 Acompanhar Métricas
          </Button>

          <Button
            component={Link}
            to="/padrao"
            variant="contained"
            color="secondary"
            sx={{ m: 2, bgcolor: "purple" }}
          >
            ⚙️ Configurar Experimento
          </Button>
        </Box>

        {/* Logo no canto inferior direito */}
        <Box
          position="absolute"
          bottom={16}
          right={16}
        >
          <img src={logo} alt="Logo" style={{ width: 250, height: "auto" }} />
        </Box>
      </Box>
    </Box>
  );
}
