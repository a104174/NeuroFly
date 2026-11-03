export async function load(url, context, nextLoad) {
  if (url.endsWith(".css")) {
    return {
      format: "module",
      shortCircuit: true,
      source: "export default new Proxy({}, { get: (_, key) => (typeof key === 'string' ? key : undefined) });",
    };
  }
  return nextLoad(url, context);
}
