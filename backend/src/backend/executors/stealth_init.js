// Patches the most common fingerprint tells that give headless Chromium
// away to bot detection (navigator.webdriver, empty plugins list, missing
// window.chrome.runtime, WebGL renderer strings that reveal SwiftShader).
// Runs in every page before the site's own scripts, via
// @playwright/mcp's --init-script flag. Not a guaranteed bypass - advanced
// detection (TLS fingerprinting, behavioral analysis) is out of scope here,
// but this covers the JS-detectable checks that are the most common first
// line of defense.

Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined,
});

Object.defineProperty(navigator, 'plugins', {
  get: () => [1, 2, 3, 4, 5].map(() => ({ name: 'Chrome PDF Plugin' })),
});

Object.defineProperty(navigator, 'languages', {
  get: () => ['en-US', 'en'],
});

if (!window.chrome) {
  window.chrome = {};
}
if (!window.chrome.runtime) {
  window.chrome.runtime = {};
}

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
  parameters.name === 'notifications'
    ? Promise.resolve({ state: Notification.permission })
    : originalQuery(parameters);

const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function (parameter) {
  // UNMASKED_VENDOR_WEBGL
  if (parameter === 37445) {
    return 'Intel Inc.';
  }
  // UNMASKED_RENDERER_WEBGL
  if (parameter === 37446) {
    return 'Intel Iris OpenGL Engine';
  }
  return getParameter.apply(this, [parameter]);
};
