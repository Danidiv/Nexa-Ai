import { Card, Button } from '@/components/ui/'
import FeatureCard from './FeatureCard.jsx'

const PricingTable = () => {
  const plans = [
    {
      id: 'basic',
      name: 'Basic',
      price: '$9.99',
      features: [
        '10 AI prompts per month',
        'Basic analytics',
        'No advanced features'
      ],
      cta: 'Get Started',
      isPopular: false
    },
    {
      id: 'pro',
      name: 'Pro',
      price: '$24.99',
      discountPrice: '$19.99',
      features: [
        '50 AI prompts per month',
        'Advanced analytics',
        'Priority support',
        'Collaboration tools'
      ],
      cta: 'Get Started',
      isPopular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '$49.99/month',
      features: [
        'Unlimited AI prompts',
        'Full team collaboration',
        'Priority support & SLA',
        'Custom integrations'
      ],
      cta: 'Contact Sales',
      isPopular: false
    }
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <h2 className="text-3xl font-bold text-center mb-12">Choose Your Plan</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <Card key={plan.id} className="p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-semibold">{plan.name}</h3>
              {plan.isPopular && (
                <Badge variant="outline" className="bg-green-100 text-green-800">
                  Popular
                </Badge>
              )}
            </div>

            <div className="flex items-end justify-between mb-6">
              <span className="text-3xl font-bold">{plan.price}</span>
              {plan.discountPrice && (
                <span className="line-through text-gray-500 ml-2">${plan.discountPrice}</span>
              )}
            </div>

            <ul className="space-y-4 mb-8">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>

            <Button className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 transition-colors">
              {plan.cta}
            </Button>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default PricingTable