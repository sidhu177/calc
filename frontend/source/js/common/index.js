// entrypoint for common bundle
// this is where modules should be `require(...)`'d

require("babel-polyfill/dist/polyfill");

require("./dap-hacks");
require("./usermenu");
