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
const serveUrl = await bundle({entryPoint});
const composition = await selectComposition({
  serveUrl,
  id: 'MotionOverlay',
  inputProps,
});

await renderMedia({
  composition,
  serveUrl,
  codec: 'vp9',
  outputLocation: path.resolve(outputPath),
  inputProps,
  concurrency: 1,
  disallowParallelEncoding: true,
  imageFormat: 'png',
  pixelFormat: 'yuva420p',
  muted: true,
  logLevel: 'info',
});
