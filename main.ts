// Entry for make.fun's "Sum up 17 November's world news in one image" bounty.
//
// The picture itself is entry.png beside this file: a front-page style
// infographic of Tuesday 17 November 2026, drawn in code by
// generate_image.py (see SOURCES.md for the stories and where they were
// reported). This program is the delivery step the grader runs: it checks
// the image against the competition gate and then copies it, byte for
// byte, to /output/entry.png.
//
// Gate, from the kit's RULES.txt: the file is a whole PNG or JPEG, at most
// 1 MiB (1048576 bytes) and at most 1024 by 1024 pixels, and the judge sees
// exactly the bytes copied. The program runs twice and must write the same
// bytes both times, so it does nothing but validate and copy.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1048576; // 1 MiB
const MAX_SIDE = 1024; // pixels, either axis

const here = fileURLToPath(new URL('.', import.meta.url));
const imagePath = join(here, 'entry.png');
const bytes = readFileSync(imagePath);

// --- validate the image against the gate before handing it over --------
function fail(reason) {
  throw new Error(`entry.png refused by the gate: ${reason}`);
}

if (bytes.length === 0) fail('the file is empty');
if (bytes.length > MAX_BYTES) fail(`${bytes.length} bytes is over the 1 MiB cap`);

let format;
let width;
let height;
if (bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) {
  // PNG: width and height are big-endian uint32s in the IHDR chunk.
  format = 'PNG';
  width = bytes.readUInt32BE(16);
  height = bytes.readUInt32BE(20);
} else if (bytes[0] === 0xff && bytes[1] === 0xd8) {
  // JPEG: walk the segments to the start-of-frame marker for the size.
  format = 'JPEG';
  let off = 2;
  while (off + 9 < bytes.length) {
    if (bytes[off] !== 0xff) fail('a JPEG segment does not start with 0xFF');
    const marker = bytes[off + 1];
    const len = bytes.readUInt16BE(off + 2);
    if (marker >= 0xc0 && marker <= 0xc3) {
      height = bytes.readUInt16BE(off + 5);
      width = bytes.readUInt16BE(off + 7);
      break;
    }
    off += 2 + len;
  }
  if (width === undefined) fail('no JPEG start-of-frame segment found');
} else {
  fail('the first bytes are neither a PNG signature nor a JPEG SOI');
}

if (width > MAX_SIDE || height > MAX_SIDE) {
  fail(`${width}x${height} is over the 1024x1024 cap`);
}

// --- hand it over ---------------------------------------------------------
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, 'entry.png');
copyFileSync(imagePath, outPath);

// The judge sees exactly the bytes in the output file, so read them back
// and prove the copy is the image that was validated above, not a partial
// or altered one.
const handed = readFileSync(outPath);
if (!handed.equals(bytes)) fail('the copied file differs from the validated image');

console.log(`entry.png: ${format} ${width}x${height}, ${bytes.length} bytes -> ${outPath}`);
