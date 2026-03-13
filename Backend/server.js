require("dotenv").config();

const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const path = require("path");

const resumeRoutes = require("./routes/resumeRoutes");

const app = express();
const PORT = process.env.PORT || 5000;

// ──── Middleware ────────────────────────────────────────────
app.use(cors());
app.use(morgan("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve uploaded files statically (handy during development)
app.use("/uploads", express.static(path.join(__dirname, "uploads")));

// ──── Routes ───────────────────────────────────────────────
app.use("/api/resume", resumeRoutes);

// Health-check
app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", uptime: process.uptime() });
});

// ──── Global Error Handler ─────────────────────────────────
app.use((err, _req, res, _next) => {
  // Multer-specific errors (e.g. file too large)
  if (err.name === "MulterError" || err.message) {
    return res.status(400).json({ success: false, error: err.message });
  }
  console.error(err.stack);
  res.status(500).json({ success: false, error: "Internal Server Error" });
});

// ──── Start Server ─────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`   Health: http://localhost:${PORT}/api/health`);
  console.log(`   Upload: POST http://localhost:${PORT}/api/resume/upload`);
});
