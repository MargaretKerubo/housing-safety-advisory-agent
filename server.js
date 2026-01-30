const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Import the housing agent functionality from the modular codebase
// Note: Since our housing agent is in Python, we'll need to call it differently
// This is a placeholder for the actual implementation

// Serve static files from the React app build directory
app.use(express.static(path.join(__dirname, 'frontend/build')));

// API Routes
app.post('/api/housing-recommendations', async (req, res) => {
  try {
    const {
      location,
      destination,
      distance,
      time,
      budget,
      safety,
      arrangement,
      query
    } = req.body;

    // Format the user input for the housing agent
    const userInput = `
      I'm looking for housing in ${location}.
      My workplace is in ${destination}.
      The commute distance is ${distance}km.
      I plan to return at ${time}.
      My budget is ${budget} KES per month.
      I prefer ${safety} safety tolerance.
      I will be living ${arrangement}.
      Additional concerns: ${query}
    `;

    // Placeholder response - in a real implementation, this would call the Python backend
    const mockResult = {
      status: "success",
      requirements: {
        has_all_details: true,
        current_location: "",
        target_location: location,
        workplace_location: destination,
        monthly_budget: budget,
        preferences: `Safety: ${safety}, Arrangement: ${arrangement}, Time: ${time}, Distance: ${distance}km`
      },
      recommendations: {
        neighborhoods: [
          {
            name: "Sample Neighborhood 1",
            distance_to_cbd: `${distance} km`,
            average_rent_1br: `${Math.floor(budget * 0.6)} - ${Math.floor(budget * 0.8)}`,
            average_rent_2br: `${Math.floor(budget * 0.8)} - ${budget}`,
            security_rating: "4/5 stars",
            security_details: "This area has good security with active neighborhood watch, adequate lighting, and proximity to police station.",
            amenities: ["Market", "School", "Hospital", "Bank"],
            transportation: `Located ${distance}km from ${destination} with regular matatu service and boda boda access.`,
            description: "A popular residential area with good infrastructure and security.",
            pros: ["Good security", "Near amenities", "Well connected"],
            cons: ["Can be crowded", "Limited parking"]
          },
          {
            name: "Sample Neighborhood 2",
            distance_to_cbd: `${distance + 2} km`,
            average_rent_1br: `${Math.floor(budget * 0.5)} - ${Math.floor(budget * 0.7)}`,
            average_rent_2br: `${Math.floor(budget * 0.7)} - ${Math.floor(budget * 0.9)}`,
            security_rating: "3/5 stars",
            security_details: "Moderate security with some neighborhood watch groups and decent lighting.",
            amenities: ["Local market", "Primary school", "Pharmacy"],
            transportation: `About ${distance + 2}km from ${destination} with reasonable transport connections.`,
            description: "A developing area with lower rents but growing amenities.",
            pros: ["Affordable", "Developing", "Less crowded"],
            cons: ["Transport links could be better", "Fewer amenities"]
          }
        ]
      },
      message: `Thank you for your inquiry about housing in ${location}. Based on your criteria of a ${budget} KES budget and ${safety} safety tolerance, I've identified several suitable neighborhoods. The first option is a well-established area with good security and amenities. The second is a developing area that offers more affordable options. Both are within reasonable distance of your workplace in ${destination}.`
    };

    res.json(mockResult);
  } catch (error) {
    console.error('Error generating housing recommendations:', error);
    res.status(500).json({ 
      error: 'Failed to generate housing recommendations',
      message: error.message 
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Catch-all handler for frontend routes (for React Router)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});