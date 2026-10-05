import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HeroSection({ headline, subheadline, ctaText, ctaUrl }) {
  return (
    <Card className="w-full max-w-7xl mx-auto px-4 py-12 md:py-20">
      <div className="text-center space-y-6">
        <h1 className="text-3xl md:text-5xl font-bold text-gray-900">{headline}</h1>
        <p className="text-xl md:text-2xl text-gray-600">{subheadline}</p>
        <Button variant="default" size="lg" asChild>
          <a href={ctaUrl} className="hover:bg-gray-900 hover:text-white transition-colors">
            {ctaText}
          </a>
        </Button>
      </div>
    </Card>
  );
}