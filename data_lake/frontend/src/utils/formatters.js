/**
 * Utility function to format numbers with thousand separators
 * @param {number} num - The number to format
 * @param {number} decimals - Number of decimal places (default 0)
 * @returns {string} - Formatted number string
 */
export const formatNumber = (num, decimals = 0) => {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return Number(num).toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

/**
 * Utility function to format currency values with ₹ symbol and thousand separators
 * @param {number} amount - The amount to format
 * @param {number} decimals - Number of decimal places (default 2)
 * @returns {string} - Formatted currency string
 */
export const formatCurrency = (amount, decimals = 2) => {
  if (amount === null || amount === undefined || isNaN(amount)) return '₹ N/A';
  return '₹ ' + Number(amount).toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

/**
 * Utility function to format percentages
 * @param {number} value - The value to format as percentage
 * @param {number} decimals - Number of decimal places (default 2)
 * @returns {string} - Formatted percentage string
 */
export const formatPercent = (value, decimals = 2) => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A%';
  return Number(value).toFixed(decimals) + '%';
};
