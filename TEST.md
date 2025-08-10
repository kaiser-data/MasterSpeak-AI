# API Endpoint Tests

## JSON request

```
curl -i -X POST https://masterspeak-ai-production.up.railway.app/api/v1/analysis/text \
  -H "Origin: https://master-speak-ai.vercel.app" \
  -H "Content-Type: application/json" \
  --data '{"text":"This is a speech.","user_id":"123","prompt_type":"default"}'
```

Expect: **200** JSON, `X-Request-ID` present.

## multipart/form-data request

```
curl -i -X POST https://masterspeak-ai-production.up.railway.app/api/v1/analysis/text \
  -H "Origin: https://master-speak-ai.vercel.app" \
  -F "text=This is a speech." \
  -F "user_id=123" \
  -F "prompt_type=default"
```

Expect: **200** JSON, `X-Request-ID` present.

## bad body → 422 (not 500)

```
curl -i -X POST https://masterspeak-ai-production.up.railway.app/api/v1/analysis/text \
  -H "Origin: https://master-speak-ai.vercel.app" \
  -H "Content-Type: application/json" \
  --data '{"txt":"missing required field"}'
```

Expect: **422** JSON with `detail` and `request_id`.

## Frontend note

Prefer JSON for text-only analysis:

```ts
await fetch('/api/v1/analysis/text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ text, user_id, prompt_type: 'default' })
});
```