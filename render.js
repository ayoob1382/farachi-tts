// رندر فریم‌به‌فریم موازی.
// استفاده: node render.js scene.html out.mp4 [--fps 30] [--workers 4] [--duration S] [--debug]
// صحنه باید window.ready و window.setTime(t) داشته باشد و timings.json کنار خودش (یا با --dir) باشد.
const { chromium } = require('playwright');
const { spawn, spawnSync } = require('child_process');
const path = require('path'), http = require('http'), fs = require('fs'), os = require('os');

const argv = process.argv.slice(2);
const VALUE_FLAGS = ['fps', 'workers', 'duration', 'dir'];
const pos = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { if (VALUE_FLAGS.includes(argv[i].slice(2))) i++; } else pos.push(argv[i]);
}
const opt = (n, d) => { const i = argv.indexOf('--' + n); return i < 0 ? d : argv[i + 1]; };
const [sceneFile, outFile] = pos;
const FPS = +opt('fps', 30);
const WORKERS = Math.max(1, +opt('workers', Math.min(4, os.cpus().length)));
const DEBUG = argv.includes('--debug');
const ROOT = path.resolve(opt('dir', path.dirname(path.resolve(sceneFile))));  // پوشه‌ای که timings.json توش است
const MIME = {'.html':'text/html; charset=utf-8','.json':'application/json','.js':'text/javascript','.woff2':'font/woff2','.ttf':'font/ttf','.svg':'image/svg+xml','.png':'image/png'};

function serve() {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      const u = decodeURIComponent(q.url.split('?')[0]);
      // timings.json از ROOT، بقیه از کنار صحنه
      const cand = [path.join(ROOT, u), path.join(path.dirname(path.resolve(sceneFile)), u)];
      const p = cand.find(f => fs.existsSync(f) && fs.statSync(f).isFile());
      if (!p) { r.writeHead(404); return r.end(); }
      r.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
      fs.createReadStream(p).pipe(r);
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

async function renderRange(port, from, to, partFile, tick) {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-gpu'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(`http://127.0.0.1:${port}/${path.basename(sceneFile)}${DEBUG ? '?debug=1' : ''}`);
  await page.waitForFunction('window.ready===true', null, { timeout: 30000 });
  const ff = spawn('ffmpeg', ['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-',
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',String(FPS), partFile], { stdio: ['pipe','inherit','inherit'] });
  const closed = new Promise(r => ff.on('close', r));
  for (let f = from; f < to; f++) {
    await page.evaluate(t => window.setTime(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    tick();
  }
  ff.stdin.end(); await closed; await browser.close();
}

(async () => {
  if (!sceneFile || !outFile) { console.error('usage: node render.js scene.html out.mp4 [--fps 30] [--workers N] [--debug]'); process.exit(1); }
  const T = JSON.parse(fs.readFileSync(path.join(ROOT, 'timings.json'), 'utf8'));
  const D = +opt('duration', T.duration);
  const total = Math.round(D * FPS);
  const n = Math.min(WORKERS, total);
  const srv = await serve();
  const port = srv.address().port;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'farachi-'));
  const per = Math.ceil(total / n);
  const parts = [];
  let done = 0; const t0 = Date.now();
  const tick = () => { if (++done % 300 === 0) { const s = (Date.now() - t0) / 1000;
    console.log(`frame ${done}/${total}  ${s.toFixed(0)}s  (${(done/s).toFixed(1)} fps)  باقی‌مانده ~${((total-done)/(done/s)/60).toFixed(1)} دقیقه`); } };
  const jobs = [];
  for (let i = 0; i < n; i++) {
    const from = i * per, to = Math.min(total, from + per);
    if (from >= to) continue;
    const pf = path.join(tmp, `part${String(i).padStart(2, '0')}.mp4`);
    parts.push(pf);
    jobs.push(renderRange(port, from, to, pf, tick));
  }
  console.log(`${total} فریم، ${parts.length} پردازش موازی`);
  await Promise.all(jobs);
  srv.close();
  const list = path.join(tmp, 'list.txt');
  fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
  const r = spawnSync('ffmpeg', ['-y','-loglevel','error','-f','concat','-safe','0','-i',list,'-c','copy',outFile], { stdio: 'inherit' });
  if (r.status !== 0) { console.error('ترکیب بخش‌ها ناموفق بود'); process.exit(1); }
  fs.rmSync(tmp, { recursive: true, force: true });
  const el = (Date.now() - t0) / 1000;
  console.log(`تمام شد: ${total} فریم در ${el.toFixed(1)} ثانیه (${(total/el).toFixed(1)} fps) -> ${outFile}`);
})().catch(e => { console.error(e); process.exit(1); });
