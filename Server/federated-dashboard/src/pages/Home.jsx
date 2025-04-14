import { Box, Typography, Button } from "@mui/material";
import { Link } from "react-router-dom";
import background from "../assets/hiaac.png"; // Importe a imagem de fundo

export default function Home() {
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
        minHeight="10vh"
        bgcolor="rgba(124, 136, 156, 0.9)" // Adicione opacidade para melhor contraste com o fundo
        padding={4}
        borderRadius={2}
        boxShadow={3}
        width="50vw"
      >
        <Typography variant="h2" color="white">
                      Dashboard Federated Learning
                    </Typography>
        
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
            Acompanhar Métricas
          </Button>

          <Button
            component={Link}
            to="/padrao"
            variant="contained"
            color="secondary"
            sx={{ m: 2, bgcolor: "purple" }}
          >
            Configurar Experimento
          </Button>

          <Button
            component={Link}
            to="/configurar-pis"
            variant="contained"
            color="secondary"
            sx={{ m: 2, bgcolor: "blue" }}
          >
            Configurar PIs
          </Button>

        </Box>

        {/* Logo no canto inferior direito */}
        <Box
          position="absolute"
          bottom={16}
          right={16}
        >
        </Box>
      </Box>
    </Box>
  );
}
