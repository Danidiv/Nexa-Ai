import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const FeatureCard = ({ title, description, icon: Icon }) => {
  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
      <div className="flex items-center justify-center h-12 mb-4">
        <Icon className="text-blue-500" />
      </div>
      <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
    </div>
  );
};

export default FeatureCard;