const BASE_URL = "/assets/william/";
const ORT_VERSION = "1.27.0";
const BYTE_ENCODER = createByteEncoder();
const BYTE_LEVEL_PATTERN = /'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+/gu;

function createByteEncoder() {
  const bytes = [];
  for (let i = 33; i <= 126; i++) bytes.push(i);
  for (let i = 161; i <= 172; i++) bytes.push(i);
  for (let i = 174; i <= 255; i++) bytes.push(i);

  const encoder = new Map();
  for (const b of bytes) encoder.set(b, String.fromCharCode(b));

  let next = 256;
  for (let b = 0; b < 256; b++) {
    if (!encoder.has(b)) encoder.set(b, String.fromCharCode(next++));
  }
  return encoder;
}

function byteLevel(text) {
  const encoded = new TextEncoder().encode(text.normalize("NFC"));
  let out = "";
  for (const byte of encoded) out += BYTE_ENCODER.get(byte);
  return out;
}

class WilliamTokenizer {
  constructor(manifest) {
    this.unkId = manifest.tokenizer.unkId;
    this.special = manifest.specialTokens;
    this.pieces = new Map();
    this.maxPieceLength = 0;

    for (let id = 0; id < manifest.tokenizer.vocab.length; id++) {
      const [piece, score] = manifest.tokenizer.vocab[id];
      this.pieces.set(piece, { id, score });
      this.maxPieceLength = Math.max(this.maxPieceLength, piece.length);
    }
  }

  encodePiece(piece) {
    const n = piece.length;
    const scores = new Float64Array(n + 1);
    const prev = new Int32Array(n + 1);
    const ids = new Int32Array(n + 1);
    scores.fill(-Infinity);
    prev.fill(-1);
    ids.fill(this.unkId);
    scores[0] = 0;

    for (let i = 0; i < n; i++) {
      if (!Number.isFinite(scores[i])) continue;

      for (let size = 1; size <= this.maxPieceLength && i + size <= n; size++) {
        const candidate = this.pieces.get(piece.slice(i, i + size));
        if (!candidate) continue;
        const score = scores[i] + candidate.score;
        if (score > scores[i + size]) {
          scores[i + size] = score;
          prev[i + size] = i;
          ids[i + size] = candidate.id;
        }
      }

      if (!Number.isFinite(scores[i + 1])) {
        scores[i + 1] = scores[i] - 100;
        prev[i + 1] = i;
        ids[i + 1] = this.unkId;
      }
    }

    const out = [];
    for (let cursor = n; cursor > 0; cursor = prev[cursor]) {
      if (prev[cursor] < 0) return [this.unkId];
      out.push(ids[cursor]);
    }
    return out.reverse();
  }

  encodeText(text) {
    const ids = [];
    for (const match of text.normalize("NFC").matchAll(BYTE_LEVEL_PATTERN)) {
      ids.push(...this.encodePiece(byteLevel(match[0])));
    }
    return ids;
  }

  encodePrompt(title) {
    const cleanTitle = title.trim() || "Untitled";
    return [
      this.special.title,
      ...this.encodeText(` ${cleanTitle} `),
      this.special.poem,
      ...this.encodeText(" "),
    ];
  }
}

function topPSample(logits, ids, options, endId) {
  const adjusted = Float32Array.from(logits);

  if (options.repetitionPenalty > 1) {
    for (const id of new Set(ids)) {
      adjusted[id] = adjusted[id] < 0 ? adjusted[id] * options.repetitionPenalty : adjusted[id] / options.repetitionPenalty;
    }
  }

  if (options.noRepeatNgramSize > 1 && ids.length >= options.noRepeatNgramSize - 1) {
    const n = options.noRepeatNgramSize;
    const prefix = ids.slice(ids.length - n + 1).join(",");
    for (let start = 0; start <= ids.length - n; start++) {
      if (ids.slice(start, start + n - 1).join(",") === prefix) adjusted[ids[start + n - 1]] = -Infinity;
    }
  }

  const candidates = Array.from(adjusted, (v, id) => ({ id, v: v / options.temperature }));
  let max = -Infinity;
  for (const item of candidates) if (item.v > max) max = item.v;

  let total = 0;
  for (const item of candidates) {
    item.p = Number.isFinite(item.v) ? Math.exp(item.v - max) : 0;
    total += item.p;
  }
  for (const item of candidates) item.p /= total;
  candidates.sort((a, b) => b.p - a.p);

  const kept = [];
  let cumulative = 0;
  for (const item of candidates) {
    kept.push(item);
    cumulative += item.p;
    if (cumulative >= options.topP) break;
  }

  let keptTotal = 0;
  for (const item of kept) keptTotal += item.p;
  let draw = Math.random() * keptTotal;
  for (const item of kept) {
    draw -= item.p;
    if (draw <= 0) return item.id;
  }
  return kept[0]?.id ?? endId;
}

function lastTokenLogits(tensor, vocabSize) {
  return tensor.data.subarray(tensor.data.length - vocabSize);
}

class WilliamOrtModel {
  constructor(manifest, session) {
    this.manifest = manifest;
    this.session = session;
    this.vocabSize = manifest.config.vocab_size;
    this.tokenizer = new WilliamTokenizer(manifest);
  }

  async nextLogits(ids) {
    const input = BigInt64Array.from(ids, (id) => BigInt(id));
    const tensor = new ort.Tensor("int64", input, [1, ids.length]);
    const results = await this.session.run({ input_ids: tensor });
    return lastTokenLogits(results.logits, this.vocabSize);
  }

  async generate(promptIds, options, onToken) {
    const ids = [...promptIds];
    const endId = this.manifest.specialTokens.end;
    const maxNew = Math.min(options.maxTokens, this.manifest.config.context_length - ids.length - 1);
    let text = "";

    for (let step = 0; step < maxNew; step++) {
      const logits = await this.nextLogits(ids);
      const next = topPSample(logits, ids, options, endId);
      if (next === endId) break;
      ids.push(next);
      text += this.manifest.decode[next] ?? "";
      onToken(text);
      await new Promise(requestAnimationFrame);
    }

    return text.trim();
  }

  async generateForTitle(title, options, onToken) {
    return this.generate(this.tokenizer.encodePrompt(title), options, onToken);
  }

  async release() {
    const session = this.session;
    this.session = null;
    if (session) await session.release();
  }
}

async function loadWilliam(status) {
  status.textContent = "loading manifest...";
  const manifest = await fetch(`${BASE_URL}manifest.json`).then((response) => response.json());

  status.textContent = "loading ONNX Runtime...";
  if (!globalThis.ort) throw new Error("ONNX Runtime Web did not load");
  ort.env.wasm.wasmPaths = `https://cdn.jsdelivr.net/npm/onnxruntime-web@${ORT_VERSION}/dist/`;
  ort.env.wasm.numThreads = globalThis.crossOriginIsolated
    ? Math.max(1, Math.min(4, navigator.hardwareConcurrency || 1))
    : 1;
  // Keep the WASM heap in a page-owned worker. Browsers terminate that worker
  // promptly on refresh instead of briefly retaining two large heaps.
  ort.env.wasm.proxy = true;

  status.textContent = "loading 14 MB ONNX model...";
  let session;
  try {
    session = await ort.InferenceSession.create(`${BASE_URL}william-int8.onnx`, {
      executionProviders: ["wasm"],
      executionMode: "sequential",
      graphOptimizationLevel: "disabled",
      enableCpuMemArena: false,
      enableMemPattern: false,
    });
  } catch (error) {
    if (String(error?.message ?? error).includes("Out of memory")) {
      throw new Error("the browser ran out of WebAssembly memory while loading the model");
    }
    throw error;
  }

  status.textContent = "model ready";
  return new WilliamOrtModel(manifest, session);
}

async function main() {
  const root = document.querySelector("[data-william-demo]");
  if (!root) return;

  const button = root.querySelector("[data-william-generate]");
  const output = root.querySelector("[data-william-output]");
  const status = root.querySelector("[data-william-status]");
  const title = root.querySelector("[data-william-title]");

  button.disabled = true;
  button.hidden = true;
  let model;
  let pageIsActive = true;

  window.addEventListener("pagehide", () => {
    pageIsActive = false;
    void model?.release().catch(() => {});
  }, { once: true });

  try {
    model = await loadWilliam(status);
    if (!pageIsActive) {
      await model.release();
      return;
    }
  } catch (error) {
    status.textContent = `could not load William: ${error.message}`;
    return;
  }

  async function writePoem() {
    const prompts = model.manifest.seedPrompts;
    const options = model.manifest.defaultGeneration;
    const requestedTitle = title.value.trim() || prompts[Math.floor(Math.random() * prompts.length)].title;
    button.disabled = true;
    button.hidden = true;
    output.textContent = "";
    title.value = requestedTitle;
    status.textContent = "generating locally with ONNX Runtime...";
    const started = performance.now();

    try {
      const poem = await model.generateForTitle(requestedTitle, options, (text) => {
        output.textContent = text;
      });
      output.textContent = poem || output.textContent;
      status.textContent = `done in ${((performance.now() - started) / 1000).toFixed(1)}s`;
    } catch (error) {
      status.textContent = `generation failed: ${error.message}`;
    } finally {
      button.disabled = false;
      button.hidden = false;
    }
  }

  button.addEventListener("click", writePoem);
  title.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      if (!button.disabled) writePoem();
    }
  });

  const prompts = model.manifest.seedPrompts;
  title.value = prompts[Math.floor(Math.random() * prompts.length)].title;
  await writePoem();
}

main();
