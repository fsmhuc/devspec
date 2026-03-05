# Example Patch

This is an example patch file.

---

## Problem

IPv6 address parsing fails with colon-separated format.

- What is broken? IPv6 addresses with double colon (::) notation
- Expected: Should parse "2001:db8::1" correctly
- Actual: Returns null/error

---

## Fix

- Root cause: Regex pattern only matched full 8-segment format
- Solution: Add support for compressed :: notation
- Code changes:
  - `src/utils/ip-parser.ts` - Updated regex pattern

---

## Impact

- `src/utils/ip-parser.ts`
- `src/validators/network.ts`

---

## Testing

- [x] Unit test added: `tests/ip-parser.test.ts`
- [x] Manual testing performed
- [ ] No test needed

---

## Checklist

- [x] Fix is minimal and focused
- [x] No spec changes required
- [x] No breaking changes
- [x] Reviewed by: @developer
