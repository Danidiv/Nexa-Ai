import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'

export default function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-background p-8">
      <Card className="max-w-sm">
        <CardHeader>
          <CardTitle>AZIZ AI + shadcn/ui + TypeScript</CardTitle>
          <CardDescription>Real components, real TypeScript, real Tailwind build.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            This proves the whole toolchain works before any AI generation is layered on top.
          </p>
        </CardContent>
        <CardFooter>
          <Button onClick={() => setCount(count + 1)}>Clicked {count} times</Button>
        </CardFooter>
      </Card>
    </div>
  )
}
