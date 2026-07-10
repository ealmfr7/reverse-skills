'use strict';

const SOURCE = 'frida.android.keymaster.trace';
const MAX_EVENTS = 200;
let eventCount = 0;

function emit(event, data) {
  if (eventCount >= MAX_EVENTS) {
    return;
  }
  eventCount += 1;
  send(JSON.stringify({
    schema: 1,
    type: 'event',
    event: event,
    ts: Date.now() / 1000,
    source: SOURCE,
    data: data || {}
  }));
}

function traceExport(moduleName, exportName, label) {
  const address = Module.findExportByName(moduleName, exportName);
  if (!address) {
    emit('native.export.missing', { module: moduleName, export: exportName, label: label });
    return;
  }
  Interceptor.attach(address, {
    onEnter(args) {
      emit('native.call.enter', { module: moduleName, export: exportName, label: label });
    },
    onLeave(retval) {
      emit('native.call.leave', { module: moduleName, export: exportName, label: label, retval: String(retval) });
    }
  });
}

emit('probe.start', { target: 'keymaster/keymint modules' });

[
  ['libkeymaster4.so', 'HIDL_FETCH_IKeymasterDevice', 'keymaster4.fetch'],
  ['android.hardware.security.keymint-V1-ndk.so', 'AServiceManager_getService', 'keymint.service']
].forEach(function (item) {
  traceExport(item[0], item[1], item[2]);
});
