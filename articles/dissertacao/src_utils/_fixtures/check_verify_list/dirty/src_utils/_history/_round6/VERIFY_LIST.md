# VERIFY_LIST fixture — DIRTY

The block below carries an `EXPECT` annotation that its command does not satisfy. The checker must
exit nonzero and name this file.

```bash
printf 'measured 7\n'
# EXPECT: contains=measured 9
```
