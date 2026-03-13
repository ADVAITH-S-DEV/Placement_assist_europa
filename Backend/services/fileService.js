const path = require("path");

/**
 * File-service abstraction.
 * Currently stores files locally via multer; can be swapped for S3 later.
 */

/**
 * Build a portable record for a saved resume.
 * @param {Object} file - The multer file object.
 * @returns {{ fileName, filePath, fileSize, mimeType }}
 */
const saveResume = (file) => {
  return {
    fileName: file.originalname,
    filePath: path.join(file.destination, file.filename),
    fileSize: file.size,
    mimeType: file.mimetype,
  };
};

module.exports = { saveResume };
