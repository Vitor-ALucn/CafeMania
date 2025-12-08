const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'cafeteria',
  decimalNumbers: true,
  waitForConnections: true,
  connectionLimit: 5
});

module.exports = pool;