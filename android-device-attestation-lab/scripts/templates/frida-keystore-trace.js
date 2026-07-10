'use strict';

const SOURCE = 'frida.android.keystore.trace';
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

Java.perform(function () {
  emit('probe.start', { target: 'java.security.KeyStore' });

  Java.use('java.security.KeyStore');
  emit('class.available', { name: 'java.security.KeyStore' });

  Java.choose('java.security.KeyStore', {
    onMatch(instance) {
      emit('keystore.instance', { type: String(instance.getType()) });
    },
    onComplete() {
      emit('keystore.choose.complete', {});
    }
  });
});
