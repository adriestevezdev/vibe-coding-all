import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header/Navigation */}
      <header className="flex justify-between items-center p-4 md:px-8">
        <div className="font-bold text-xl">Project Blueprint</div>
        <nav className="hidden md:flex space-x-6">
          <a href="#" className="hover:text-primary">Home</a>
          <a href="#" className="hover:text-primary">Features</a>
          <a href="#" className="hover:text-primary">Pricing</a>
          <a href="#" className="hover:text-primary">Contact</a>
        </nav>
        <a 
          href="/login" 
          className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-hover transition-colors"
        >
          Get Started
        </a>
      </header>

      {/* Hero Section */}
      <section className="bg-gray-custom py-16 md:py-24 px-4 md:px-8 flex-grow">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-3xl md:text-5xl font-bold mb-6">Transform Your Project Ideas into Structured Documentation</h1>
          <p className="text-lg md:text-xl mb-8 max-w-3xl mx-auto text-gray-custom">
            Project Blueprint uses AI to convert your project concepts into comprehensive, well-organized documentation, saving you time and effort.
          </p>
          <a 
            href="/login" 
            className="bg-primary text-white px-6 py-3 rounded-md hover:bg-primary-hover transition-colors text-lg font-medium"
          >
            Get Started
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 md:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold mb-12 text-center">Key Features</h2>
          <p className="text-center mb-12 text-gray-custom">
            Project Blueprint offers a range of features designed to streamline your documentation process and enhance project clarity.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-6 rounded-lg">
              <div className="mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Automated Documentation</h3>
              <p className="text-gray-custom">Generate tailored project documentation automatically from your initial ideas.</p>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-lg">
              <div className="mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Powered Insights</h3>
              <p className="text-gray-custom">Receive in-depth suggestions and insights to improve your project planning and execution.</p>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-lg">
              <div className="mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Time-Saving Efficiency</h3>
              <p className="text-gray-custom">Reduce the time spent on documentation so you can focus on project development.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-custom py-16 px-4 md:px-8 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold mb-6">Ready to Simplify Your Project Documentation?</h2>
          <p className="mb-8 text-gray-custom">
            Start using Project Blueprint today and experience the power of AI-driven project planning.
          </p>
          <a 
            href="/login" 
            className="bg-white text-primary px-6 py-3 rounded-md hover:bg-gray-100 transition-colors text-lg font-medium"
          >
            Sign Up Now
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 md:px-8 text-center text-sm text-gray-500">
        <div className="max-w-6xl mx-auto flex justify-center space-x-8 mb-4">
          <a href="#" className="hover:text-gray-700">Terms of Service</a>
          <a href="#" className="hover:text-gray-700">Privacy Policy</a>
          <a href="#" className="hover:text-gray-700">Contact Us</a>
        </div>
        <p>© 2023 Project Blueprint. All rights reserved.</p>
      </footer>
    </div>
  );
}
