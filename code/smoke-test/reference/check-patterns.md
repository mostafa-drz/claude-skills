# Check Patterns Reference

Heuristics for building trace plans. Adapt to the project.

## API-based projects
- Find relevant endpoints from CLAUDE.md, route files, or OpenAPI specs
- Use `curl` or `httpx` to call endpoints
- Check both the resource and downstream resources

## Event-driven systems
- Trace the event chain: trigger → handler → output
- Check each stage: published? received? output produced?

## Database-backed systems
- Query relevant tables/collections
- Check records exist with expected values
- Verify relationships between records

## Frontend features
- Check API endpoints the frontend calls
- Verify data shape matches frontend expectations

## General patterns (apply everywhere)
1. **Resource exists** — Does it exist where it should?
2. **Resource is correct** — Right fields/values?
3. **Downstream effects** — Did side effects happen?
4. **No errors** — Any error states or failed statuses?
5. **Consistency** — Do related resources agree?
