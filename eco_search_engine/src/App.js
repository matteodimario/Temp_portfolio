import { useState } from 'react';
import { Search, Leaf, Recycle, Globe, Award, AlertCircle, Info } from 'lucide-react';

export default function SustainableSearchEngine() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showInfoPanel, setShowInfoPanel] = useState(false);

  // Custom color scheme
  const colors = {
    sepia: "#DCDCC8",
    darkGreen: "#506038",
    lightBlue: "#CFD9EA",
    darkText: "#333333",
    lightText: "#FFFFFF",
    success: "#4B7F52"  // A slightly different green for success indicators
  };

  // Sample data for demonstration purposes
  const exampleResults = [
    {
      id: 1,
      title: "Organic Cotton T-Shirt",
      brand: "EcoThreads",
      image: "/api/placeholder/120/160",
      price: "$34.99",
      sustainability: {
        ethicalLabor: 95,
        recyclability: 90,
        carbonFootprint: 85
      },
      certifications: ["GOTS Certified", "Fair Trade"]
    },
    {
      id: 2,
      title: "Recycled Denim Jeans",
      brand: "GreenStitch",
      image: "/api/placeholder/120/160",
      price: "$79.99",
      sustainability: {
        ethicalLabor: 90,
        recyclability: 95,
        carbonFootprint: 80
      },
      certifications: ["Recycled Materials", "B Corp"]
    },
    {
      id: 3,
      title: "Hemp Blend Sweater",
      brand: "NatureFiber",
      image: "/api/placeholder/120/160",
      price: "$64.50",
      sustainability: {
        ethicalLabor: 85,
        recyclability: 80,
        carbonFootprint: 90
      },
      certifications: ["Carbon Neutral", "Local Production"]
    }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    
    // Simulate API call
    setTimeout(() => {
      setSearchResults(exampleResults);
      setIsSearching(false);
    }, 1000);
  };

  const SustainabilityMeter = ({ value, label, icon }) => {
    const Icon = icon;
    const getColor = (val) => {
      if (val >= 90) return colors.success;
      if (val >= 80) return '#68945D';
      if (val >= 70) return '#D6A85C';
      return '#C27D38';
    };

    return (
      <div className="flex flex-col items-center">
        <div className="flex items-center mb-1">
          <Icon size={16} className="mr-1" style={{ color: colors.darkGreen }} />
          <span className="text-xs" style={{ color: colors.darkText }}>{label}</span>
        </div>
        <div className="w-full rounded-full h-2" style={{ backgroundColor: colors.sepia }}>
          <div 
            className="h-2 rounded-full" 
            style={{ width: `${value}%`, backgroundColor: getColor(value) }}
          ></div>
        </div>
        <span className="text-xs mt-1 font-medium" style={{ color: colors.darkText }}>{value}/100</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.sepia }}>
      {/* Header */}
      <header style={{ backgroundColor: colors.darkGreen }}>
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold flex items-center" style={{ color: colors.lightText }}>
              <Leaf className="mr-2" />
              EcoSearch
            </h1>
            <button 
              onClick={() => setShowInfoPanel(!showInfoPanel)}
              className="flex items-center text-sm px-3 py-1 rounded-full"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)', color: colors.lightText }}
            >
              <Info size={16} className="mr-1" />
              About
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-8 pb-16" style={{ 
        background: `linear-gradient(to bottom, ${colors.darkGreen}, ${colors.darkGreen}CC)`,
        color: colors.lightText
      }}>
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Find Truly Sustainable Fashion</h2>
          <p className="text-lg mb-8 max-w-2xl mx-auto">
            Cutting through greenwashing with AI-powered search that verifies eco-friendly claims
          </p>
          
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for sustainable clothing (e.g., 'organic cotton t-shirt')"
              className="w-full py-4 px-6 pr-12 rounded-full text-lg shadow-lg focus:outline-none focus:ring-2"
              style={{ 
                backgroundColor: colors.lightText, 
                color: colors.darkText,
                borderColor: colors.lightBlue 
              }}
            />
            <button
              type="submit"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-full"
              style={{ backgroundColor: colors.darkGreen }}
            >
              <Search size={24} style={{ color: colors.lightText }} />
            </button>
          </form>
        </div>
      </section>

      {/* Info Panel */}
      {showInfoPanel && (
        <div className="shadow-md p-6 max-w-3xl mx-auto -mt-6 rounded-lg mb-8" style={{ backgroundColor: colors.lightBlue }}>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-xl font-bold" style={{ color: colors.darkGreen }}>About EcoSearch</h3>
            <button 
              onClick={() => setShowInfoPanel(false)}
              style={{ color: colors.darkGreen }}
            >
              <AlertCircle size={20} />
            </button>
          </div>
          
          <p className="mb-4" style={{ color: colors.darkText }}>
            EcoSearch is an AI-powered search engine designed to help consumers find genuinely sustainable clothing. 
            We prioritize verified eco-friendly attributes and filter out misleading claims through advanced ML techniques.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="flex flex-col items-center text-center p-3">
              <Award style={{ color: colors.darkGreen }} className="mb-2" size={32} />
              <h4 className="font-semibold mb-1" style={{ color: colors.darkGreen }}>Verified Certifications</h4>
              <p className="text-sm" style={{ color: colors.darkText }}>We prioritize products with credible sustainability certifications</p>
            </div>
            <div className="flex flex-col items-center text-center p-3">
              <AlertCircle style={{ color: colors.darkGreen }} className="mb-2" size={32} />
              <h4 className="font-semibold mb-1" style={{ color: colors.darkGreen }}>Greenwashing Detection</h4>
              <p className="text-sm" style={{ color: colors.darkText }}>Our AI identifies and filters misleading environmental claims</p>
            </div>
            <div className="flex flex-col items-center text-center p-3">
              <Globe style={{ color: colors.darkGreen }} className="mb-2" size={32} />
              <h4 className="font-semibold mb-1" style={{ color: colors.darkGreen }}>Comprehensive Impact</h4>
              <p className="text-sm" style={{ color: colors.darkText }}>We evaluate ethical labor, recyclability, and carbon footprint</p>
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {isSearching ? (
        <div className="container mx-auto px-4 py-8 text-center">
          <div className="animate-pulse flex flex-col items-center">
            <div className="rounded-full h-12 w-12 mb-4" style={{ backgroundColor: colors.lightBlue }}></div>
            <div className="h-4 rounded w-24 mb-2" style={{ backgroundColor: colors.lightBlue }}></div>
            <div className="h-3 rounded w-16" style={{ backgroundColor: colors.lightBlue }}></div>
          </div>
        </div>
      ) : searchResults.length > 0 ? (
        <div className="container mx-auto px-4 py-8">
          <h3 className="text-xl font-semibold mb-6" style={{ color: colors.darkGreen }}>
            Sustainable Options ({searchResults.length})
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.map(item => (
              <div key={item.id} className="rounded-lg shadow-md overflow-hidden" style={{ backgroundColor: colors.lightText }}>
                <div className="p-4">
                  <div className="flex mb-4">
                    <div className="w-1/3">
                      <img
                        src={item.image}
                        alt={item.title}
                        className="w-full h-40 object-cover rounded"
                      />
                    </div>
                    <div className="w-2/3 pl-4">
                      <h4 className="font-bold text-lg mb-1" style={{ color: colors.darkText }}>{item.title}</h4>
                      <p className="text-sm mb-2" style={{ color: colors.darkText }}>by {item.brand}</p>
                      <p className="font-semibold mb-2" style={{ color: colors.darkGreen }}>{item.price}</p>
                      <div className="flex flex-wrap gap-1 mt-auto">
                        {item.certifications.map((cert, i) => (
                          <span 
                            key={i} 
                            className="text-xs px-2 py-1 rounded"
                            style={{ backgroundColor: `${colors.darkGreen}22`, color: colors.darkGreen }}
                          >
                            {cert}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="border-t pt-3" style={{ borderColor: colors.sepia }}>
                    <h5 className="text-sm font-semibold mb-2" style={{ color: colors.darkGreen }}>Sustainability Metrics</h5>
                    <div className="grid grid-cols-3 gap-2">
                      <SustainabilityMeter 
                        value={item.sustainability.ethicalLabor} 
                        label="Ethical Labor" 
                        icon={Award} 
                      />
                      <SustainabilityMeter 
                        value={item.sustainability.recyclability} 
                        label="Recyclability" 
                        icon={Recycle} 
                      />
                      <SustainabilityMeter 
                        value={item.sustainability.carbonFootprint} 
                        label="Carbon Score" 
                        icon={Globe} 
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Features Section */}
      {!searchResults.length && !isSearching && (
        <section className="container mx-auto px-4 py-12">
          <h2 className="text-2xl font-bold text-center mb-10" style={{ color: colors.darkGreen }}>How Our AI Makes a Difference</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-lg shadow-md" style={{ backgroundColor: colors.lightText }}>
              <div className="p-3 rounded-full inline-block mb-4" style={{ backgroundColor: `${colors.lightBlue}99` }}>
                <Award style={{ color: colors.darkGreen }} size={24} />
              </div>
              <h3 className="text-xl font-semibold mb-2" style={{ color: colors.darkGreen }}>Verified Claims</h3>
              <p style={{ color: colors.darkText }}>
                We analyze product descriptions against trusted certification databases to verify sustainability claims.
              </p>
            </div>
            
            <div className="p-6 rounded-lg shadow-md" style={{ backgroundColor: colors.lightText }}>
              <div className="p-3 rounded-full inline-block mb-4" style={{ backgroundColor: `${colors.lightBlue}99` }}>
                <Search style={{ color: colors.darkGreen }} size={24} />
              </div>
              <h3 className="text-xl font-semibold mb-2" style={{ color: colors.darkGreen }}>Semantic Analysis</h3>
              <p style={{ color: colors.darkText }}>
                Our BERT-powered AI looks beyond keywords to understand context and detect greenwashing.
              </p>
            </div>
            
            <div className="p-6 rounded-lg shadow-md" style={{ backgroundColor: colors.lightText }}>
              <div className="p-3 rounded-full inline-block mb-4" style={{ backgroundColor: `${colors.lightBlue}99` }}>
                <Recycle style={{ color: colors.darkGreen }} size={24} />
              </div>
              <h3 className="text-xl font-semibold mb-2" style={{ color: colors.darkGreen }}>Transparency Ranking</h3>
              <p style={{ color: colors.darkText }}>
                We prioritize brands that provide clear, verifiable information about their environmental impact.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer style={{ backgroundColor: colors.darkGreen, color: colors.lightText }} className="py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h2 className="text-xl font-bold flex items-center">
                <Leaf className="mr-2" />
                EcoSearch
              </h2>
              <p className="text-sm mt-1" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>AI-powered sustainable fashion discovery</p>
            </div>
            
            <div className="flex space-x-6">
              <a href="#" style={{ color: colors.lightText }} className="hover:opacity-80">About</a>
              <a href="#" style={{ color: colors.lightText }} className="hover:opacity-80">How It Works</a>
              <a href="#" style={{ color: colors.lightText }} className="hover:opacity-80">Contact</a>
              <a href="#" style={{ color: colors.lightText }} className="hover:opacity-80">Privacy Policy</a>
            </div>
          </div>
          
          <div className="border-t mt-6 pt-6 text-center text-sm" style={{ borderColor: 'rgba(255, 255, 255, 0.2)', color: 'rgba(255, 255, 255, 0.7)' }}>
            &copy; {new Date().getFullYear()} EcoSearch. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}