const express = require('express');
const cors = require('cors');
const adb = require('adbkit');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const client = adb.createClient();

// List connected devices
app.get('/api/devices', async (req, res) => {
  try {
    const devices = await client.listDevices();
    const result = devices.map(d => ({ id: d.id, type: d.type }));
    res.json(result);
  } catch (err) {
    console.error('ADB error listing devices:', err);
    res.status(500).json({ error: err.message });
  }
});

// Pull a file from the device and send it back
app.get('/api/pull', async (req, res) => {
  const { deviceId, filePath } = req.query;
  if (!deviceId || !filePath) {
    return res.status(400).json({ error: 'deviceId and filePath required' });
  }
  try {
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir);
    const fileName = path.basename(filePath);
    const destPath = path.join(tempDir, `${deviceId.replace(/[:/\\]/g, '_')}_${fileName}`);
    const pullStream = await client.pull(deviceId, filePath);
    const writeStream = fs.createWriteStream(destPath);
    pullStream.pipe(writeStream);
    await new Promise((resolve, reject) => {
      writeStream.on('finish', resolve);
      writeStream.on('error', reject);
    });
    res.download(destPath, fileName, err => {
      if (err) console.error('Download error:', err);
      fs.unlink(destPath, () => {});
    });
  } catch (err) {
    console.error('ADB pull error:', err);
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`ADB server listening on http://localhost:${PORT}`);
});
