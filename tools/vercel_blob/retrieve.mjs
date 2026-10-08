/** Build-only byte transfer. Python/D2 remains the archive authority. */
import { open, realpath, lstat, link, unlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, dirname, resolve } from 'node:path';
import { Readable, Transform } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { pathToFileURL } from 'node:url';

export const categories = Object.freeze([
  'SDK_DEPENDENCY_MISSING', 'BUILD_OIDC_MISSING', 'STORE_METADATA_MISMATCH',
  'STATIC_CREDENTIAL_PROHIBITED', 'PREVIEW_ENVIRONMENT_REQUIRED',
  'INVALID_ARGUMENT', 'PRIVATE_OBJECT_NOT_FOUND',
  'BLOB_ACCESS_REJECTED', 'NETWORK_OR_TLS_FAILURE', 'DOWNLOAD_TIMEOUT',
  'DOWNLOAD_STREAM_INTERRUPTED', 'OUTPUT_FILESYSTEM_FAILURE',
  'INVALID_RESPONSE', 'UNKNOWN_REDACTED_FAILURE',
]);
class Failure extends Error {
  constructor(category) { super(category); this.category = category; }
}
const networkCodes = new Set([
  'ENOTFOUND', 'EAI_AGAIN', 'ECONNRESET', 'ECONNREFUSED', 'ETIMEDOUT',
  'CERT_HAS_EXPIRED', 'UNABLE_TO_VERIFY_LEAF_SIGNATURE',
  'DEPTH_ZERO_SELF_SIGNED_CERT', 'UND_ERR_CONNECT_TIMEOUT',
]);

function classify(error, sdk, stage, timedOut) {
  if (timedOut) return 'DOWNLOAD_TIMEOUT';
  if (error instanceof Failure) return error.category;
  if (sdk?.BlobAccessError && error instanceof sdk.BlobAccessError)
    return 'BLOB_ACCESS_REJECTED';
  if (sdk?.BlobNotFoundError && error instanceof sdk.BlobNotFoundError)
    return 'PRIVATE_OBJECT_NOT_FOUND';
  if (stage === 'dependency') return 'SDK_DEPENDENCY_MISSING';
  if (stage === 'output') return 'OUTPUT_FILESYSTEM_FAILURE';
  if (networkCodes.has(error?.code) || networkCodes.has(error?.cause?.code))
    return 'NETWORK_OR_TLS_FAILURE';
  if (stage === 'stream') return 'DOWNLOAD_STREAM_INTERRUPTED';
  return 'UNKNOWN_REDACTED_FAILURE';
}

async function destinationPath(destination) {
  if (typeof destination !== 'string' || destination !== resolve(destination) ||
      basename(destination) !== 'runtime.tar.gz') throw new Failure('INVALID_ARGUMENT');
  const parent = dirname(destination);
  if (!basename(parent).startsWith('neurofly-build-') ||
      dirname(parent) !== await realpath(tmpdir()) ||
      await realpath(parent) !== parent || !(await lstat(parent)).isDirectory())
    throw new Failure('INVALID_ARGUMENT');
  return destination;
}

export async function retrieve({ destination, pathname, storeId }, {
  env = process.env, loadSdk = () => import('@vercel/blob'), timeoutMs = 120000,
} = {}) {
  let sdk, stage = 'guard', part, handle, ownsPart = false, ownsDestination = false;
  let timer, timedOut = false;
  const controller = new AbortController();
  try {
    if (!env.VERCEL_OIDC_TOKEN?.trim()) throw new Failure('BUILD_OIDC_MISSING');
    if (env.VERCEL_ENV !== 'preview') throw new Failure('PREVIEW_ENVIRONMENT_REQUIRED');
    if (!storeId || env.BLOB_STORE_ID !== storeId) throw new Failure('STORE_METADATA_MISMATCH');
    if (env.BLOB_READ_WRITE_TOKEN) throw new Failure('STATIC_CREDENTIAL_PROHIBITED');
    if (typeof pathname !== 'string' ||
        !/^neurofly\/runtime\/v2\/([a-f0-9]{64})\/neurofly-runtime-v2-\1\.tar\.gz$/.test(pathname))
      throw new Failure('INVALID_ARGUMENT');
    stage = 'output';
    destination = await destinationPath(destination);
    // Exclusive staging plus an atomic, no-overwrite link prevents partial acceptance.
    part = `${destination}.part`;
    handle = await open(part, 'wx', 0o600);
    ownsPart = true;
    stage = 'dependency';
    sdk = await loadSdk();
    stage = 'request';
    timer = setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs);
    let rejectAbort;
    const aborted = new Promise((_, reject) => {
      rejectAbort = () => reject(new Failure('DOWNLOAD_TIMEOUT'));
      controller.signal.addEventListener('abort', rejectAbort, { once: true });
    });
    let result;
    try {
      result = await Promise.race([
        sdk.get(pathname, {
          access: 'private', oidcToken: env.VERCEL_OIDC_TOKEN, storeId,
          useCache: false, abortSignal: controller.signal,
        }), aborted,
      ]);
    } finally { controller.signal.removeEventListener('abort', rejectAbort); }
    if (result === null) throw new Failure('PRIVATE_OBJECT_NOT_FOUND');
    if (result?.statusCode !== 200 || !result.stream?.getReader ||
        !Number.isSafeInteger(result.blob?.size) || result.blob.size < 0)
      throw new Failure('INVALID_RESPONSE');
    stage = 'stream';
    let transferred = 0;
    const counter = new Transform({ transform(chunk, encoding, callback) {
      transferred += chunk.length; callback(null, chunk);
    } });
    await pipeline(Readable.fromWeb(result.stream), counter,
      handle.createWriteStream({ autoClose: true }),
      { signal: controller.signal });
    handle = undefined;
    // Transport completeness only; Python still validates the pinned bytes/SHA.
    if (transferred !== result.blob.size) throw new Failure('DOWNLOAD_STREAM_INTERRUPTED');
    stage = 'output';
    if (controller.signal.aborted) throw new Failure('DOWNLOAD_TIMEOUT');
    await link(part, destination); ownsDestination = true;
    await unlink(part); ownsPart = false;
    return { ok: true };
  } catch (error) {
    const category = classify(error, sdk, stage, timedOut);
    let cleanupFailed = false;
    if (handle) { try { await handle.close(); } catch { cleanupFailed = true; } }
    if (ownsPart) { try { await unlink(part); } catch { cleanupFailed = true; } }
    if (ownsDestination) {
      try { await unlink(destination); } catch { cleanupFailed = true; }
    }
    return { ok: false, category: cleanupFailed ? 'OUTPUT_FILESYSTEM_FAILURE' : category };
  } finally { clearTimeout(timer); }
}

export async function main(args = process.argv.slice(2)) {
  const result = args.length === 3 ? await retrieve({
    destination: args[0], pathname: args[1], storeId: args[2],
  }) : { ok: false, category: 'INVALID_ARGUMENT' };
  if (!result.ok) process.stderr.write(`NEUROFLY_BLOB_FAILURE ${result.category}\n`);
  return result.ok ? 0 : 1;
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href)
  process.exitCode = await main();
