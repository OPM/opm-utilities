**opm-ci-builder tests**
This contains a test suite for a opm ci builder docker image

*Run like jenkins, just locally*
Run a opm-common PR builder with opm-common=123 and opm-simulators=456

```console
TRIGGER="opm-common=123 opm-simulators=456" ctest -R pull.opm-common
```
