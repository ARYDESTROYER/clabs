const http = require('http');
const fs = require('fs').promises;
const path = require('path');

const port = 30000;
const baseDir = '/home/labDirectory';

const server = http.createServer(async (req, res) => {
    let filePath;
    if (req.url === '/' || req.url === '/index.html') {
        filePath = path.join(baseDir, 'index.html');
        res.setHeader('Content-Type', 'text/html');
    } else if (req.url === '/script.js') {
        filePath = path.join(baseDir, 'script.js');
        res.setHeader('Content-Type', 'application/javascript');
    } else if (req.url === '/styles.css') {
        filePath = path.join(baseDir, 'styles.css');
        res.setHeader('Content-Type', 'text/css');
    } else if (req.url === '/jquery.js') {
        filePath = path.join(baseDir, 'jquery.js');
        res.setHeader('Content-Type', 'application/javascript');
    } else {
        res.statusCode = 404;
        res.setHeader('Content-Type', 'text/plain');
        res.end('404 Not Found');
        return;
    }

    try {
        const content = await fs.readFile(filePath);
        res.statusCode = 200;
        res.end(content);
    } catch (err) {
        res.statusCode = 500;
        res.setHeader('Content-Type', 'text/plain');
        res.end('500 Internal Server Error');
    }
});

server.listen(port, () => {
    // console.log(`Server running at http://localhost:${port}/`);
});
