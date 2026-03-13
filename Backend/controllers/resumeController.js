const fileService = require("../services/fileService");
const { success, error } = require("../utils/responseHelper");

/**
 * POST /api/resume/upload
 * Accepts a single resume file (field name: "resume").
 */
const uploadResume = (req, res) => {
  try {
    if (!req.file) {
      return error(res, "No file uploaded. Please attach a resume.", 400);
    }

    const fileRecord = fileService.saveResume(req.file);

    return success(
      res,
      {
        message: "Resume uploaded successfully",
        file: fileRecord,
      },
      201
    );
  } catch (err) {
    console.error("Upload error:", err.message);
    return error(res, "Failed to upload resume", 500);
  }
};

module.exports = { uploadResume };
