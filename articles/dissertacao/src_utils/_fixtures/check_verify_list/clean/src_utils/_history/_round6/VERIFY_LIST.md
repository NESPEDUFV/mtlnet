# VERIFY_LIST fixture — CLEAN

One satisfied assertion, one mutating block that must be REFUSED rather than run, and one
recursion block that must be SKIPPED rather than run. The checker must exit 0.

A build block is deliberately NOT in this fixture: the build guard also checks that the block's own
`cd` resolves, and it reports CD-FAIL (rc=1, correctly) for any tree that is not the real
dissertation checkout. That path is exercised in the DIRTY direction of the real document instead.

```bash
printf 'measured 7\n'
# EXPECT: contains=measured 7
```

```bash
git -C /tmp/nowhere push origin main
```

```bash
cd src && bash ../src_utils/check.sh
```
