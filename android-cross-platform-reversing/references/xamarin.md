# Xamarin

## Signals

- `assemblies/`
- `.dll` assemblies
- `libmonodroid.so`

## Approach

Inspect managed assemblies when present. JADX usually shows Android glue, not
full application logic. Native analysis may still be needed for `libmonodroid`
or bundled native libraries.
