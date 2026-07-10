# Cordova and Capacitor

## Signals

- `assets/www/`
- `cordova.js`
- `capacitor.config.*`

## Approach

Treat `assets/www` as a packaged web app. Extract it and analyze JavaScript,
HTML, WebView bridges, API endpoints, and local storage patterns. Use WebView
hooks from `android-frida-hooking` for runtime bridge calls.
