const express = require("express");
const router = express.Router();
const upload = require("../config/multerConfig");
const resumeController = require("../controllers/resumeController");

// POST  /api/resume/upload
router.post("/upload", upload.single("resume"), resumeController.uploadResume);

module.exports = router;
