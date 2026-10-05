import { Button } from "@/components/ui/button";
import Navbar from "./components/Navbar.jsx";
import HeroSection from "./components/HeroSection.jsx";
import FeatureCard from "./components/FeatureCard.jsx";
import PricingTable from "./components/PricingTable.jsx";
import Testimonial from "./components/Testimonial.jsx";

const App = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <HeroSection />
        <section className="py-16 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "🤖",
                title: "Smart AI Assistant",
                description: "Get instant answers and guidance from our advanced AI assistant."
              },
              {
                icon: "📊",
                title: "Data Analytics",
                description: "Transform raw data into actionable insights with ease."
              },
              {
                icon: "🎨",
                title: "Creative Tools",
                description: "Generate unique content, designs, and creative ideas in seconds."
              }
            ].map((feature, index) => (
              <FeatureCard key={index} {...feature} />
            ))}
          </div>
        </section>

        <section className="py-16 max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: "Sign Up",
                description: "Create your free account in minutes."
              },
              {
                title: "Connect Your Data",
                description: "Link your preferred data sources to start analyzing."
              },
              {
                title: "Start Analyzing",
                description: "Let our AI work its magic and uncover insights."
              }
            ].map((step, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-sm">
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="py-16 max-w-7xl mx-auto">
          <PricingTable />
        </section>

        <section className="py-16 bg-indigo-50 rounded-t-[40px] mb-8">
          <h2 className="text-3xl font-bold text-center mb-12">What our users say</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                quote: "Aziz AI has completely transformed how we analyze customer data. The insights are unmatched!",
                name: "Sarah Johnson",
                company: "TechSolutions Inc."
              },
              {
                quote: "The creative tools alone have saved me countless hours of brainstorming.",
                name: "Michael Chen",
                company: "CreativeWorks Studio"
              },
              {
                quote: "Easy to use and incredibly powerful. Highly recommend for any business looking to innovate.",
                name: "Emily Rodriguez",
                company: "GlobalMarkets"
              }
            ].map((testimonial, index) => (
              <Testimonial key={index} {...testimonial} />
            ))}
          </div>
        </section>

        <section className="py-16 max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="max-w-4xl mx-auto space-y-4">
            {[
              {
                question: "How does Aziz AI work?",
                answer: "Aziz AI uses advanced machine learning algorithms to analyze your data and provide actionable insights."
              },
              {
                question: "Is my data safe with Aziz AI?",
                answer: "We use industry-standard encryption and secure protocols to protect all your data."
              },
              {
                question: "Can I customize the AI features?",
                answer: "Yes, many of our features are highly customizable based on your specific needs."
              }
            ].map((faq, index) => (
              <div key={index} className="border rounded-lg p-6">
                <h3 className="font-semibold mb-2 cursor-pointer" onClick={() => {}}>
                  {faq.question}
                </h3>
                <p className="text-gray-700">{faq.answer}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="py-16 bg-gradient-to-br from-indigo-50 to-purple-100 text-center">
          <h2 className="text-4xl font-bold mb-8">Ready to transform your business?</h2>
          <Button size="lg" className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg rounded-full px-12 py-4">
            Get Started Today
          </Button>
        </section>
      </main>

      <footer className="py-8 bg-gray-900 text-white text-center">
        <p>© 2023 Aziz AI. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;