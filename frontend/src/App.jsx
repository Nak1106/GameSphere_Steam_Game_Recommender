import React, { useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_BASE = 'http://localhost:8000';

function RecommendationsTab() {
  const [authorIndex, setAuthorIndex] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');
    setResults([]);
    try {
      const res = await axios.get(`${API_BASE}/recommendations/${authorIndex}`);
      setResults(res.data.recommendations);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Game Recommendations</h2>
      <input
        type="number"
        placeholder="Enter your Steam author_index"
        value={authorIndex}
        onChange={e => setAuthorIndex(e.target.value)}
        style={{ marginRight: 8 }}
      />
      <button onClick={fetchRecommendations} disabled={!authorIndex || loading}>
        {loading ? 'Loading...' : 'Get Recommendations'}
      </button>
      {error && <div style={{ color: 'red', marginTop: 12 }}>{error}</div>}
      {results.length > 0 && (
        <table border="1" cellPadding="6" style={{ marginTop: 24, width: '100%' }}>
          <thead>
            <tr>
              <th>Game Name</th>
              <th>Predicted Rating</th>
              <th>Avg Sentiment Score</th>
              <th>% Positive</th>
              <th>% Negative</th>
            </tr>
          </thead>
          <tbody>
            {results.map((row, idx) => (
              <tr key={idx}>
                <td>{row.app_name}</td>
                <td>{row.predicted_rating?.toFixed(2)}</td>
                <td>{row.avg_sentiment_score ? row.avg_sentiment_score.toFixed(2) : '-'}</td>
                <td>{row.percent_positive ? row.percent_positive.toFixed(1) : '-'}</td>
                <td>{row.percent_negative ? row.percent_negative.toFixed(1) : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function LeaderboardTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${API_BASE}/sentiment-leaderboard`);
      setData(res.data.leaderboard);
    } catch (err) {
      setError('Error fetching leaderboard');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchLeaderboard();
    // eslint-disable-next-line
  }, []);

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (error) return <div style={{ color: 'red', padding: 24 }}>{error}</div>;
  if (!data) return null;

  const chartData = {
    labels: data.map(row => row.app_name),
    datasets: [
      {
        label: '% Positive',
        data: data.map(row => row.percent_positive),
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Top 20 Games by % Positive Sentiment',
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        title: { display: true, text: '% Positive' },
      },
    },
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Sentiment Leaderboard</h2>
      <Bar data={chartData} options={options} />
    </div>
  );
}

function App() {
  const [tab, setTab] = useState(0);
  return (
    <div>
      <header style={{ padding: 16, borderBottom: '1px solid #eee', marginBottom: 16 }}>
        <button onClick={() => setTab(0)} style={{ marginRight: 16, fontWeight: tab === 0 ? 'bold' : 'normal' }}>
          Game Recommendations
        </button>
        <button onClick={() => setTab(1)} style={{ fontWeight: tab === 1 ? 'bold' : 'normal' }}>
          Sentiment Leaderboard
        </button>
      </header>
      {tab === 0 ? <RecommendationsTab /> : <LeaderboardTab />}
    </div>
  );
}

export default App;
