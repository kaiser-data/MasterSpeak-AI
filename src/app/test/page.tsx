export default function TestPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">🚀 Deployment Test v2.7</h1>
      <p>If you can see this page, the deployment is working!</p>
      <p className="mt-4">
        <strong>Commit:</strong> 5f17fa58 (should match Vercel build logs)
      </p>
      <div className="mt-4 p-4 bg-green-100 rounded">
        <p><strong>Next steps:</strong></p>
        <ol className="list-decimal list-inside mt-2">
          <li>Go to <a href="/" className="text-blue-600 underline">main site</a></li>
          <li>Check for v2.7 red banner</li>
          <li>Test analysis with title field</li>
        </ol>
      </div>
    </div>
  )
}