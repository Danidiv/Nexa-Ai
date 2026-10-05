import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <a href="#" className="text-xl font-bold text-indigo-600">aziz.ai</a>
          </div>
          <div className="hidden md:flex space-x-8">
            <a href="#features" className="text-gray-700 hover:text-indigo-600 transition-colors duration-200">Features</a>
            <a href="#how-it-works" className="text-gray-700 hover:text-indigo-600 transition-colors duration-200">How It Works</a>
            <a href="#pricing" className="text-gray-700 hover:text-indigo-600 transition-colors duration-200">Pricing</a>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm" className="hidden md:inline-flex text-gray-700 hover:text-indigo-600 transition-colors duration-200">
              Sign In
            </Button>
            <Button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors duration-200">
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}