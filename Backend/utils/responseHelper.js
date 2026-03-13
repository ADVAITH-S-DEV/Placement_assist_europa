/**
 * Standardized API response helpers.
 * Use these everywhere so every endpoint returns a consistent shape.
 */

const success = (res, data = null, statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    data,
  });
};

const error = (res, message = "Internal Server Error", statusCode = 500) => {
  return res.status(statusCode).json({
    success: false,
    error: message,
  });
};

module.exports = { success, error };
