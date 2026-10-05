import { Card } from '@/components/ui/card';

export default function Testimonial({ quote, name, company }) {
  return (
    <Card className="p-8 max-w-md mx-auto text-center">
      <blockquote className="text-xl md:text-2xl font-medium italic mb-6">
        {quote}
      </blockquote>
      <div className="flex flex-col items-center gap-4">
        <p className="font-semibold">{name}</p>
        <p className="text-gray-500 text-sm">{company}</p>
      </div>
    </Card>
  );
}