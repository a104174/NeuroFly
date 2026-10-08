import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, readFile, writeFile, rm, mkdir, copyFile, readdir, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import * as sdk from '@vercel/blob';
import { retrieve, categories } from './retrieve.mjs';

const storeId = 'store_S3zkyGCIjHi3p79M';
const sha = '12c2f5c314a273c7ada36277cf0db6415e929ab3bdf4911a26f78d72943fbca5';
const pathname = `neurofly/runtime/v2/${sha}/neurofly-runtime-v2-${sha}.tar.gz`;
const env = { VERCEL_ENV: 'preview', VERCEL_OIDC_TOKEN: 'synthetic-test-only', BLOB_STORE_ID: storeId };
const sensitive = 'synthetic-private-error https://example.invalid/?signature=test-only';
const response = (bytes = Buffer.from('fixture')) => ({ statusCode: 200,
  blob: { size: bytes.length }, stream: new ReadableStream({ start(c) {
    c.enqueue(bytes); c.close();
  } }) });

async function fixture(t) {
  const root = await mkdtemp(join(await realpath(tmpdir()), 'neurofly-build-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  return { root, destination: join(root, 'runtime.tar.gz'), pathname, storeId };
}
const options = (get) => ({ env, loadSdk: async () => ({ ...sdk, get }) });
async function assertFailure(t, expected, get, extra = {}) {
  const input = await fixture(t);
  const result = await retrieve(input, { ...options(get), ...extra });
  assert.deepEqual(result, { ok: false, category: expected });
  assert.deepEqual(await readdir(input.root), []);
  assert(!JSON.stringify(result).includes(sensitive));
}

test('private pinned request streams bytes with explicit OIDC and no static token', async t => {
  const input = await fixture(t);
  const bytes = Buffer.from('exact\0fixture\xff', 'latin1');
  const result = await retrieve(input, options(async (name, opts) => {
    assert.equal(name, pathname);
    assert.equal(opts.access, 'private'); assert.equal(opts.storeId, storeId);
    assert.equal(opts.oidcToken, env.VERCEL_OIDC_TOKEN);
    assert.equal(opts.useCache, false); assert(!('token' in opts));
    assert(opts.abortSignal instanceof AbortSignal);
    return response(bytes);
  }));
  assert.deepEqual(result, { ok: true });
  assert.deepEqual(await readFile(input.destination), bytes);
  assert.deepEqual(await readdir(input.root), ['runtime.tar.gz']);
});
for (const [name, override, category] of [
  ['missing OIDC', { VERCEL_OIDC_TOKEN: '' }, 'BUILD_OIDC_MISSING'],
  ['Production rejected', { VERCEL_ENV: 'production' }, 'PREVIEW_ENVIRONMENT_REQUIRED'],
  ['missing environment', { VERCEL_ENV: undefined }, 'PREVIEW_ENVIRONMENT_REQUIRED'],
  ['missing store', { BLOB_STORE_ID: undefined }, 'STORE_METADATA_MISMATCH'],
  ['wrong store', { BLOB_STORE_ID: 'wrong' }, 'STORE_METADATA_MISMATCH'],
  ['static credential', { BLOB_READ_WRITE_TOKEN: 'synthetic-test-only' }, 'STATIC_CREDENTIAL_PROHIBITED'],
]) test(name, async t => assertFailure(t, category, () => assert.fail('SDK called'),
  { env: { ...env, ...override } }));

test('null object is rejected', async t => assertFailure(t, 'PRIVATE_OBJECT_NOT_FOUND', async () => null));
test('typed missing object is rejected', async t => assertFailure(t, 'PRIVATE_OBJECT_NOT_FOUND',
  async () => { throw new sdk.BlobNotFoundError(); }));
test('typed access rejection is sanitized', async t => assertFailure(t, 'BLOB_ACCESS_REJECTED',
  async () => { const e = new sdk.BlobAccessError(); e.message = sensitive; throw e; }));
test('structured network error is sanitized', async t => assertFailure(t, 'NETWORK_OR_TLS_FAILURE',
  async () => { throw new Error(sensitive, { cause: { code: 'ENOTFOUND' } }); }));
test('unknown SDK error is sanitized', async t => assertFailure(t, 'UNKNOWN_REDACTED_FAILURE',
  async () => { throw new Error(sensitive); }));
test('missing dependency is sanitized', async t => assertFailure(t, 'SDK_DEPENDENCY_MISSING',
  () => assert.fail('get called'), { loadSdk: async () => { throw new Error(sensitive); } }));
test('non-success response is rejected', async t => assertFailure(t, 'INVALID_RESPONSE',
  async () => ({ statusCode: 304, stream: null })));
test('timeout bounds even a non-cooperating SDK promise', async t => assertFailure(t, 'DOWNLOAD_TIMEOUT',
  () => new Promise(() => {}), { timeoutMs: 15 }));
test('interrupted stream removes partial file', async t => assertFailure(t, 'DOWNLOAD_STREAM_INTERRUPTED',
  async () => ({ statusCode: 200, blob: { size: 20 }, stream: new ReadableStream({
    pull(c) { c.error(new Error(sensitive)); },
  }) })));
test('gracefully truncated transfer removes partial file', async t => assertFailure(t, 'DOWNLOAD_STREAM_INTERRUPTED',
  async () => ({ ...response(), blob: { size: 200 } })));
test('stalled stream times out and removes partial file', async t => assertFailure(t, 'DOWNLOAD_TIMEOUT',
  async () => ({ statusCode: 200, blob: { size: 20 }, stream: new ReadableStream({}) }),
  { timeoutMs: 15 }));
test('invalid destination and pathname are rejected without retrieving', async t => {
  const input = await fixture(t);
  for (const change of [{ destination: join(input.root, 'other') },
    { destination: 'runtime.tar.gz' }, { pathname: 'unrelated/object' }]) {
    assert.deepEqual(await retrieve({ ...input, ...change }, options(() => assert.fail('network'))),
      { ok: false, category: 'INVALID_ARGUMENT' });
  }
  assert.deepEqual(await readdir(input.root), []);
});
test('existing archive is never overwritten; owned partial is cleaned', async t => {
  const input = await fixture(t); await writeFile(input.destination, 'preserve');
  assert.deepEqual(await retrieve(input, options(async () => response())),
    { ok: false, category: 'OUTPUT_FILESYSTEM_FAILURE' });
  assert.equal(await readFile(input.destination, 'utf8'), 'preserve');
  assert.deepEqual(await readdir(input.root), ['runtime.tar.gz']);
});
test('existing partial is preserved and SDK is not called', async t => {
  const input = await fixture(t); await mkdir(`${input.destination}.part`);
  assert.deepEqual(await retrieve(input, options(() => assert.fail('network'))),
    { ok: false, category: 'OUTPUT_FILESYSTEM_FAILURE' });
  assert.deepEqual(await readdir(input.root), ['runtime.tar.gz.part']);
});
test('real child helper resolves colocated SDK without account login or credential files', async t => {
  const input = await fixture(t);
  const helper = join(input.root, 'retrieve.mjs');
  await copyFile(fileURLToPath(new URL('./retrieve.mjs', import.meta.url)), helper);
  const packageRoot = join(input.root, 'node_modules/@vercel/blob');
  await mkdir(packageRoot, { recursive: true });
  await writeFile(join(packageRoot, 'package.json'), JSON.stringify({ type: 'module', exports: './index.mjs' }));
  await writeFile(join(packageRoot, 'index.mjs'), `export async function get(name, opts) {
    if (name !== ${JSON.stringify(pathname)} || opts.storeId !== ${JSON.stringify(storeId)} ||
        opts.access !== 'private' || opts.oidcToken !== 'synthetic-test-only' || 'token' in opts)
      throw new Error('fixture contract failure');
    if (process.env.FIXTURE_FAILURE) throw new Error(${JSON.stringify(sensitive)});
    return {statusCode:200, blob:{size:7}, stream:new ReadableStream({start(c){
      c.enqueue(new TextEncoder().encode('fixture'));c.close();}})};
  }`);
  const childEnv = { ...env, HOME: input.root, CI: '1' };
  for (const failure of [false, true]) {
    if (failure) await rm(input.destination);
    const result = spawnSync(process.execPath, [helper, input.destination, pathname, storeId], {
      cwd: input.root, env: { ...childEnv, ...(failure ? { FIXTURE_FAILURE: '1' } : {}) }, encoding: 'utf8',
    });
    assert.equal(result.status, failure ? 1 : 0);
    assert.equal(result.stdout, '');
    assert.equal(result.stderr, failure ? 'NEUROFLY_BLOB_FAILURE UNKNOWN_REDACTED_FAILURE\n' : '');
    assert(!result.stderr.includes(sensitive));
    if (!failure) assert.equal(await readFile(input.destination, 'utf8'), 'fixture');
    assert(!(await readdir(input.root)).some(name => name === '.env.local' || name === 'auth.json'));
  }
});
test('protocol is a finite unique allowlist', () => assert.equal(new Set(categories).size, categories.length));
