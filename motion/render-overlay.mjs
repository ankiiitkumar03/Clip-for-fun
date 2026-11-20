import fs from 'node:fs/promises';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';

const [propsPath, outputPath] = process.argv.slice(2);
if (!propsPath || !outputPath) {
  throw new Error('Usage: node render-overlay.mjs props.json overlay.webm');
}

const inputProps = JSON.parse(await fs.readFile(propsPath, 'utf8'));
const entryPoint = path.resolve('src/index.jsx');
const bundleDir = await fs.mkdtemp(path.join(process.cwd(), '.bundle-'));
try {
  const serveUrl = await bundle({entryPoint, outDir: bundleDir});
  const composition = await selectComposition({
    serveUrl,
    id: 'MotionOverlay',
    inputProps,
  });

  await renderMedia({
    composition,
    serveUrl,
    codec: 'prores',
    proResProfile: '4444',
    outputLocation: path.resolve(outputPath),
    inputProps,
    concurrency: 1,
    disallowParallelEncoding: true,
    imageFormat: 'png',
    pixelFormat: 'yuva444p10le',
    muted: true,
    logLevel: 'info',
  });
} finally {
  await fs.rm(bundleDir, {recursive: true, force: true});
}
