const { useState } = React;

function SustainableSearchEngine() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError(null);
    setSearchResults([]);

    try {
      const response = await fetch('/api/retrieve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `API request failed (${response.status})`);
      }

      const formattedResults = data.websites.map(rawUrl => ({
        url: rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`,
        title: new URL(rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`).hostname.replace(/^www\./, ''),
      }));

      setSearchResults(formattedResults);
    } catch (err) {
      console.error("Search error:", err);
      setError(err.message);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#DCDCC8' }}>
      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4" style={{ color: '#506038' }}>
            EcoSearch
          </h1>
          <p className="text-lg text-gray-700">
            Discover sustainable fashion brands
          </p>
        </header>

        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-12">
          <div className="flex shadow-lg rounded-lg overflow-hidden">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for eco-friendly brands..."
              className="flex-grow p-4 focus:outline-none"
            />
            <button
              type="submit"
              disabled={isSearching}
              className="bg-green-700 text-white px-6 hover:bg-green-800 transition"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="max-w-2xl mx-auto bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-8">
            <div className="flex items-center">
              <span className="mr-2">⚠️</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        <div className="max-w-4xl mx-auto">
          {searchResults.length > 0 ? (
            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <a
                  key={index}
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition border-l-4 border-green-500"
                >
                  <h3 className="text-xl font-semibold mb-2">{result.title}</h3>
                  <p className="text-gray-600 text-sm">{result.url}</p>
                </a>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <span className="text-3xl block mb-4">💨</span>
              <p>Enter a search term to find sustainable brands</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(<SustainableSearchEngine />);
